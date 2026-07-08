"""
Weather API Integration using Open-Meteo
Open-Meteo is free, requires no API key, and provides excellent coverage for India
"""
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json


# Open-Meteo API endpoints
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Common Indian cities with their coordinates for quick lookup
INDIAN_CITIES = {
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "delhi": {"lat": 28.6139, "lon": 77.2090},
    "bangalore": {"lat": 12.9716, "lon": 77.5946},
    "chennai": {"lat": 13.0827, "lon": 80.2707},
    "kolkata": {"lat": 22.5726, "lon": 88.3639},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "pune": {"lat": 18.5204, "lon": 73.8567},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "jaipur": {"lat": 26.9124, "lon": 75.7873},
    "lucknow": {"lat": 26.8467, "lon": 80.9462},
    "kochi": {"lat": 9.9312, "lon": 76.2673},
    "goa": {"lat": 15.2993, "lon": 74.1240},
    "chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "indore": {"lat": 22.7196, "lon": 75.8577},
    "bhopal": {"lat": 23.2599, "lon": 77.4126},
    "nagpur": {"lat": 21.1458, "lon": 79.0882},
    "surat": {"lat": 21.1702, "lon": 72.8311},
    "vadodara": {"lat": 22.3072, "lon": 73.1812},
    "coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "madurai": {"lat": 9.9252, "lon": 78.1198},
}


def search_city(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Search for a city and return its coordinates.
    First checks the local Indian cities dictionary, then uses the API.
    
    Args:
        city_name: Name of the city to search
    
    Returns:
        Dictionary with city info including lat, lon, name, country
    """
    # Check local dictionary first (faster, works offline for known cities)
    city_lower = city_name.lower().strip()
    if city_lower in INDIAN_CITIES:
        city_data = INDIAN_CITIES[city_lower]
        return {
            "name": city_name.title(),
            "latitude": city_data["lat"],
            "longitude": city_data["lon"],
            "country": "India"
        }
    
    # Use Open-Meteo geocoding API
    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                result = data["results"][0]
                return {
                    "name": result.get("name"),
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "country": result.get("country_code"),
                    "admin1": result.get("admin1")  # State/region
                }
    except requests.RequestException as e:
        print(f"Geocoding error: {e}")
    
    return None


def get_weather_data(
    latitude: float,
    longitude: float,
    days: int = 5
) -> Optional[Dict[str, Any]]:
    """
    Fetch weather data from Open-Meteo API.
    
    Args:
        latitude: City latitude
        longitude: City longitude
        days: Number of forecast days (1-16)
    
    Returns:
        Dictionary with current weather and forecast data
    """
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "surface_pressure",
                "precipitation"
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "precipitation_probability",
                "precipitation"
            ],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "sunrise",
                "sunset",
                "precipitation_sum",
                "precipitation_probability_max",
                "uv_index_max",
                "wind_speed_10m_max"
            ],
            "timezone": "auto",
            "forecast_days": min(days, 16)
        }
        
        response = requests.get(WEATHER_URL, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return parse_weather_response(data)
        else:
            print(f"API error: {response.status_code}")
            return None
            
    except requests.RequestException as e:
        print(f"Weather API error: {e}")
        return None


def parse_weather_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the Open-Meteo API response into a cleaner format.
    
    Args:
        data: Raw API response
    
    Returns:
        Parsed weather data dictionary
    """
    current = data.get("current", {})
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})
    
    # Get current hour index for today's hourly data
    current_time = datetime.now()
    current_hour = current_time.hour
    
    # Calculate rain chance from hourly data
    rain_chance = 0
    if hourly.get("precipitation_probability"):
        # Average precipitation probability for next 6 hours
        next_6_hours = hourly["precipitation_probability"][current_hour:current_hour+6]
        if next_6_hours:
            rain_chance = sum(next_6_hours) / len(next_6_hours)
    
    # Get today's UV index
    uv_index = 0
    if daily.get("uv_index_max") and daily["uv_index_max"]:
        uv_index = daily["uv_index_max"][0] if daily["uv_index_max"][0] else 0
    
    # Check for thunderstorm/lightning (weather codes 95, 96, 99)
    weather_code = current.get("weather_code", 0)
    has_thunderstorm = weather_code in [95, 96, 99]
    has_lightning = weather_code in [95, 99]
    
    # Parse daily forecasts
    daily_forecasts = []
    if daily.get("time"):
        for i, date in enumerate(daily["time"]):
            daily_forecasts.append({
                "date": date,
                "temp_max": daily["temperature_2m_max"][i] if daily.get("temperature_2m_max") else None,
                "temp_min": daily["temperature_2m_min"][i] if daily.get("temperature_2m_min") else None,
                "weather_code": daily["weather_code"][i] if daily.get("weather_code") else None,
                "rain_chance": daily["precipitation_probability_max"][i] if daily.get("precipitation_probability_max") else 0,
                "uv_index": daily["uv_index_max"][i] if daily.get("uv_index_max") else 0,
                "sunrise": daily["sunrise"][i] if daily.get("sunrise") else None,
                "sunset": daily["sunset"][i] if daily.get("sunset") else None,
                "wind_speed_max": daily["wind_speed_10m_max"][i] if daily.get("wind_speed_10m_max") else 0
            })
    
    return {
        "current": {
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "weather_code": weather_code,
            "wind_speed": current.get("wind_speed_10m"),
            "wind_direction": current.get("wind_direction_10m"),
            "pressure": current.get("surface_pressure"),
            "precipitation": current.get("precipitation", 0),
            "time": current.get("time")
        },
        "rain_chance": round(rain_chance, 1),
        "uv_index": round(uv_index, 1),
        "has_thunderstorm": has_thunderstorm,
        "has_lightning": has_lightning,
        "daily_forecasts": daily_forecasts,
        "hourly_forecast": hourly
    }


def get_weather_code_description(code: int) -> str:
    """
    Get human-readable weather description from WMO code.
    """
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return codes.get(code, "Unknown")