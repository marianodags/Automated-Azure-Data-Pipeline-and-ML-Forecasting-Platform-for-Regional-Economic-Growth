# AI-Powered Regional Economic Intelligence Platform

An end-to-end automated analytics platform that ingests regional economic data, performs automated ETL data cleaning and quality validation, trains Machine Learning models (XGBoost, Random Forest, ARIMA) for 2026–2030 economic forecasting with 95% Confidence Intervals, runs scenario analysis, generates automated AI narrative insights, and serves data via FastAPI REST API and Power BI dashboards.

---

## Architecture Overview

```
Data Sources (PSA, PPA, PLDS, Revenue, Inflation, Agriculture)
                         │
                         ▼
             Python Automated ETL
          (Cleaning, Quality Validation,
         PSIC Sanitization, Imputation)
                         │
                         ▼
        Azure SQL Database / SQLite Lake
                         │
                         ▼
            Machine Learning Engine
         (XGBoost, ARIMA, Random Forest)
      ├──────────────────────────────────┤
      │ Forecasts 2026-2030 + 95% CI     │
      │ What-If Scenario Simulator       │
      │ Automated AI Insights Generator  │
      └──────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   FastAPI REST API             Power BI Dashboards
 (/api/forecasts, etc.)     (Executive, Forecast,
                             Map, Industry, Insights)
```

---

## Key Features

- **Automated Data ETL Pipeline**: Cleaning, missing value imputation, duplicate LGU record removal, PSIC code validation, and tax/non-tax revenue consistency validation using Pandas.
- **Machine Learning & Time-Series Forecasting**:
  - Predicts **Regional GDP, Industry Sector Growth, Revenues, Inflation Rates, and Employment Rates** for 2026–2030.
  - Computes **95% Confidence Intervals** (Upper and Lower bounds).
- **Scenario Analysis Simulator ("What-If" Analysis)**:
  - Dynamic simulation engine to quantify economic impacts (e.g. *"What happens to regional GDP and employment if agriculture grows by 5%?"*).
- **AI Insights Engine**:
  - Automatically synthesizes economic narrative headlines and trends (e.g. *"Manufacturing projected to grow 1.9% next year"*, *"El Niño agricultural yields impact"*).
- **RESTful API Service**:
  - FastAPI web service providing endpoints for querying provinces, quarterly GDP, forecasts, AI insights, scenario simulations, and pipeline triggers.
- **Power BI Integration**:
  - DAX measures, dataset export scripts (`dashboard/export_datasets.py`), and 5-page dashboard specifications (`dashboard/POWER_BI_SPEC.md`).
- **Cloud Infrastructure & CI/CD**:
  - Azure Bicep IaC templates (`azure/main.bicep`) deploying Azure SQL DB, Blob Storage, Functions, and Azure Data Factory.
  - Docker containerization (`Dockerfile`, `docker-compose.yml`) and GitHub Actions workflow (`.github/workflows/ci.yml`).

---

## Directory Structure

```
├── api/
│   └── main.py              # FastAPI REST API Application
├── automation/
│   └── orchestrator.py      # Scheduled Daily ETL & Pipeline Trigger
├── azure/
│   └── main.bicep           # Azure IaC Infrastructure Template
├── dashboard/
│   ├── POWER_BI_SPEC.md     # Power BI Report Layout & DAX Specification
│   └── export_datasets.py   # Dataset Exporter for Power BI Ingestion
├── database/
│   ├── connection.py        # SQLAlchemy Connection & Initialization
│   ├── models.py            # Database Schema (ORM Models)
│   └── seed.py              # Historical Dataset Generator (2018-2025)
├── etl/
│   └── pipeline.py          # Data Validation & Cleaning Engine
├── ml/
│   ├── forecaster.py        # ML & Time Series Forecasting Engine
│   ├── insights.py          # Automated AI Narrative Generator
│   └── scenario.py          # Economic Scenario Analysis Simulator
├── tests/
│   └── test_platform.py     # pytest Unit & Integration Test Suite
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI/CD Pipeline
├── Dockerfile               # Docker Container Definition
├── docker-compose.yml       # Docker Compose Setup
└── requirements.txt         # Python Package Dependencies
```

---

## Quickstart Guide

### 1. Local Environment Setup

```bash
# Clone repository and create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Seed Database & Run ML Pipeline

```bash
# Seed database with Region IX economic data (2018–2025)
PYTHONPATH=. python3 database/seed.py

# Run ML forecaster and generate 2026-2030 predictions
PYTHONPATH=. python3 ml/forecaster.py

# Generate AI narrative insights
PYTHONPATH=. python3 ml/insights.py
```

### 3. Launch REST API Server

```bash
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```
- Open Swagger API Documentation: `http://localhost:8000/docs`

### 4. Run Automated Daily Pipeline

```bash
PYTHONPATH=. python3 automation/orchestrator.py
```

### 5. Run Test Suite

```bash
PYTHONPATH=. pytest
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API Health & Platform Info |
| `GET` | `/api/provinces` | List all provinces and LGUs |
| `GET` | `/api/municipalities` | List municipalities by province |
| `GET` | `/api/gdp/quarterly` | Historical quarterly GDP data |
| `GET` | `/api/forecasts` | ML forecasts (GDP, Revenue, Inflation, etc.) with 95% CIs |
| `GET` | `/api/ai-insights` | Automated AI narrative insights |
| `POST` | `/api/scenario/simulate` | Run "What-If" scenario simulations |
| `POST` | `/api/pipeline/trigger` | Manually trigger full ETL & ML retraining pipeline |

---

## Power BI Dashboard Overview

The platform exports dynamic datasets to CSV/SQL (`dashboard/powerbi_*.csv`) which feed into 5 interactive dashboard views:

1. **Executive Dashboard**: High-level KPIs (Regional GDP, Growth Rate, Inflation, Employment, Poverty).
2. **Forecast Dashboard**: Line & Ribbon Chart displaying 2020–2030* actual vs predicted values with a 95% Confidence Interval band.
3. **Industry Dashboard**: Sector breakdown (Agriculture, Manufacturing, Construction, Trade, Tourism, ICT).
4. **Interactive Map Dashboard**: Drill-down Philippine regional map from Region IX (Zamboanga Peninsula) down to Province & Municipality.
5. **AI Insights & What-If Simulator**: Interactive parameter sliders and AI narrative cards.

---

## Cloud Deployment (Azure)

Deploy Azure resources using Bicep CLI:

```bash
az group create --name rg-regional-econ-prod --location eastasia
az deployment group create \
  --resource-group rg-regional-econ-prod \
  --template-file azure/main.bicep \
  --parameters sqlAdminPassword="YourStrongPassword123!"
```
