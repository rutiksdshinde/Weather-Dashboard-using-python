# Weather Dashboard - Complete Project Details

## Project Overview

This is a comprehensive **Weather Dashboard** built specifically for Indian users. It goes beyond basic weather information by providing **actionable activity scores** based on weather conditions.

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Database | SQLite with SQLAlchemy ORM |
| Weather API | Open-Meteo (Free, no API key needed) |
| Frontend | HTML/CSS/JavaScript + Tailwind CSS |
| Charts | Chart.js |

## Key Features

### 1. Real-Time Weather Dashboard
- Current temperature, humidity, wind speed, UV index
- 5-day weather forecast
- Weather icons and descriptions
- Feels-like temperature

### 2. Activity Scoring System (The Unique Feature!)

Five custom scoring algorithms that analyze weather data to provide practical recommendations:

**🧺 Laundry Score (0-100, higher = better)**
- Considers: humidity, rain chance, wind speed, temperature, UV index, daytime
- Helps decide if it's a good day to dry clothes outdoors
- Ideal conditions: Low humidity, no rain, gentle breeze, warm temperature

**🚗 Driving Score (0-100, higher = better)**
- Considers: rain chance, wind speed, temperature, visibility, fog
- Assesses road safety based on weather
- Important for Indian conditions with two-wheelers

**🌤️ Outdoor Activity Score (0-100, higher = better)**
- Considers: temperature, humidity, wind, rain, UV index
- General comfort score for outdoor activities
- Supports specific activities: running, cycling, walking

**💧 Irrigation Score (0-100, higher = better)**
- Considers: temperature, humidity, wind, rain chance, time of day
- Helps farmers and gardeners decide when to water crops
- Best time: early morning with no rain expected

**⚡ Power Cut Risk Score (0-100, higher = HIGHER RISK)**
- Considers: temperature (grid load), thunderstorms, lightning, heavy rain, wind
- Particularly relevant for Indian cities where weather affects power infrastructure
- High temperatures → more AC usage → higher grid load → power cut risk

### 3. City Search & Management
- Search any city worldwide
- Pre-configured for 20+ Indian cities (Mumbai, Delhi, Bangalore, etc.)
- Save favorite cities for quick access
- Set primary city

### 4. Personalization
- Save multiple cities with custom settings
- Set power risk alert thresholds
- Enable/disable rain alerts

### 5. Historical Trends
- View score trends over the last 7-30 days
- Interactive line charts using Chart.js
- Compare this week vs last week

### 6. Alert System
- Automatic threshold checking
- Power risk alerts when threshold is crossed
- Rain alerts for saved cities
- Alert logging in database

## Project Structure

```
weather-dashboard/
├── app.py                  # Main FastAPI application (500+ lines)
├── weather_api.py          # Open-Meteo API integration
├── requirements.txt        # Python dependencies
├── run.bat                # Windows launcher script
├── DETAILS.md             # This file - complete project details
├── README.md              # Full documentation
├── database/
│   ├── __init__.py
│   └── models.py          # 4 database tables
│       ├── UserPreference # Saved cities & settings
│       ├── HistoricalScore # Daily score records
│       ├── AlertLog       # Alert history
│       └── WeatherCache   # API response cache
├── scoring/
│   ├── __init__.py
│   ├── laundry.py         # Laundry score algorithm
│   ├── driving.py         # Driving score algorithm
│   ├── outdoor.py         # Outdoor activity score algorithm
│   ├── irrigation.py      # Irrigation score algorithm
│   └── power_risk.py      # Power cut risk algorithm
├── templates/
│   └── index.html         # Modern responsive frontend
└── static/                # Static assets folder
```

## API Endpoints

### Weather APIs
- `POST /api/search` - Search city by name
- `POST /api/weather` - Get weather & scores for coordinates
- `GET /api/weather/{city_name}` - Get weather by city name

### User Preferences APIs
- `GET /api/preferences` - List saved cities
- `POST /api/preferences` - Save a new city
- `DELETE /api/preferences/{id}` - Delete a city
- `GET /api/preferences/{id}/weather` - Get weather for saved city

### History APIs
- `GET /api/history/{preference_id}` - Get historical scores
- `POST /api/history/record` - Record daily scores (scheduler)

### Alert APIs
- `GET /api/alerts/{preference_id}` - Get alert history
- `POST /api/alerts/check` - Check & create new alerts
- `POST /api/alerts/{alert_id}/send` - Mark alert as sent

## How It Works

1. **User searches for a city** → App looks up coordinates (local dictionary or API)
2. **Fetches weather data** from Open-Meteo API
3. **Caches the data** for 10 minutes to reduce API calls
4. **Calculates all 5 scores** using custom algorithms
5. **Displays results** with color-coded recommendations
6. **Saves to database** if user has saved the city
7. **Checks alerts** against user thresholds

