from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database.connection import get_db, init_db
from database.models import (
    Province, Municipality, Industry, QuarterlyGDP,
    Revenue, Employment, Agriculture, Inflation, Forecast, AIInsights
)
from ml.scenario import ScenarioAnalysisEngine
from automation.orchestrator import AutomatedPipelineOrchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI-Powered Regional Economic Intelligence Platform API",
    description="REST API serving Regional GDP, Forecasts, AI Insights, Economic Scenario Simulations, and Pipeline Automation.",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Web Dashboard static directory if present
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/dashboard", response_class=FileResponse)
def get_dashboard():
    """Serve the Web Dashboard UI."""
    dashboard_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard UI file not found.")
    return FileResponse(dashboard_path)


# Serve dashboard static assets
if os.path.exists("dashboard"):
    app.mount("/static", StaticFiles(directory="dashboard"), name="static")


@app.get("/")
def read_root():
    return {
        "platform": "AI-Powered Regional Economic Intelligence Platform",
        "region": "Region IX (Zamboanga Peninsula)",
        "status": "Online",
        "dashboard_url": "/dashboard",
        "docs_url": "/docs"
    }


@app.get("/dashboard")
def get_dashboard():
    """Serves the interactive web dashboard HTML UI."""
    dashboard_path = os.path.join("dashboard", "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="Dashboard UI file not found")


@app.get("/api/provinces")
def get_provinces(db: Session = Depends(get_db)):
    """Fetch all provinces in the region."""
    provinces = db.query(Province).all()
    return [
        {
            "id": p.id,
            "psgc_code": p.psgc_code,
            "name": p.name,
            "region": p.region
        }
        for p in provinces
    ]


@app.get("/api/municipalities")
def get_municipalities(province_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Fetch municipalities filtered optional by province."""
    query = db.query(Municipality)
    if province_id:
        query = query.filter(Municipality.province_id == province_id)
    municipalities = query.all()
    return [
        {
            "id": m.id,
            "psgc_code": m.psgc_code,
            "name": m.name,
            "province_id": m.province_id,
            "lgu_class": m.lgu_class
        }
        for m in municipalities
    ]


@app.get("/api/gdp/quarterly")
def get_quarterly_gdp(
    province_id: Optional[int] = None,
    industry_id: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Fetch quarterly regional GDP dataset."""
    query = db.query(QuarterlyGDP)
    if province_id:
        query = query.filter(QuarterlyGDP.province_id == province_id)
    if industry_id:
        query = query.filter(QuarterlyGDP.industry_id == industry_id)
    if year:
        query = query.filter(QuarterlyGDP.year == year)

    records = query.all()
    return [
        {
            "id": r.id,
            "year": r.year,
            "quarter": r.quarter,
            "province_id": r.province_id,
            "industry_id": r.industry_id,
            "gdp_value_m_php": r.gdp_value_m_php,
            "growth_rate_pct": r.growth_rate_pct
        }
        for r in records
    ]


@app.get("/api/forecasts")
def get_forecasts(
    metric_type: Optional[str] = Query(None, description="GDP, Industry_Growth, Revenue, Inflation, Employment"),
    year: Optional[int] = None,
    province_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Fetch ML forecasts with 95% confidence intervals."""
    query = db.query(Forecast)
    if metric_type:
        query = query.filter(Forecast.metric_type == metric_type)
    if year:
        query = query.filter(Forecast.year == year)
    if province_id:
        query = query.filter(Forecast.province_id == province_id)

    records = query.all()
    return [
        {
            "id": r.id,
            "metric_type": r.metric_type,
            "year": r.year,
            "quarter": r.quarter,
            "province_id": r.province_id,
            "industry_id": r.industry_id,
            "model_used": r.model_used,
            "forecast_value": r.forecast_value,
            "lower_bound_95": r.lower_bound_95,
            "upper_bound_95": r.upper_bound_95
        }
        for r in records
    ]


@app.get("/api/ai-insights")
def get_ai_insights(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Fetch AI-generated narrative insights."""
    query = db.query(AIInsights)
    if category:
        query = query.filter(AIInsights.category == category)
    insights = query.all()
    return [
        {
            "id": i.id,
            "category": i.category,
            "headline": i.headline,
            "insight_text": i.insight_text,
            "impact_level": i.impact_level,
            "generated_at": i.generated_at.isoformat() if i.generated_at else None
        }
        for i in insights
    ]


@app.post("/api/scenario/simulate")
def run_scenario_simulation(
    target_year: int = 2026,
    agri_growth_delta_pct: float = 0.0,
    mfg_growth_delta_pct: float = 0.0,
    const_growth_delta_pct: float = 0.0,
    inflation_delta_pct: float = 0.0,
    db: Session = Depends(get_db)
):
    """Simulate economic scenario shocks (e.g. +5% Agriculture growth)."""
    engine = ScenarioAnalysisEngine(db_session=db)
    result = engine.simulate_sector_shock(
        target_year=target_year,
        agri_growth_delta_pct=agri_growth_delta_pct,
        mfg_growth_delta_pct=mfg_growth_delta_pct,
        const_growth_delta_pct=const_growth_delta_pct,
        inflation_delta_pct=inflation_delta_pct
    )
    return result


@app.post("/api/pipeline/trigger")
def trigger_pipeline():
    """Triggers end-to-end automated ETL, ML retraining, and forecast refresh."""
    orchestrator = AutomatedPipelineOrchestrator()
    summary = orchestrator.run_daily_pipeline()
    return summary
