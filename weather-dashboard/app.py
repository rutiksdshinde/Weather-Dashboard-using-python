"""
Weather Dashboard - Main FastAPI Application
A comprehensive weather dashboard with activity scoring for Indian users
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.models import (
    init_db, get_db, SessionLocal, 
    UserPreference, HistoricalScore, AlertLog, WeatherCache
)
from weather_api import search_city, get_weather_data, get_weather_code_description
from scoring.laundry import calculate_laundry_score, get_laundry_recommendation
from scoring.driving import calculate_driving_score, get_driving_recommendation
from scoring.outdoor import calculate_outdoor_score, get_outdoor_recommendation
from scoring.power_risk import calculate_power_risk_score, get_power_risk_recommendation
from scoring.irrigation import calculate_irrigation_score, get_irrigation_recommendation


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: cleanup if needed


# Initialize FastAPI app
app = FastAPI(
    title="Weather Dashboard",
    description="A comprehensive weather dashboard with activity scoring for Indian users",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Pydantic models for request/response
class CitySearchRequest(BaseModel):
    city_name: str = Field(..., min_length=1, max_length=100)


class WeatherRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    city_name: Optional[str] = None


class UserPreferenceCreate(BaseModel):
    city_name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    is_primary: bool = False
    laundry_priority: int = Field(1, ge=1, le=5)
    driving_priority: int = Field(1, ge=1, le=5)
    outdoor_priority: int = Field(1, ge=1, le=5)
    irrigation_priority: int = Field(1, ge=1, le=5)
    power_risk_priority: int = Field(1, ge=1, le=5)
    power_risk_threshold: int = Field(70, ge=10, le=90)
    rain_alert: bool = False


class AlertNotificationRequest(BaseModel):
    preference_id: int
    alert_type: str
    message: str


# Cache management
CACHE_DURATION_MINUTES = 10


def get_cached_weather(lat: float, lon: float, db: Session) -> Optional[dict]:
    """Get weather data from cache if available and not expired."""
    cache = db.query(WeatherCache).filter(
        WeatherCache.latitude == lat,
        WeatherCache.longitude == lon
    ).first()
    
    if cache and cache.expires_at > datetime.utcnow():
        return json.loads(cache.weather_data)
    return None


def cache_weather_data(lat: float, lon: float, data: dict, db: Session):
    """Store weather data in cache."""
    # Delete old cache entry if exists
    db.query(WeatherCache).filter(
        WeatherCache.latitude == lat,
        WeatherCache.longitude == lon
    ).delete()
    
    # Create new cache entry
    cache = WeatherCache(
        latitude=lat,
        longitude=lon,
        weather_data=json.dumps(data),
        expires_at=datetime.utcnow() + timedelta(minutes=CACHE_DURATION_MINUTES)
    )
    db.add(cache)
    db.commit()


def calculate_all_scores(weather_data: dict, is_daytime: bool = True) -> dict:
    """Calculate all activity scores from weather data."""
    current = weather_data.get("current", {})
    temp = current.get("temperature", 25)
    humidity = current.get("humidity", 50)
    wind_speed = current.get("wind_speed", 10)
    rain_chance = weather_data.get("rain_chance", 0)
    uv_index = weather_data.get("uv_index", 0)
    has_thunderstorm = weather_data.get("has_thunderstorm", False)
    has_lightning = weather_data.get("has_lightning", False)
    has_rain = current.get("precipitation", 0) > 0
    
    # Calculate scores
    laundry_score = calculate_laundry_score(
        humidity, rain_chance, wind_speed, temp, uv_index, is_daytime
    )
    
    driving_score = calculate_driving_score(
        rain_chance, wind_speed, temp, has_fog=False, is_daytime=is_daytime
    )
    
    outdoor_score = calculate_outdoor_score(
        temp, humidity, wind_speed, rain_chance, uv_index, is_daytime
    )
    
    irrigation_score = calculate_irrigation_score(
        temp, humidity, wind_speed, rain_chance, has_rain, "morning"
    )
    
    time_of_day = "evening" if not is_daytime else "day"
    power_risk_score = calculate_power_risk_score(
        temp, humidity, wind_speed, rain_chance, 
        has_thunderstorm, has_lightning, time_of_day
    )
    
    return {
        "laundry": {
            "score": laundry_score,
            **get_laundry_recommendation(laundry_score)
        },
        "driving": {
            "score": driving_score,
            **get_driving_recommendation(driving_score)
        },
        "outdoor": {
            "score": outdoor_score,
            **get_outdoor_recommendation(outdoor_score)
        },
        "irrigation": {
            "score": irrigation_score,
            **get_irrigation_recommendation(irrigation_score)
        },
        "power_risk": {
            "score": power_risk_score,
            **get_power_risk_recommendation(power_risk_score)
        }
    }


# API Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/search")
async def search_city_api(request: CitySearchRequest):
    """Search for a city by name."""
    result = search_city(request.city_name)
    if result:
        return {"success": True, "data": result}
    raise HTTPException(status_code=404, detail="City not found")


@app.post("/api/weather")
async def get_weather(request: WeatherRequest, db: Session = Depends(get_db)):
    """Get weather data and calculate activity scores for a location."""
    # Check cache first
    cached = get_cached_weather(request.latitude, request.longitude, db)
    if cached:
        return {"success": True, "data": cached, "cached": True}
    
    # Fetch fresh data
    weather_data = get_weather_data(request.latitude, request.longitude)
    if not weather_data:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    # Determine if daytime (simple check based on current hour)
    current_hour = datetime.now().hour
    is_daytime = 6 <= current_hour <= 18
    
    # Calculate all scores
    scores = calculate_all_scores(weather_data, is_daytime)
    
    # Add weather description
    weather_code = weather_data["current"].get("weather_code", 0)
    weather_data["weather_description"] = get_weather_code_description(weather_code)
    
    # Prepare response
    response_data = {
        "weather": weather_data,
        "scores": scores,
        "city_name": request.city_name,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Cache the data
    cache_weather_data(request.latitude, request.longitude, response_data, db)
    
    return {"success": True, "data": response_data, "cached": False}


@app.get("/api/weather/{city_name}")
async def get_weather_by_city(city_name: str, db: Session = Depends(get_db)):
    """Get weather data for a city by name."""
    city_info = search_city(city_name)
    if not city_info:
        raise HTTPException(status_code=404, detail="City not found")
    
    return await get_weather(
        WeatherRequest(
            latitude=city_info["latitude"],
            longitude=city_info["longitude"],
            city_name=city_info["name"]
        ),
        db
    )


# User Preferences Routes
@app.get("/api/preferences")
async def get_preferences(db: Session = Depends(get_db)):
    """Get all saved user preferences."""
    preferences = db.query(UserPreference).all()
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "city_name": p.city_name,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "country": p.country,
                "is_primary": p.is_primary,
                "power_risk_threshold": p.power_risk_threshold,
                "rain_alert": p.rain_alert
            }
            for p in preferences
        ]
    }


@app.post("/api/preferences")
async def create_preference(
    preference: UserPreferenceCreate, 
    db: Session = Depends(get_db)
):
    """Create a new user preference."""
    # If setting as primary, unset other primaries
    if preference.is_primary:
        db.query(UserPreference).update({"is_primary": False})
    
    db_pref = UserPreference(**preference.model_dump())
    db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    
    return {"success": True, "data": {"id": db_pref.id, **preference.model_dump()}}


@app.delete("/api/preferences/{preference_id}")
async def delete_preference(preference_id: int, db: Session = Depends(get_db)):
    """Delete a user preference."""
    pref = db.query(UserPreference).filter(
        UserPreference.id == preference_id
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    db.delete(pref)
    db.commit()
    return {"success": True, "message": "Preference deleted"}


@app.get("/api/preferences/{preference_id}/weather")
async def get_preference_weather(preference_id: int, db: Session = Depends(get_db)):
    """Get weather and scores for a saved preference."""
    pref = db.query(UserPreference).filter(
        UserPreference.id == preference_id
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    weather_data = get_weather_data(pref.latitude, pref.longitude)
    if not weather_data:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    current_hour = datetime.now().hour
    is_daytime = 6 <= current_hour <= 18
    
    scores = calculate_all_scores(weather_data, is_daytime)
    
    weather_code = weather_data["current"].get("weather_code", 0)
    weather_data["weather_description"] = get_weather_code_description(weather_code)
    
    return {
        "success": True,
        "data": {
            "preference": {
                "id": pref.id,
                "city_name": pref.city_name,
                "latitude": pref.latitude,
                "longitude": pref.longitude
            },
            "weather": weather_data,
            "scores": scores
        }
    }


# Historical Data Routes
@app.get("/api/history/{preference_id}")
async def get_history(
    preference_id: int,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get historical scores for a preference."""
    pref = db.query(UserPreference).filter(
        UserPreference.id == preference_id
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    history = db.query(HistoricalScore).filter(
        HistoricalScore.preference_id == preference_id,
        HistoricalScore.date >= start_date
    ).order_by(HistoricalScore.date).all()
    
    return {
        "success": True,
        "data": [
            {
                "date": h.date.isoformat(),
                "laundry_score": h.laundry_score,
                "driving_score": h.driving_score,
                "outdoor_score": h.outdoor_score,
                "irrigation_score": h.irrigation_score,
                "power_risk_score": h.power_risk_score,
                "temperature": h.temperature
            }
            for h in history
        ]
    }


@app.post("/api/history/record")
async def record_daily_scores(db: Session = Depends(get_db)):
    """Record daily scores for all preferences (to be called by scheduler)."""
    preferences = db.query(UserPreference).all()
    recorded = 0
    
    for pref in preferences:
        weather_data = get_weather_data(pref.latitude, pref.longitude)
        if not weather_data:
            continue
        
        current_hour = datetime.now().hour
        is_daytime = 6 <= current_hour <= 18
        scores = calculate_all_scores(weather_data, is_daytime)
        current = weather_data.get("current", {})
        
        # Check if today's record already exists
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        existing = db.query(HistoricalScore).filter(
            HistoricalScore.preference_id == pref.id,
            HistoricalScore.date == today
        ).first()
        
        if existing:
            continue
        
        # Create new record
        record = HistoricalScore(
            preference_id=pref.id,
            date=today,
            temperature=current.get("temperature"),
            humidity=current.get("humidity"),
            wind_speed=current.get("wind_speed"),
            rain_chance=weather_data.get("rain_chance"),
            uv_index=weather_data.get("uv_index"),
            laundry_score=scores["laundry"]["score"],
            driving_score=scores["driving"]["score"],
            outdoor_score=scores["outdoor"]["score"],
            irrigation_score=scores["irrigation"]["score"],
            power_risk_score=scores["power_risk"]["score"]
        )
        db.add(record)
        recorded += 1
    
    db.commit()
    return {"success": True, "recorded": recorded}


# Alert Routes
@app.get("/api/alerts/{preference_id}")
async def get_alerts(
    preference_id: int,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get alert history for a preference."""
    pref = db.query(UserPreference).filter(
        UserPreference.id == preference_id
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    alerts = db.query(AlertLog).filter(
        AlertLog.preference_id == preference_id,
        AlertLog.created_at >= start_date
    ).order_by(AlertLog.created_at.desc()).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "message": a.message,
                "score_value": a.score_value,
                "threshold": a.threshold,
                "is_sent": a.is_sent,
                "sent_at": a.sent_at.isoformat() if a.sent_at else None,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]
    }


@app.post("/api/alerts/check")
async def check_and_create_alerts(db: Session = Depends(get_db)):
    """Check all preferences and create alerts if thresholds are crossed."""
    preferences = db.query(UserPreference).all()
    alerts_created = 0
    
    for pref in preferences:
        weather_data = get_weather_data(pref.latitude, pref.longitude)
        if not weather_data:
            continue
        
        current_hour = datetime.now().hour
        is_daytime = 6 <= current_hour <= 18
        scores = calculate_all_scores(weather_data, is_daytime)
        
        # Check power risk threshold
        power_risk_score = scores["power_risk"]["score"]
        if power_risk_score >= pref.power_risk_threshold:
            # Check if alert was already created recently (within 6 hours)
            recent_alert = db.query(AlertLog).filter(
                AlertLog.preference_id == pref.id,
                AlertLog.alert_type == "power_risk",
                AlertLog.created_at >= datetime.utcnow() - timedelta(hours=6)
            ).first()
            
            if not recent_alert:
                alert = AlertLog(
                    preference_id=pref.id,
                    alert_type="power_risk",
                    message=f"Power cut risk is {power_risk_score}% in {pref.city_name}",
                    score_value=power_risk_score,
                    threshold=pref.power_risk_threshold
                )
                db.add(alert)
                alerts_created += 1
        
        # Check rain alert
        if pref.rain_alert:
            rain_chance = weather_data.get("rain_chance", 0)
            if rain_chance > 70:
                recent_alert = db.query(AlertLog).filter(
                    AlertLog.preference_id == pref.id,
                    AlertLog.alert_type == "rain",
                    AlertLog.created_at >= datetime.utcnow() - timedelta(hours=6)
                ).first()
                
                if not recent_alert:
                    alert = AlertLog(
                        preference_id=pref.id,
                        alert_type="rain",
                        message=f"High rain probability ({rain_chance}%) in {pref.city_name}",
                        score_value=rain_chance,
                        threshold=70
                    )
                    db.add(alert)
                    alerts_created += 1
    
    db.commit()
    return {"success": True, "alerts_created": alerts_created}


@app.post("/api/alerts/{alert_id}/send")
async def send_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as sent (placeholder for actual notification logic)."""
    alert = db.query(AlertLog).filter(AlertLog.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # TODO: Integrate with Telegram/email/SMS here
    alert.is_sent = True
    alert.sent_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Alert marked as sent"}


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)