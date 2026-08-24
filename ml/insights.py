import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import SessionLocal
from database.models import Forecast, AIInsights, QuarterlyGDP, Industry, Agriculture

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI_Insights")


class AIInsightsGenerator:
    def __init__(self, db_session: Session = None):
        self.db = db_session if db_session else SessionLocal()

    def generate_and_save_insights(self) -> List[Dict[str, str]]:
        """
        Synthesizes economic narrative insights from raw economic indicators and ML forecasts,
        and saves them to the AI_Insights table.
        """
        logger.info("Generating AI Insights from historical and forecast datasets...")

        # Clear old insights
        self.db.query(AIInsights).delete()
        self.db.commit()

        insights_list = []

        # 1. Sector Growth Drivers (e.g. Manufacturing / Construction)
        mfg_forecast = self.db.query(Forecast).join(Industry).filter(
            Forecast.metric_type == "Industry_Growth",
            Industry.sector == "Manufacturing",
            Forecast.year == 2026
        ).all()

        if mfg_forecast:
            avg_mfg_growth = sum(f.forecast_value for f in mfg_forecast) / len(mfg_forecast)
            mfg_insight = {
                "category": "Industry",
                "headline": "Manufacturing Sector Projected Acceleration",
                "insight_text": f"Manufacturing is projected to grow {avg_mfg_growth:.1f}% next year driven by regional industrial zone expansion and food processing demand.",
                "impact_level": "High"
            }
            insights_list.append(mfg_insight)

        # 2. Agriculture Climate Vulnerability Insight
        agri_insight = {
            "category": "Executive",
            "headline": "Agricultural Output Climate Vulnerability",
            "insight_text": "Agriculture production may experience temporary yield declines due to El Niño climate conditions affecting quarterly crop harvests in Zamboanga del Norte and Sibugay.",
            "impact_level": "High"
        }
        insights_list.append(agri_insight)

        # 3. Construction Contribution to GDP
        const_forecast = self.db.query(Forecast).join(Industry).filter(
            Forecast.metric_type == "GDP",
            Industry.sector == "Construction",
            Forecast.year == 2026
        ).all()
        
        all_gdp_forecast = self.db.query(Forecast).filter(
            Forecast.metric_type == "GDP",
            Forecast.year == 2026
        ).all()

        if const_forecast and all_gdp_forecast:
            const_val = sum(f.forecast_value for f in const_forecast)
            total_val = sum(f.forecast_value for f in all_gdp_forecast)
            share_pct = (const_val / total_val) * 100.0 if total_val > 0 else 0.0

            const_insight = {
                "category": "Forecast",
                "headline": "Infrastructure Construction Momentum",
                "insight_text": f"Construction contributes approximately {share_pct:.1f}% of projected regional GDP in 2026, driven by national infrastructure connectivity projects across Region IX.",
                "impact_level": "Medium"
            }
            insights_list.append(const_insight)

        # 4. Regional Inflation Trend
        inf_forecast = self.db.query(Forecast).filter(
            Forecast.metric_type == "Inflation",
            Forecast.year == 2026
        ).first()

        if inf_forecast:
            inf_insight = {
                "category": "Executive",
                "headline": "Inflation Rate Stabilization",
                "insight_text": f"Regional inflation rate is projected to stabilize around {inf_forecast.forecast_value:.1f}% in 2026 (95% CI: {inf_forecast.lower_bound_95:.1f}% - {inf_forecast.upper_bound_95:.1f}%), easing consumer cost pressures.",
                "impact_level": "Medium"
            }
            insights_list.append(inf_insight)

        # Save to Database
        for item in insights_list:
            insight_obj = AIInsights(**item)
            self.db.add(insight_obj)

        self.db.commit()
        logger.info(f"Generated and persisted {len(insights_list)} AI Insights.")
        return insights_list


if __name__ == "__main__":
    generator = AIInsightsGenerator()
    res = generator.generate_and_save_insights()
    print(f"Generated {len(res)} AI Insights:")
    for i in res:
        print(f"[{i['category']}] {i['headline']}: {i['insight_text']}")
