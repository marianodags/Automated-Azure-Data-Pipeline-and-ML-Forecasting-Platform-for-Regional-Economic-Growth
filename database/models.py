from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base


class Province(Base):
    __tablename__ = "province"

    id = Column(Integer, primary_key=True, index=True)
    psgc_code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False, default="Region IX (Zamboanga Peninsula)")

    municipalities = relationship("Municipality", back_populates="province", cascade="all, delete-orphan")
    gdp_records = relationship("QuarterlyGDP", back_populates="province")
    revenue_records = relationship("Revenue", back_populates="province")
    forecasts = relationship("Forecast", back_populates="province")


class Municipality(Base):
    __tablename__ = "municipality"

    id = Column(Integer, primary_key=True, index=True)
    psgc_code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey("province.id"), nullable=False)
    lgu_class = Column(String(20), nullable=True)  # e.g., 1st Class, 2nd Class

    province = relationship("Province", back_populates="municipalities")
    revenue_records = relationship("Revenue", back_populates="municipality")


class Industry(Base):
    __tablename__ = "industry"

    id = Column(Integer, primary_key=True, index=True)
    psic_code = Column(String(10), unique=True, index=True, nullable=False)  # Philippine Standard Industrial Classification
    name = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=False)  # Agriculture, Manufacturing, Construction, Trade, Tourism, ICT, Services

    gdp_records = relationship("QuarterlyGDP", back_populates="industry")
    forecasts = relationship("Forecast", back_populates="industry")


class QuarterlyGDP(Base):
    __tablename__ = "quarterly_gdp"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)  # 1 to 4
    province_id = Column(Integer, ForeignKey("province.id"), nullable=True)
    industry_id = Column(Integer, ForeignKey("industry.id"), nullable=True)
    gdp_value_m_php = Column(Float, nullable=False)  # GDP value in Million PHP
    growth_rate_pct = Column(Float, nullable=True)

    province = relationship("Province", back_populates="gdp_records")
    industry = relationship("Industry", back_populates="gdp_records")


class Revenue(Base):
    __tablename__ = "revenue"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    province_id = Column(Integer, ForeignKey("province.id"), nullable=False)
    municipality_id = Column(Integer, ForeignKey("municipality.id"), nullable=True)
    tax_revenue_m_php = Column(Float, nullable=False)
    non_tax_revenue_m_php = Column(Float, nullable=False)
    total_revenue_m_php = Column(Float, nullable=False)

    province = relationship("Province", back_populates="revenue_records")
    municipality = relationship("Municipality", back_populates="revenue_records")


class Employment(Base):
    __tablename__ = "employment"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    region = Column(String(100), nullable=False, default="Region IX (Zamboanga Peninsula)")
    labor_force_participation_rate = Column(Float, nullable=False)
    employment_rate = Column(Float, nullable=False)
    unemployment_rate = Column(Float, nullable=False)
    underemployment_rate = Column(Float, nullable=False)


class Agriculture(Base):
    __tablename__ = "agriculture"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    commodity = Column(String(100), nullable=False)  # Palay, Corn, Coconut, Rubber, Fishery
    production_metric_tons = Column(Float, nullable=False)
    value_m_php = Column(Float, nullable=False)


class Inflation(Base):
    __tablename__ = "inflation"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    region = Column(String(100), nullable=False, default="Region IX (Zamboanga Peninsula)")
    cpi = Column(Float, nullable=False)  # Consumer Price Index
    inflation_rate_pct = Column(Float, nullable=False)


class Forecast(Base):
    __tablename__ = "forecast"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String(50), nullable=False)  # GDP, Industry_Growth, Revenue, Inflation, Employment, Agriculture
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=True)
    province_id = Column(Integer, ForeignKey("province.id"), nullable=True)
    industry_id = Column(Integer, ForeignKey("industry.id"), nullable=True)
    model_used = Column(String(50), nullable=False)  # XGBoost, ARIMA, Random Forest, Prophet
    forecast_value = Column(Float, nullable=False)
    lower_bound_95 = Column(Float, nullable=False)  # 95% Confidence Interval Lower
    upper_bound_95 = Column(Float, nullable=False)  # 95% Confidence Interval Upper
    created_at = Column(DateTime, default=datetime.utcnow)

    province = relationship("Province", back_populates="forecasts")
    industry = relationship("Industry", back_populates="forecasts")


class AIInsights(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # Executive, Forecast, Industry, Sector
    headline = Column(String(255), nullable=False)
    insight_text = Column(Text, nullable=False)
    impact_level = Column(String(20), nullable=False, default="Medium")  # High, Medium, Low
    generated_at = Column(DateTime, default=datetime.utcnow)
