"""
Outdoor Activity Score Calculator
Determines how comfortable the weather is for outdoor activities
Score: 0-100 (higher is better)
"""

def calculate_outdoor_score(
    temperature: float,
    humidity: float,
    wind_speed: float,
    rain_chance: float,
    uv_index: float = 0,
    is_daytime: bool = True,
    activity_type: str = "general"
) -> float:
    """
    Calculate outdoor activity comfort score based on weather conditions.
    
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity percentage (0-100)
        wind_speed: Wind speed in km/h
        rain_chance: Probability of rain percentage (0-100)
        uv_index: UV index (0-11+)
        is_daytime: Whether it's daytime
        activity_type: Type of activity (general, running, cycling, walking)
    
    Returns:
        Score from 0-100 (higher is better for outdoor activities)
    """
    # Start with a perfect score
    score = 100.0
    
    # Temperature comfort zone (15-25°C is ideal for most activities)
    if 15 <= temperature <= 25:
        score += 5  # Ideal temperature
    elif 10 <= temperature < 15 or 25 < temperature <= 30:
        pass  # Acceptable
    elif temperature > 35:
        score -= 20  # Too hot, heat stress risk
    elif temperature < 5:
        score -= 15  # Too cold
    
    # Humidity affects comfort (40-60% is ideal)
    if 40 <= humidity <= 60:
        score += 3  # Ideal humidity
    elif humidity > 80:
        score -= 15  # Too humid, sticky feeling
    elif humidity < 20:
        score -= 5   # Too dry
    
    # Heat index consideration (temperature + humidity)
    if temperature > 30 and humidity > 60:
        heat_index_penalty = (temperature - 30) * (humidity - 60) * 0.02
        score -= min(heat_index_penalty, 20)
    
    # Wind comfort
    if wind_speed < 5:
        score += 2  # Calm, pleasant
    elif wind_speed > 30:
        score -= 10  # Too windy
    elif wind_speed > 20:
        score -= 5   # Moderately windy
    
    # Rain is generally bad for outdoor activities
    if rain_chance > 50:
        score -= 25
    elif rain_chance > 20:
        score -= 10
    
    # UV protection needed
    if uv_index > 8:
        score -= 15  # Very high UV, dangerous
    elif uv_index > 5:
        score -= 5   # Moderate UV, use sunscreen
    elif uv_index > 3 and is_daytime:
        score += 2   # Good for vitamin D
    
    # Night activities have different considerations
    if not is_daytime:
        score -= 5  # Reduced visibility
        if temperature < 10:
            score -= 5  # Cold night
    
    # Activity-specific adjustments
    if activity_type == "running":
        # Runners prefer cooler temperatures
        if temperature > 20:
            score -= (temperature - 20) * 0.5
        if humidity > 70:
            score -= 10  # Harder to cool down
    elif activity_type == "cycling":
        # Cyclists are more affected by wind
        if wind_speed > 15:
            score -= (wind_speed - 15) * 0.5
    elif activity_type == "walking":
        # Walking is more tolerant
        pass
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, round(score, 1)))


def get_outdoor_recommendation(score: float, activity_type: str = "general") -> dict:
    """
    Get a human-readable recommendation based on the outdoor score.
    
    Returns:
        Dictionary with recommendation details
    """
    activity_emoji = {
        "general": "🌤️",
        "running": "🏃",
        "cycling": "🚴",
        "walking": "🚶"
    }
    
    emoji = activity_emoji.get(activity_type, "🌤️")
    
    if score >= 80:
        return {
            "score": score,
            "status": "excellent",
            "icon": emoji,
            "message": f"Excellent weather for {activity_type}!",
            "color": "#22c55e"
        }
    elif score >= 60:
        return {
            "score": score,
            "status": "good",
            "icon": "👍",
            "message": f"Good conditions for {activity_type}.",
            "color": "#84cc16"
        }
    elif score >= 40:
        return {
            "score": score,
            "status": "moderate",
            "icon": "⚠️",
            "message": f"Moderate conditions. Take precautions.",
            "color": "#f59e0b"
        }
    elif score >= 20:
        return {
            "score": score,
            "status": "poor",
            "icon": "😕",
            "message": f"Poor conditions for {activity_type}.",
            "color": "#f97316"
        }
    else:
        return {
            "score": score,
            "status": "very_poor",
            "icon": "❌",
            "message": f"Not recommended for {activity_type} today.",
            "color": "#ef4444"
        }