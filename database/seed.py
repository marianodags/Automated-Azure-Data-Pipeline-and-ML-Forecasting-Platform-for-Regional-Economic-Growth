import random
import numpy as np
from datetime import datetime
from database.connection import init_db, SessionLocal
from database.models import (
    Province, Municipality, Industry, QuarterlyGDP,
    Revenue, Employment, Agriculture, Inflation
)


def seed_database():
    init_db()
    db = SessionLocal()

    # Avoid duplicate seeding
    if db.query(Province).first():
        print("Database already seeded.")
        db.close()
        return

    print("Seeding database with Region IX historical economic data (2018-2025)...")

    # 1. Seed Provinces
    provinces_data = [
        {"psgc_code": "097200000", "name": "Zamboanga del Norte", "region": "Region IX (Zamboanga Peninsula)"},
        {"psgc_code": "097300000", "name": "Zamboanga del Sur", "region": "Region IX (Zamboanga Peninsula)"},
        {"psgc_code": "098300000", "name": "Zamboanga Sibugay", "region": "Region IX (Zamboanga Peninsula)"},
        {"psgc_code": "097332000", "name": "Zamboanga City (HUC)", "region": "Region IX (Zamboanga Peninsula)"},
        {"psgc_code": "099700000", "name": "Isabela City", "region": "Region IX (Zamboanga Peninsula)"},
    ]

    province_objs = {}
    for p_data in provinces_data:
        p = Province(**p_data)
        db.add(p)
        db.flush()
        province_objs[p.name] = p

    # 2. Seed Municipalities
    municipalities_data = [
        {"psgc_code": "097201000", "name": "Dapitan City", "province_id": province_objs["Zamboanga del Norte"].id, "lgu_class": "3rd Class Component City"},
        {"psgc_code": "097202000", "name": "Dipolog City", "province_id": province_objs["Zamboanga del Norte"].id, "lgu_class": "3rd Class Component City"},
        {"psgc_code": "097218000", "name": "Sindangan", "province_id": province_objs["Zamboanga del Norte"].id, "lgu_class": "1st Class"},
        {"psgc_code": "097322000", "name": "Pagadian City", "province_id": province_objs["Zamboanga del Sur"].id, "lgu_class": "2nd Class Component City"},
        {"psgc_code": "097316000", "name": "Molave", "province_id": province_objs["Zamboanga del Sur"].id, "lgu_class": "1st Class"},
        {"psgc_code": "098301000", "name": "Ipil", "province_id": province_objs["Zamboanga Sibugay"].id, "lgu_class": "1st Class"},
        {"psgc_code": "098302000", "name": "Alicia", "province_id": province_objs["Zamboanga Sibugay"].id, "lgu_class": "3rd Class"},
        {"psgc_code": "097332001", "name": "Zamboanga City Proper", "province_id": province_objs["Zamboanga City (HUC)"].id, "lgu_class": "Highly Urbanized City"},
        {"psgc_code": "099700001", "name": "Isabela City Central", "province_id": province_objs["Isabela City"].id, "lgu_class": "Component City"},
    ]

    muni_objs = []
    for m_data in municipalities_data:
        m = Municipality(**m_data)
        db.add(m)
        muni_objs.append(m)
    db.flush()

    # 3. Seed Industries
    industries_data = [
        {"psic_code": "A", "name": "Agriculture, Forestry and Fishing", "sector": "Agriculture"},
        {"psic_code": "C", "name": "Manufacturing", "sector": "Manufacturing"},
        {"psic_code": "F", "name": "Construction", "sector": "Construction"},
        {"psic_code": "G", "name": "Wholesale and Retail Trade", "sector": "Trade"},
        {"psic_code": "I", "name": "Accommodation and Food Service Activities", "sector": "Tourism"},
        {"psic_code": "J", "name": "Information and Communication", "sector": "ICT"},
        {"psic_code": "K", "name": "Financial and Insurance Activities", "sector": "Services"},
    ]

    industry_objs = {}
    for ind_data in industries_data:
        ind = Industry(**ind_data)
        db.add(ind)
        db.flush()
        industry_objs[ind.sector] = ind

    # 4. Seed Quarterly GDP (2018 - 2025)
    # Baseline quarterly GDP in Million PHP for Region IX components (~380 Billion PHP total annual GRDP for Region IX)
    base_gdp_by_province = {
        "Zamboanga del Norte": 22000.0,
        "Zamboanga del Sur": 30000.0,
        "Zamboanga Sibugay": 18000.0,
        "Zamboanga City (HUC)": 35000.0,
        "Isabela City": 50000.0 / 10.0,
    }

    sector_shares = {
        "Agriculture": 0.28,
        "Manufacturing": 0.18,
        "Construction": 0.12,
        "Trade": 0.22,
        "Tourism": 0.08,
        "ICT": 0.05,
        "Services": 0.07,
    }

    # Growth multipliers per year (reflecting COVID shock in 2020 and post-COVID recovery)
    yearly_growth_multiplier = {
        2018: 1.00,
        2019: 1.06,
        2020: 0.94,  # -6% contraction in 2020
        2021: 1.02,  # rebound starts
        2022: 1.075, # strong rebound
        2023: 1.052, # steady growth
        2024: 1.061,
        2025: 1.065,
    }

    quarter_seasonality = {1: 0.23, 2: 0.24, 3: 0.25, 4: 0.28}

    random.seed(42)
    np.random.seed(42)

    for prov_name, prov in province_objs.items():
        base_val = base_gdp_by_province[prov_name]
        for year in range(2018, 2026):
            growth_mult = yearly_growth_multiplier[year]
            for quarter in range(1, 5):
                q_season = quarter_seasonality[quarter]
                for sector_name, share in sector_shares.items():
                    ind = industry_objs[sector_name]
                    # Calculated quarterly GDP with minor random noise
                    noise = np.random.normal(1.0, 0.015)
                    gdp_val = round(base_val * growth_mult * q_season * share * noise, 2)

                    # Compute YoY growth rate if year > 2018
                    growth_rate = round((growth_mult - 1.0) * 100 + np.random.normal(0, 0.5), 2)

                    db.add(QuarterlyGDP(
                        year=year,
                        quarter=quarter,
                        province_id=prov.id,
                        industry_id=ind.id,
                        gdp_value_m_php=gdp_val,
                        growth_rate_pct=growth_rate
                    ))

    # 5. Seed Revenue (2018 - 2025)
    for year in range(2018, 2026):
        growth = (1 + 0.05) ** (year - 2018)
        for prov_name, prov in province_objs.items():
            tax_rev = round(1200.0 * growth * random.uniform(0.95, 1.05), 2)
            non_tax = round(800.0 * growth * random.uniform(0.95, 1.05), 2)
            total = round(tax_rev + non_tax, 2)
            db.add(Revenue(
                year=year,
                province_id=prov.id,
                municipality_id=None,
                tax_revenue_m_php=tax_rev,
                non_tax_revenue_m_php=non_tax,
                total_revenue_m_php=total
            ))

        for muni in muni_objs:
            muni_tax = round(150.0 * growth * random.uniform(0.92, 1.08), 2)
            muni_non_tax = round(100.0 * growth * random.uniform(0.92, 1.08), 2)
            muni_total = round(muni_tax + muni_non_tax, 2)
            db.add(Revenue(
                year=year,
                province_id=muni.province_id,
                municipality_id=muni.id,
                tax_revenue_m_php=muni_tax,
                non_tax_revenue_m_php=muni_non_tax,
                total_revenue_m_php=muni_total
            ))

    # 6. Seed Employment (2018 - 2025 Quarterly)
    for year in range(2018, 2026):
        for q in range(1, 5):
            if year == 2020:
                unemp = round(random.uniform(8.5, 11.2), 2)
                emp = round(100.0 - unemp, 2)
                lfpr = round(random.uniform(58.0, 61.0), 2)
                underemp = round(random.uniform(18.0, 22.0), 2)
            else:
                unemp = round(random.uniform(3.8, 5.5), 2)
                emp = round(100.0 - unemp, 2)
                lfpr = round(random.uniform(62.0, 66.0), 2)
                underemp = round(random.uniform(12.0, 16.0), 2)

            db.add(Employment(
                year=year,
                quarter=q,
                region="Region IX (Zamboanga Peninsula)",
                labor_force_participation_rate=lfpr,
                employment_rate=emp,
                unemployment_rate=unemp,
                underemployment_rate=underemp
            ))

    # 7. Seed Agriculture (2018 - 2025 Quarterly)
    commodities = ["Palay", "Corn", "Coconut", "Rubber", "Fishery"]
    base_prod = {"Palay": 180000, "Corn": 95000, "Coconut": 220000, "Rubber": 45000, "Fishery": 130000}
    price_per_ton = {"Palay": 19000, "Corn": 16000, "Coconut": 28000, "Rubber": 55000, "Fishery": 85000}

    for year in range(2018, 2026):
        # El Niño shock simulated in 2023/2024
        weather_factor = 0.90 if year in [2023, 2024] else 1.02
        for q in range(1, 5):
            for comm in commodities:
                prod = round(base_prod[comm] * 0.25 * weather_factor * random.uniform(0.95, 1.05), 2)
                val_m = round((prod * price_per_ton[comm]) / 1e6, 2)
                db.add(Agriculture(
                    year=year,
                    quarter=q,
                    commodity=comm,
                    production_metric_tons=prod,
                    value_m_php=val_m
                ))

    # 8. Seed Inflation (2018 - 2025 Monthly)
    base_cpi = 100.0
    for year in range(2018, 2026):
        for month in range(1, 13):
            # Inflation peaks in late 2022 / early 2023 due to global commodity prices
            if year == 2022 and month >= 8:
                inf_rate = round(random.uniform(6.5, 7.9), 2)
            elif year == 2023 and month <= 6:
                inf_rate = round(random.uniform(6.8, 8.2), 2)
            elif year in [2020, 2021]:
                inf_rate = round(random.uniform(2.1, 3.8), 2)
            else:
                inf_rate = round(random.uniform(3.2, 4.8), 2)

            base_cpi += (inf_rate / 12.0)
            db.add(Inflation(
                year=year,
                month=month,
                region="Region IX (Zamboanga Peninsula)",
                cpi=round(base_cpi, 2),
                inflation_rate_pct=inf_rate
            ))

    db.commit()
    db.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
