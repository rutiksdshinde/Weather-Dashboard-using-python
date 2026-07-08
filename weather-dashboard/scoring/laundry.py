"""
Laundry Score Calculator
Determines how good the weather is for drying clothes outdoors
Score: 0-100 (higher is better)
"""

def calculate_laundry_score(
    humidity: float,
    rain_chance: float,
    wind_speed: float,
    temperature: float,
    uv_index: float = 0,
    is_daytime: bool = True
) -> float:
    """
    Calculate laundry drying score based on weather conditions.
    
    Args:
        humidity: Relative humidity percentage (0-100)
        rain_chance: Probability of rain percentage (0-100)
        wind_speed: Wind speed in km/h
        temperature: Temperature in Celsius
        uv_index: UV index (0-11+)
        is_daytime: Whether it's daytime (sun helps drying)
    
    Returns:
        Score from 0-100 (higher is better for drying clothes)
    """
    # Start with a perfect score
    score = 100.0
    
    # High humidity slows evaporation significantly
    # Humidity above 70% is bad, below 40% is great
    humidity_penalty = max(0, (humidity - 30) * 0.6)
    score -= humidity_penalty
    
    # Rain chance is critical - clothes will get wet
    score -= rain_chance * 0.8
    
    # Wind helps evaporation (up to a point)
    # Gentle breeze (5-15 km/h) is ideal
    if wind_speed < 5:
        score -= (5 - wind_speed) * 1.5  # Not enough wind
    elif wind_speed <= 15:
        score += 5  # Ideal wind
    elif wind_speed <= 30:
        score += 2  # Good but strong
    else:
        score -= 5  # Too windy, clothes might blow away
    
    # Temperature helps evaporation
    if temperature >= 25:
        score += 5  # Warm, good for drying
    elif temperature >= 15:
        score += 2  # Moderate
    elif temperature < 10:
        score -= 5  # Cold, slow drying
    
    # UV/Sunlight helps drying and disinfects
    if is_daytime and uv_index > 3:
        score += 5
    elif not is_daytime:
        score -= 10  # Night drying is slower
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, round(score, 1)))


def get_laundry_recommendation(score: float) -> dict:
    """
    Get a human-readable recommendation based on the laundry score.
    
    Returns:
        Dictionary with recommendation details
    """
    if score >= 80:
        return {
            "score": score,
            "status": "excellent",
            "icon": "✅",
            "message": "Excellent day for drying clothes outdoors!",
            "color": "#22c55e"
        }
    elif score >= 60:
        return {
            "score": score,
            "status": "good",
            "icon": "👍",
            "message": "Good conditions for outdoor drying.",
            "color": "#84cc16"
        }
    elif score >= 40:
        return {
            "score": score,
            "status": "moderate",
            "icon": "⚠️",
            "message": "Moderate conditions. Consider covered area.",
            "color": "#f59e0b"
        }
    elif score >= 20:
        return {
            "score": score,
            "status": "poor",
            "icon": "😕",
            "message": "Poor drying conditions. Use indoor drying.",
            "color": "#f97316"
        }
    else:
        return {
            "score": score,
            "status": "very_poor",
            "icon": "❌",
            "message": "Not recommended for outdoor drying today.",
            "color": "#ef4444"
        }