## Scoring Algorithm Example (Laundry)

```python
def calculate_laundry_score(humidity, rain_chance, wind_speed, temperature, uv_index, is_daytime):
    score = 100.0
    
    # High humidity slows evaporation
    humidity_penalty = max(0, (humidity - 30) * 0.6)
    score -= humidity_penalty
    
    # Rain chance is critical
    score -= rain_chance * 0.8
    
    # Wind helps evaporation (up to a point)
    if 5 <= wind_speed <= 15:
        score += 5  # Ideal wind
    elif wind_speed > 30:
        score -= 5  # Too windy
    
    # Temperature helps evaporation
    if temperature >= 25:
        score += 5  # Warm, good for drying
    elif temperature < 10:
        score -= 5  # Cold, slow drying
    
    # Sunlight helps
    if is_daytime and uv_index > 3:
        score += 5
    
    return max(0.0, min(100.0, round(score, 1)))
```

## Database Schema

### UserPreference Table
- `id` - Primary key
- `city_name` - Name of the city
- `latitude`, `longitude` - Coordinates
- `country` - Country name
- `is_primary` - Boolean flag for primary city
- `laundry_priority`, `driving_priority`, `outdoor_priority`, `irrigation_priority`, `power_risk_priority` - Activity priorities (1-5)
- `power_risk_threshold` - Alert threshold for power risk
- `rain_alert` - Boolean for rain alerts
- `created_at`, `updated_at` - Timestamps

### HistoricalScore Table
- `id` - Primary key
- `preference_id` - Foreign key to UserPreference
- `date` - Date of the record
- `temperature`, `humidity`, `wind_speed`, `rain_chance`, `uv_index` - Weather data
- `laundry_score`, `driving_score`, `outdoor_score`, `irrigation_score`, `power_risk_score` - Calculated scores
- `created_at` - Timestamp

### AlertLog Table
- `id` - Primary key
- `preference_id` - Foreign key to UserPreference
- `alert_type` - Type of alert (power_risk, rain)
- `message` - Alert message
- `score_value` - Score that triggered the alert
- `threshold` - Threshold that was crossed
- `is_sent` - Boolean for sent status
- `sent_at`, `created_at` - Timestamps

### WeatherCache Table
- `id` - Primary key
- `latitude`, `longitude` - Coordinates
- `weather_data` - JSON string of cached data
- `cached_at`, `expires_at` - Timestamps

## Pre-configured Indian Cities

The application includes built-in coordinates for these Indian cities:

- Mumbai, Delhi, Bangalore, Chennai, Kolkata
- Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow
- Kochi, Goa, Chandigarh, Indore, Bhopal
- Nagpur, Surat, Vadodara, Coimbatore, Madurai

## Current Status

✅ **Server is running** on http://localhost:8000
✅ **All APIs tested and working**
✅ **Database created** (weather_dashboard.db)
✅ **Frontend accessible** and functional
✅ **Weather data fetching** from Open-Meteo working
✅ **Score calculations** verified

## To Run the Project

1. Open terminal/command prompt
2. Navigate to project: `cd weather-dashboard`
3. Run: `python app.py`
4. Open browser: http://localhost:8000

Or simply double-click `run.bat` in the weather-dashboard folder.

## Why This Project is Portfolio-Worthy

1. **Original Data Engineering**: Custom composite scoring algorithms, not just API wrapper
2. **Real Problem Solving**: Addresses local Indian challenges (power cuts, laundry, irrigation)
3. **Full Stack Development**: Backend API, database, frontend UI
4. **Extensible Architecture**: Easy to add new scoring functions or cities
5. **Production Ready**: Caching, error handling, database persistence
6. **Monetization Potential**: Could be a niche tool for farmers or general users

## Future Enhancements

1. **Telegram Bot Integration**: Send alerts via Telegram
2. **Email Notifications**: Email alerts for saved cities
3. **SMS Alerts**: SMS notifications for critical weather events
4. **Mobile App**: React Native or Flutter mobile application
5. **Advanced Analytics**: Machine learning for better predictions
6. **Multi-language Support**: Support for Hindi and other Indian languages
7. **Air Quality Index**: Add AQI data and health recommendations
8. **Agricultural Insights**: Crop-specific recommendations for farmers

## Deployment Options

- **Docker**: Containerize the application
- **Cloud Platforms**: Deploy to AWS, Google Cloud, Azure, or Heroku
- **VPS**: Deploy to a virtual private server with Nginx + Gunicorn

---

**Built with ❤️ for Indian users by considering local weather challenges and needs.**