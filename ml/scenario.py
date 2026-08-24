import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import SessionLocal
from database.models import QuarterlyGDP, Industry, Forecast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Scenario_Engine")


class ScenarioAnalysisEngine:
    def __init__(self, db_session: Session = None):
        self.db = db_session if db_session else SessionLocal()

    def simulate_sector_shock(
        self,
        target_year: int = 2026,
        agri_growth_delta_pct: float = 0.0,
        mfg_growth_delta_pct: float = 0.0,
        const_growth_delta_pct: float = 0.0,
        inflation_delta_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Simulates "What-if" economic scenarios (e.g., "What happens to regional GDP if agriculture grows by 5%?").
        Calculates baseline vs simulated regional GDP, sector growth, and employment impact.
        """
        # Get baseline forecasted GDP for target_year
        baseline_gdp_records = self.db.query(
            Forecast.industry_id, Forecast.forecast_value
        ).filter(
            Forecast.metric_type == "GDP",
            Forecast.year == target_year
        ).all()

        if not baseline_gdp_records:
            return {"error": f"No baseline forecasts found for target year {target_year}"}

        # Calculate baseline total regional GDP
        baseline_total_gdp = sum(r[1] for r in baseline_gdp_records)

        # Map industry sector names
        industries = self.db.query(Industry).all()
        industry_map = {ind.id: ind.sector for ind in industries}

        simulated_total_gdp = 0.0
        sector_adjustments = {
            "Agriculture": agri_growth_delta_pct,
            "Manufacturing": mfg_growth_delta_pct,
            "Construction": const_growth_delta_pct
        }

        sector_breakdown = {}

        for ind_id, base_val in baseline_gdp_records:
            sector_name = industry_map.get(ind_id, "Services")
            delta_pct = sector_adjustments.get(sector_name, 0.0)
            
            # Apply shock multiplier
            sim_val = base_val * (1.0 + (delta_pct / 100.0))
            simulated_total_gdp += sim_val

            if sector_name not in sector_breakdown:
                sector_breakdown[sector_name] = {"baseline": 0.0, "simulated": 0.0}
            sector_breakdown[sector_name]["baseline"] += base_val
            sector_breakdown[sector_name]["simulated"] += sim_val

        gdp_diff_m_php = round(simulated_total_gdp - baseline_total_gdp, 2)
        pct_change_total_gdp = round((gdp_diff_m_php / baseline_total_gdp) * 100, 2)

        # Estimated job creation/loss impact (~ 1500 jobs per 100M PHP GDP change)
        est_jobs_impact = int((gdp_diff_m_php / 100.0) * 1500)

        result = {
            "target_year": target_year,
            "scenarios_applied": {
                "agriculture_growth_delta_pct": agri_growth_delta_pct,
                "manufacturing_growth_delta_pct": mfg_growth_delta_pct,
                "construction_growth_delta_pct": const_growth_delta_pct,
                "inflation_delta_pct": inflation_delta_pct
            },
            "baseline_regional_gdp_m_php": round(baseline_total_gdp, 2),
            "simulated_regional_gdp_m_php": round(simulated_total_gdp, 2),
            "gdp_difference_m_php": gdp_diff_m_php,
            "regional_gdp_growth_delta_pct": pct_change_total_gdp,
            "estimated_employment_impact_jobs": est_jobs_impact,
            "sector_breakdown_m_php": {
                sec: {
                    "baseline": round(data["baseline"], 2),
                    "simulated": round(data["simulated"], 2),
                    "delta_m_php": round(data["simulated"] - data["baseline"], 2)
                }
                for sec, data in sector_breakdown.items()
            }
        }

        logger.info(f"Executed scenario analysis for {target_year}: Delta GDP = {gdp_diff_m_php} M PHP ({pct_change_total_gdp}%)")
        return result


if __name__ == "__main__":
    scenario = ScenarioAnalysisEngine()
    sim_res = scenario.simulate_sector_shock(target_year=2026, agri_growth_delta_pct=5.0)
    print("Scenario Analysis Result (+5% Agriculture):")
    print(sim_res)
