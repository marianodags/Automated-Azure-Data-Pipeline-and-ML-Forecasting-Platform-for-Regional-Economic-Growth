# Power BI Dashboard Configuration & Integration Specifications

This directory contains DAX definitions, dataset connection queries, and visual layouts for the **AI-Powered Regional Economic Intelligence Platform** Power BI Report.

---

## 1. Power BI Data Source Connection (M / Power Query)

```powerquery
// Power Query M Script for Azure SQL Database Connection
let
    Server = "regional-econ-db-server.database.windows.net",
    Database = "regional_economy_db",
    Source = Sql.Database(Server, Database, [CreateNavigationProperties=true]),
    
    Province_Table = Source{[Schema="dbo",Item="province"]}[Data],
    Municipality_Table = Source{[Schema="dbo",Item="municipality"]}[Data],
    Industry_Table = Source{[Schema="dbo",Item="industry"]}[Data],
    QuarterlyGDP_Table = Source{[Schema="dbo",Item="quarterly_gdp"]}[Data],
    Forecast_Table = Source{[Schema="dbo",Item="forecast"]}[Data],
    AIInsights_Table = Source{[Schema="dbo",Item="ai_insights"]}[Data]
in
    Forecast_Table
```

---

## 2. Key DAX Measures

### Regional GDP & Forecast DAX Measures
```dax
// Total Historical GDP (Million PHP)
Total_Historical_GDP = 
SUM('QuarterlyGDP'[gdp_value_m_php])

// Total Projected GDP (Million PHP)
Total_Forecast_GDP = 
CALCULATE(
    SUM('Forecast'[forecast_value]),
    'Forecast'[metric_type] = "GDP"
)

// Combined Historical + Forecast GDP
Combined_GDP_Series = 
IF(
    HASONEVALUE('Calendar'[Year]) && SELECTEDVALUE('Calendar'[Year]) <= 2025,
    [Total_Historical_GDP],
    [Total_Forecast_GDP]
)

// Forecast 95% Upper Bound
Forecast_Upper_95 = 
CALCULATE(
    SUM('Forecast'[upper_bound_95]),
    'Forecast'[metric_type] = "GDP"
)

// Forecast 95% Lower Bound
Forecast_Lower_95 = 
CALCULATE(
    SUM('Forecast'[lower_bound_95]),
    'Forecast'[metric_type] = "GDP"
)

// GDP Growth Rate YoY (%)
GDP_YoY_Growth = 
VAR PrevYear = CALCULATE([Combined_GDP_Series], DATEADD('Calendar'[Date], -1, YEAR))
RETURN
IF(
    ISBLANK(PrevYear) || PrevYear == 0,
    BLANK(),
    DIVIDE([Combined_GDP_Series] - PrevYear, PrevYear) * 100
)
```

---

## 3. Power BI Dashboard Layout Specifications

### Page 1: Executive Dashboard
- **KPI Cards**:
  - Regional GDP (2025 Actual vs 2026 Forecast)
  - GDP YoY Growth Rate (%)
  - Per Capita GDP (PHP)
  - Inflation Rate (%)
  - Employment Rate (%)
  - Poverty Incidence Rate (%)
- **Main Visuals**:
  - Regional GDP Trend Line Chart (2018–2025 Actual vs 2026–2030* Forecast)
  - Provincial GDP Contribution Bar Chart

### Page 2: Forecast Dashboard
- **Main Visuals**:
  - Combined Line & Ribbon Chart: Actual vs Forecast (2020–2030*) with 95% Confidence Band (Lower_Bound_95 to Upper_Bound_95).
  - ML Model Accuracy Metrics Table (XGBoost, ARIMA, Random Forest MAE/RMSE comparisons).
  - Year Slicer (2020 to 2030).

### Page 3: Industry Sector Dashboard
- **Main Visuals**:
  - Industry Contribution Donut Chart & Treemap:
    - Agriculture, Forestry & Fishing
    - Manufacturing
    - Construction
    - Wholesale & Retail Trade
    - Tourism (Accommodation & Food)
    - ICT & Services
  - YoY Sector Growth Comparison Column Chart.

### Page 4: Interactive Philippine Map Dashboard
- **Main Visuals**:
  - Shape Map / ArcGIS Map: Drill-down from Region IX (Zamboanga Peninsula) -> Province (Zamboanga del Norte, Zamboanga del Sur, Zamboanga Sibugay, Zamboanga City, Isabela City) -> Municipalities.
  - Revenue & Local Economic Output Tooltips.

### Page 5: AI Insights & Scenario Simulator Dashboard
- **Main Visuals**:
  - AI Narratives Cards (Dynamically refreshed from `ai_insights` table).
  - What-If Scenario Parameter Sliders:
    - Agriculture Growth Delta (+/- %)
    - Manufacturing Expansion (+/- %)
    - Infrastructure Investment Multiplier
  - Dynamic Scenario Impact Gauge & Summary Table.
