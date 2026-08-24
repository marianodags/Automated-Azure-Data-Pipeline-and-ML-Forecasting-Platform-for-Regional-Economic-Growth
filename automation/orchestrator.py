import logging
import datetime
from database.connection import SessionLocal
from etl.pipeline import ETLPipeline
from ml.forecaster import MLForecastingEngine
from ml.insights import AIInsightsGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Pipeline_Orchestrator")


class AutomatedPipelineOrchestrator:
    """
    Simulates Azure Functions / Azure Data Factory daily midnight schedule:
    Download/Ingest -> ETL Clean & Validate -> Retrain ML & Forecast -> Generate AI Insights -> Upload Azure SQL / Power BI.
    """
    def __init__(self):
        self.db = SessionLocal()

    def run_daily_pipeline(self):
        start_time = datetime.datetime.now()
        logger.info(f"=== Starting Automated Pipeline Schedule Run: {start_time} ===")

        # Step 1: Ingest & ETL Cleaning & Validation
        logger.info("[Step 1/4] Running Ingest & ETL Validation...")
        etl = ETLPipeline(db_session=self.db)
        etl_summary = etl.run_full_etl()

        # Step 2: Retrain Machine Learning Models & Generate Forecasts
        logger.info("[Step 2/4] Retraining ML Models & Generating Forecasts...")
        forecaster = MLForecastingEngine(db_session=self.db)
        forecast_count = forecaster.generate_all_forecasts(start_year=2026, end_year=2030)

        # Step 3: Generate Automated AI Narrative Insights
        logger.info("[Step 3/4] Generating AI Insights...")
        insights_gen = AIInsightsGenerator(db_session=self.db)
        insights = insights_gen.generate_and_save_insights()

        # Step 4: Finalize & Publish (Power BI Refresh Trigger Simulation)
        end_time = datetime.datetime.now()
        duration_sec = (end_time - start_time).total_seconds()

        summary = {
            "status": "SUCCESS",
            "timestamp": start_time.isoformat(),
            "execution_time_seconds": round(duration_sec, 2),
            "etl_summary": etl_summary,
            "forecast_records_generated": forecast_count,
            "ai_insights_generated": len(insights)
        }

        logger.info(f"=== Completed Scheduled Pipeline Run in {duration_sec:.2f}s ===")
        self.db.close()
        return summary


if __name__ == "__main__":
    orchestrator = AutomatedPipelineOrchestrator()
    res = orchestrator.run_daily_pipeline()
    print("Orchestrator Execution Run Summary:")
    print(res)
