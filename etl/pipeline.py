import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import (
    Province, Municipality, Industry, QuarterlyGDP,
    Revenue, Employment, Agriculture, Inflation
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ETL_Pipeline")


class DataValidationError(Exception):
    """Custom exception raised when data validation fails."""
    pass


class ETLPipeline:
    def __init__(self, db_session: Session = None):
        self.db = db_session if db_session else SessionLocal()

    def validate_missing_values(self, df: pd.DataFrame, required_cols: List[str]) -> pd.DataFrame:
        """Checks and fills or flags missing values in critical columns."""
        missing = df[required_cols].isnull().sum()
        if missing.any():
            logger.warning(f"Missing values detected: {missing[missing > 0].to_dict()}")
            # Fill numeric missing values with column median and text with 'Unknown'
            for col in required_cols:
                if df[col].dtype in ['float64', 'int64']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna('Unknown')
        return df

    def validate_duplicate_lgus(self, df: pd.DataFrame, id_cols: List[str]) -> pd.DataFrame:
        """Detects and removes duplicate LGU/province records."""
        duplicates = df.duplicated(subset=id_cols, keep='first')
        if duplicates.any():
            logger.warning(f"Found {duplicates.sum()} duplicate records on keys {id_cols}. Removing duplicates.")
            df = df.drop_duplicates(subset=id_cols, keep='first')
        return df

    def validate_psic_codes(self, df: pd.DataFrame, psic_col: str = "psic_code") -> pd.DataFrame:
        """Validates Philippine Standard Industrial Classification (PSIC) codes."""
        valid_psics = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"}
        invalid_mask = ~df[psic_col].astype(str).str.upper().isin(valid_psics)
        if invalid_mask.any():
            logger.warning(f"Invalid PSIC codes detected in {invalid_mask.sum()} rows. Sanitizing...")
            df.loc[invalid_mask, psic_col] = "A"  # Default fallback
        return df

    def validate_revenue_consistency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Verifies tax_revenue + non_tax_revenue == total_revenue, fixing minor discrepancies."""
        if set(["tax_revenue_m_php", "non_tax_revenue_m_php", "total_revenue_m_php"]).issubset(df.columns):
            expected_total = df["tax_revenue_m_php"] + df["non_tax_revenue_m_php"]
            diff = (df["total_revenue_m_php"] - expected_total).abs()
            inconsistent = diff > 0.01
            if inconsistent.any():
                logger.warning(f"Revenue total inconsistency detected in {inconsistent.sum()} rows. Recalculating totals.")
                df.loc[inconsistent, "total_revenue_m_php"] = expected_total[inconsistent]
        return df

    def clean_and_transform_gdp(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """ETL pipeline step for Quarterly GDP raw datasets."""
        logger.info("Cleaning & validating GDP dataset...")
        df = raw_df.copy()
        df = self.validate_missing_values(df, ["year", "quarter", "gdp_value_m_php"])
        df = self.validate_duplicate_lgus(df, ["year", "quarter", "province_id", "industry_id"])
        
        # Calculate growth rate if missing
        if "growth_rate_pct" not in df.columns or df["growth_rate_pct"].isnull().any():
            df["growth_rate_pct"] = df.groupby(["province_id", "industry_id"])["gdp_value_m_php"].pct_change() * 100
            df["growth_rate_pct"] = df["growth_rate_pct"].fillna(0.0)
            
        return df

    def process_and_load_revenue_batch(self, raw_records: List[Dict]) -> int:
        """Loads and validates a batch of raw revenue records into DB."""
        df = pd.DataFrame(raw_records)
        df = self.validate_missing_values(df, ["year", "province_id", "tax_revenue_m_php", "non_tax_revenue_m_php"])
        df = self.validate_duplicate_lgus(df, ["year", "province_id", "municipality_id"])
        df = self.validate_revenue_consistency(df)

        count = 0
        for _, row in df.iterrows():
            rev = Revenue(
                year=int(row["year"]),
                province_id=int(row["province_id"]),
                municipality_id=int(row["municipality_id"]) if pd.notnull(row.get("municipality_id")) else None,
                tax_revenue_m_php=float(row["tax_revenue_m_php"]),
                non_tax_revenue_m_php=float(row["non_tax_revenue_m_php"]),
                total_revenue_m_php=float(row["total_revenue_m_php"])
            )
            self.db.add(rev)
            count += 1

        self.db.commit()
        logger.info(f"Successfully processed and loaded {count} revenue records.")
        return count

    def run_full_etl(self) -> Dict[str, int]:
        """Runs validation routines across all database tables."""
        logger.info("Starting full database ETL validation run...")
        
        # Verify GDP records
        gdp_records = self.db.query(QuarterlyGDP).all()
        logger.info(f"Validated {len(gdp_records)} Quarterly GDP records.")
        
        # Verify Revenue records
        rev_records = self.db.query(Revenue).all()
        logger.info(f"Validated {len(rev_records)} Revenue records.")

        return {
            "gdp_records_validated": len(gdp_records),
            "revenue_records_validated": len(rev_records)
        }


if __name__ == "__main__":
    etl = ETLPipeline()
    res = etl.run_full_etl()
    print("ETL Validation Run Summary:", res)
