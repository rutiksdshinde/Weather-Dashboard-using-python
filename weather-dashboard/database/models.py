"""
Database models for Weather Dashboard
Stores user preferences, historical scores, and cached weather data
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class UserPreference(Base):
    """User preferences for saved cities and activity priorities"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    city_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country = Column(String(50))
    is_primary = Column(Boolean, default=False)
    
    # Activity priorities (1-5 scale)
    laundry_priority = Column(Integer, default=3)
    driving_priority = Column(Integer, default=3)
    outdoor_priority = Column(Integer, default=3)
    irrigation_priority = Column(Integer, default=3)
    power_risk_priority = Column(Integer, default=3)
    
    # Alert thresholds
    power_risk_threshold = Column(Integer, default=70)
    rain_alert = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    historical_scores = relationship("HistoricalScore", back_populates="user_preference", cascade="all, delete-orphan")
    alerts = relationship("AlertLog", back_populates="user_preference", cascade="all, delete-orphan")


class HistoricalScore(Base):
    """Historical daily scores for trend analysis"""
    __tablename__ = 'historical_scores'
    
    id = Column(Integer, primary_key=True)
    preference_id = Column(Integer, ForeignKey('user_preferences.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Weather data snapshot
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    rain_chance = Column(Float)
    uv_index = Column(Float)
    
    # Activity scores (0-100)
    laundry_score = Column(Float)
    driving_score = Column(Float)
    outdoor_score = Column(Float)
    irrigation_score = Column(Float)
    power_risk_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user_preference = relationship("UserPreference", back_populates="historical_scores")


class AlertLog(Base):
    """Log of sent alerts"""
    __tablename__ = 'alert_logs'
    
    id = Column(Integer, primary_key=True)
    preference_id = Column(Integer, ForeignKey('user_preferences.id'), nullable=False)
    alert_type = Column(String(50), nullable=False)  # power_risk, rain, etc.
    message = Column(Text)
    score_value = Column(Float)
    threshold = Column(Float)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user_preference = relationship("UserPreference", back_populates="alerts")


class WeatherCache(Base):
    """Cache for weather API responses"""
    __tablename__ = 'weather_cache'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weather_data = Column(Text, nullable=False)  # JSON string
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


# Database setup
DATABASE_URL = "sqlite:///./weather_dashboard.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database and create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()