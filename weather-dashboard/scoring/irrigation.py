"""
Irrigation Score Calculator
Determines optimal conditions for watering plants/crops
Score: 0-100 (higher is better for irrigation)
"""

def calculate_irrigation_score(
    temperature: float,
    humidity: float,
    wind_speed: float,
    rain_chance: float,
    has_rain: bool = False,
    time_of_day: str = "morning"
) -> float:
    """
    Calculate irrigation suitability score based on weather conditions.
    
    This is particularly useful for farmers and gardeners to determine
    the best time to water crops or plants.
    
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity percentage (0-100)
        wind_speed: Wind speed in km/h
        rain_chance: Probability of rain percentage (0-100)
        has_rain: Whether it's currently raining
        time_of_day: Time category (morning, afternoon, evening, night)
    
    Returns:
        Score from 0-100 (higher is better for irrigation)
    """
    # Start with a good baseline score
    score = 100.0
    
    # If it's already raining, irrigation is unnecessary
    if has_rain:
        return 0.0
    
    # High rain chance means we should wait
    if rain_chance > 70:
        score -= 50  # Very likely to rain, don't irrigate
    elif rain_chance > 40:
        score -= 30  # Might rain soon
    elif rain_chance > 20:
        score -= 15  # Slight chance
    
    # Temperature affects evaporation rate
    # Very hot temperatures cause rapid evaporation (wasteful)
    if temperature > 35:
        score -= 20  # Too hot, water evaporates quickly
    elif temperature > 30:
        score -= 10
    elif temperature < 5:
        score -= 10  # Too cold, water may freeze or not absorb well
    
    # High humidity reduces evaporation (good for irrigation)
    if humidity < 30:
        score += 5   # Low humidity, water will be absorbed quickly
    elif humidity > 80:
        score -= 5   # Very high humidity, plants may get fungal issues
    
    # Wind causes uneven water distribution and evaporation
    if wind_speed > 25:
        score -= 20  # Too windy, water drifts away
    elif wind_speed > 15:
        score -= 10
    elif wind_speed > 10:
        score -= 5
    
    # Time of day matters significantly
    # Early morning is best (less evaporation, plants absorb before heat)
    if time_of_day == "morning":
        score += 10  # Best time
    elif time_of_day == "evening":
        score += 5   # Second best (but can promote fungal growth)
    elif time_of_day == "afternoon":
        score -= 15  # Worst time (high evaporation)
    elif time_of_day == "night":
        score -= 5   # Can promote fungal diseases
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, round(score, 1)))


def get_irrigation_recommendation(score: float) -> dict:
    """
    Get a human-readable recommendation based on the irrigation score.
    
    Returns:
        Dictionary with recommendation details
    """
    if score >= 80:
        return {
            "score": score,
            "status": "excellent",
            "icon": "💧",
            "message": "Excellent time for irrigation!",
            "color": "#22c55e"
        }
    elif score >= 60:
        return {
            "score": score,
            "status": "good",
            "icon": "🌱",
            "message": "Good conditions for watering plants.",
            "color": "#84cc16"
        }
    elif score >= 40:
        return {
            "score": score,
            "status": "moderate",
            "icon": "⚠️",
            "message": "Moderate conditions. Consider waiting.",
            "color": "#f59e0b"
        }
    elif score >= 20:
        return {
            "score": score,
            "status": "poor",
            "icon": "🌧️",
            "message": "Poor time for irrigation. Rain likely.",
            "color": "#f97316"
        }
    else:
        return {
            "score": score,
            "status": "not_recommended",
            "icon": "❌",
            "message": "Do not irrigate. It's raining or about to rain.",
            "color": "#ef4444"
        }