import pytest
import pandas as pd
from fastapi.testclient import TestClient
from database.connection import init_db, SessionLocal
from database.models import Province, QuarterlyGDP, Forecast, AIInsights
from etl.pipeline import ETLPipeline
from ml.forecaster import MLForecastingEngine
from ml.scenario import ScenarioAnalysisEngine
from ml.insights import AIInsightsGenerator
from api.main import app


@pytest.fixture(scope="module")
def setup_database():
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_database_seeding_and_models(setup_database):
    db = setup_database
    prov_count = db.query(Province).count()
    assert prov_count >= 5, "Database should contain at least 5 provinces"


def test_etl_pipeline(setup_database):
    db = setup_database
    etl = ETLPipeline(db_session=db)
    
    # Test duplicate detection & cleaning
    raw_df = pd.DataFrame([
        {'year': 2024, 'quarter': 1, 'province_id': 1, 'industry_id': 1, 'gdp_value_m_php': 100.0, 'psic_code': 'A'},
        {'year': 2024, 'quarter': 1, 'province_id': 1, 'industry_id': 1, 'gdp_value_m_php': 100.0, 'psic_code': 'A'},
        {'year': 2024, 'quarter': 2, 'province_id': 1, 'industry_id': 1, 'gdp_value_m_php': None, 'psic_code': 'INVALID'},
    ])

    cleaned = etl.validate_duplicate_lgus(raw_df, ['year', 'quarter', 'province_id', 'industry_id'])
    cleaned = etl.validate_missing_values(cleaned, ['year', 'quarter', 'gdp_value_m_php'])
    cleaned = etl.validate_psic_codes(cleaned, 'psic_code')

    assert len(cleaned) == 2
    assert cleaned.iloc[1]['psic_code'] == 'A'


def test_ml_forecaster(setup_database):
    db = setup_database
    forecaster = MLForecastingEngine(db_session=db)
    count = forecaster.generate_all_forecasts(start_year=2026, end_year=2030)
    assert count > 0, "Forecaster should generate positive number of forecasts"

    forecast_sample = db.query(Forecast).filter(Forecast.year == 2026).first()
    assert forecast_sample is not None
    assert forecast_sample.lower_bound_95 <= forecast_sample.forecast_value <= forecast_sample.upper_bound_95


def test_scenario_analysis(setup_database):
    db = setup_database
    scenario_engine = ScenarioAnalysisEngine(db_session=db)
    res = scenario_engine.simulate_sector_shock(target_year=2026, agri_growth_delta_pct=5.0)

    assert "simulated_regional_gdp_m_php" in res
    assert res["gdp_difference_m_php"] > 0
    assert res["regional_gdp_growth_delta_pct"] > 0


def test_ai_insights_generator(setup_database):
    db = setup_database
    generator = AIInsightsGenerator(db_session=db)
    insights = generator.generate_and_save_insights()
    assert len(insights) > 0

    insight_record = db.query(AIInsights).first()
    assert insight_record is not None
    assert len(insight_record.headline) > 0


def test_api_endpoints():
    client = TestClient(app)

    # 1. Root
    res_root = client.get("/")
    assert res_root.status_code == 200

    # 1b. Web Dashboard Endpoint
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "Region IX" in res_dash.text

    # 2. Provinces
    res_prov = client.get("/api/provinces")
    assert res_prov.status_code == 200
    assert len(res_prov.json()) >= 5

    # 3. Forecasts
    res_fc = client.get("/api/forecasts?metric_type=GDP&year=2026")
    assert res_fc.status_code == 200
    assert len(res_fc.json()) > 0

    # 4. AI Insights
    res_ai = client.get("/api/ai-insights")
    assert res_ai.status_code == 200
    assert len(res_ai.json()) > 0

    # 5. Scenario Simulation POST
    res_sim = client.post("/api/scenario/simulate?target_year=2026&agri_growth_delta_pct=5.0")
    assert res_sim.status_code == 200
    assert res_sim.json()["gdp_difference_m_php"] > 0
