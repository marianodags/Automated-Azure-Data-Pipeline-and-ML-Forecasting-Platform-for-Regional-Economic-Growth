import json
import pandas as pd
from database.connection import SessionLocal
from database.models import Province, Municipality, Industry, QuarterlyGDP, Forecast, AIInsights

def export_powerbi_datasets():
    """Exports SQLite / Azure SQL database tables into JSON/CSV datasets for Power BI import."""
    db = SessionLocal()

    # 1. Export Regional GDP Dataset
    gdp_query = db.query(
        QuarterlyGDP.year,
        QuarterlyGDP.quarter,
        Province.name.label("province_name"),
        Industry.sector.label("sector_name"),
        QuarterlyGDP.gdp_value_m_php,
        QuarterlyGDP.growth_rate_pct
    ).join(Province, QuarterlyGDP.province_id == Province.id)\
     .join(Industry, QuarterlyGDP.industry_id == Industry.id).all()

    df_gdp = pd.DataFrame(gdp_query)
    df_gdp.to_csv("dashboard/powerbi_gdp_dataset.csv", index=False)

    # 2. Export Forecast Dataset
    forecast_query = db.query(
        Forecast.metric_type,
        Forecast.year,
        Province.name.label("province_name"),
        Industry.sector.label("sector_name"),
        Forecast.model_used,
        Forecast.forecast_value,
        Forecast.lower_bound_95,
        Forecast.upper_bound_95
    ).outerjoin(Province, Forecast.province_id == Province.id)\
     .outerjoin(Industry, Forecast.industry_id == Industry.id).all()

    df_forecast = pd.DataFrame(forecast_query)
    df_forecast.to_csv("dashboard/powerbi_forecast_dataset.csv", index=False)

    # 3. Export AI Insights Dataset
    insights_query = db.query(
        AIInsights.category,
        AIInsights.headline,
        AIInsights.insight_text,
        AIInsights.impact_level
    ).all()

    df_insights = pd.DataFrame(insights_query)
    df_insights.to_csv("dashboard/powerbi_insights_dataset.csv", index=False)

    db.close()
    print("Power BI datasets exported successfully to dashboard/ directory!")

if __name__ == "__main__":
    export_powerbi_datasets()
