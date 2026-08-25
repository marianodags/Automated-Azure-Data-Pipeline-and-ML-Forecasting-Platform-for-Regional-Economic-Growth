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

    # 3. Seed Detailed Industries (PSA Standard Classification)
    industries_data = [
        {"psic_code": "A", "name": "Agriculture, forestry, and fishing", "sector": "Agriculture"},
        {"psic_code": "B", "name": "Mining and quarrying", "sector": "Industry"},
        {"psic_code": "C", "name": "Manufacturing", "sector": "Manufacturing"},
        {"psic_code": "D-E", "name": "Electricity, steam, water and waste management", "sector": "Industry"},
        {"psic_code": "F", "name": "Construction", "sector": "Construction"},
        {"psic_code": "G", "name": "Wholesale and retail trade; repair of motor vehicles and motorcycles", "sector": "Trade"},
        {"psic_code": "H", "name": "Transportation and storage", "sector": "Services"},
        {"psic_code": "I", "name": "Accommodation and food service activities", "sector": "Tourism"},
        {"psic_code": "J", "name": "Information and communication", "sector": "ICT"},
        {"psic_code": "K", "name": "Financial and insurance activities", "sector": "Services"},
        {"psic_code": "L", "name": "Real estate and ownership of dwellings", "sector": "Services"},
        {"psic_code": "M", "name": "Professional and business services", "sector": "Services"},
        {"psic_code": "N", "name": "Public administration and defense; compulsory social security", "sector": "Services"},
        {"psic_code": "P", "name": "Education", "sector": "Services"},
        {"psic_code": "Q", "name": "Human health and social work activities", "sector": "Services"},
        {"psic_code": "S", "name": "Other services", "sector": "Services"},
    ]

    industry_objs = {}
    for ind_data in industries_data:
        ind = Industry(**ind_data)
        db.add(ind)
        db.flush()
        industry_objs[ind.name] = ind

    # 4. Seed Official PSA Provincial Product Accounts (PPA) GDP for Zamboanga del Norte (2018-2024)
    # Unit in Image: In '000 PHP -> Converting to Million PHP (/ 1,000)
    zdn_gdp_ppa = {
        "Agriculture, forestry, and fishing": {
            2018: 19708798, 2019: 19176988, 2020: 18737364, 2021: 17374858, 2022: 17432561, 2023: 18806745, 2024: 18457242
        },
        "Mining and quarrying": {
            2018: 246148, 2019: 178693, 2020: 158736, 2021: 166800, 2022: 179693, 2023: 181497, 2024: 198428
        },
        "Manufacturing": {
            2018: 19977097, 2019: 19863802, 2020: 25522591, 2021: 22534272, 2022: 23213610, 2023: 21139584, 2024: 22343564
        },
        "Electricity, steam, water and waste management": {
            2018: 1061276, 2019: 1124432, 2020: 1239229, 2021: 1266646, 2022: 1229491, 2023: 1229970, 2024: 1314332
        },
        "Construction": {
            2018: 15129235, 2019: 14324717, 2020: 14575660, 2021: 14186003, 2022: 17223742, 2023: 19757593, 2024: 20268202
        },
        "Wholesale and retail trade; repair of motor vehicles and motorcycles": {
            2018: 20612961, 2019: 21668655, 2020: 21300422, 2021: 21581253, 2022: 22677794, 2023: 24125124, 2024: 25123193
        },
        "Transportation and storage": {
            2018: 3323679, 2019: 3712019, 2020: 2218896, 2021: 2153161, 2022: 2609020, 2023: 2910086, 2024: 3268885
        },
        "Accommodation and food service activities": {
            2018: 1698804, 2019: 1968138, 2020: 1081510, 2021: 1102003, 2022: 1448303, 2023: 1704906, 2024: 1919230
        },
        "Information and communication": {
            2018: 2168824, 2019: 2402877, 2020: 2533723, 2021: 2744117, 2022: 3028497, 2023: 3147811, 2024: 3323103
        },
        "Financial and insurance activities": {
            2018: 2388247, 2019: 2824945, 2020: 3055636, 2021: 3275015, 2022: 3663276, 2023: 3990136, 2024: 4396506
        },
        "Real estate and ownership of dwellings": {
            2018: 4471690, 2019: 4604662, 2020: 4487571, 2021: 4093993, 2022: 4155624, 2023: 4301690, 2024: 4489734
        },
        "Professional and business services": {
            2018: 653295, 2019: 685932, 2020: 596468, 2021: 665886, 2022: 710201, 2023: 762763, 2024: 851173
        },
        "Public administration and defense; compulsory social security": {
            2018: 3755759, 2019: 4192149, 2020: 4546942, 2021: 4664140, 2022: 4773369, 2023: 5011939, 2024: 5170492
        },
        "Education": {
            2018: 6784456, 2019: 7031650, 2020: 6981610, 2021: 8479728, 2022: 9238831, 2023: 9812897, 2024: 10104961
        },
        "Human health and social work activities": {
            2018: 1655980, 2019: 1791615, 2020: 2027145, 2021: 2297055, 2022: 2481143, 2023: 2644955, 2024: 2925556
        },
        "Other services": {
            2018: 1147078, 2019: 1320155, 2020: 377761, 2021: 372898, 2022: 514303, 2023: 681085, 2024: 733941
        }
    }

    zdn_prov = province_objs["Zamboanga del Norte"]
    quarter_distribution = [0.23, 0.24, 0.25, 0.28]

    for ind_name, years_data in zdn_gdp_ppa.items():
        ind = industry_objs[ind_name]
        for year in range(2018, 2025):
            annual_thousand = years_data[year]
            annual_m_php = annual_thousand / 1000.0  # Convert to Million PHP

            # Divide into 4 quarters
            for q in range(1, 5):
                q_val = round(annual_m_php * quarter_distribution[q - 1], 2)
                db.add(QuarterlyGDP(
                    year=year,
                    quarter=q,
                    province_id=zdn_prov.id,
                    industry_id=ind.id,
                    gdp_value_m_php=q_val,
                    growth_rate_pct=0.0
                ))

    # Also seed 2025 estimated baseline for ZDN
    for ind_name, years_data in zdn_gdp_ppa.items():
        ind = industry_objs[ind_name]
        annual_2024_m = years_data[2024] / 1000.0
        annual_2025_m = annual_2024_m * 1.05  # ~5% estimated growth
        for q in range(1, 5):
            q_val = round(annual_2025_m * quarter_distribution[q - 1], 2)
            db.add(QuarterlyGDP(
                year=2025,
                quarter=q,
                province_id=zdn_prov.id,
                industry_id=ind.id,
                gdp_value_m_php=q_val,
                growth_rate_pct=5.0
            ))

    # Seed remaining provinces
    other_provinces = ["Zamboanga del Sur", "Zamboanga Sibugay", "Zamboanga City (HUC)", "Isabela City"]
    for prov_name in other_provinces:
        prov = province_objs[prov_name]
        for ind_name, ind in industry_objs.items():
            base_m = zdn_gdp_ppa[ind_name][2024] / 1000.0
            mult = 1.1 if "Sur" in prov_name else (1.2 if "HUC" in prov_name else 0.7)
            for year in range(2018, 2026):
                growth = (1.04) ** (year - 2018)
                for q in range(1, 5):
                    q_val = round((base_m * mult * growth / 4.0), 2)
                    db.add(QuarterlyGDP(
                        year=year,
                        quarter=q,
                        province_id=prov.id,
                        industry_id=ind.id,
                        gdp_value_m_php=q_val,
                        growth_rate_pct=4.0
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
