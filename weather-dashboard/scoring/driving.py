"""
Driving Score Calculator
Determines how safe and comfortable the weather is for driving
Score: 0-100 (higher is better)
"""

def calculate_driving_score(
    rain_chance: float,
    wind_speed: float,
    temperature: float,
    visibility: float = 10,
    is_daytime: bool = True,
    has_fog: bool = False
) -> float:
    """
    Calculate driving safety score based on weather conditions.
    
    Args:
        rain_chance: Probability of rain percentage (0-100)
        wind_speed: Wind speed in km/h
        temperature: Temperature in Celsius
        visibility: Visibility in km (default 10 = good)
        is_daytime: Whether it's daytime
        has_fog: Whether fog is present
    
    Returns:
        Score from 0-100 (higher is better for driving)
    """
    # Start with a perfect score
    score = 100.0
    
    # Rain significantly affects driving safety
    # Heavy rain chance reduces visibility and road grip
    if rain_chance > 70:
        score -= 30  # Heavy rain risk
    elif rain_chance > 40:
        score -= 15  # Moderate rain risk
    elif rain_chance > 20:
        score -= 5   # Light rain risk
    
    # Wind affects vehicle stability, especially for two-wheelers
    if wind_speed > 50:
        score -= 25  # Dangerous crosswinds
    elif wind_speed > 30:
        score -= 15  # Strong crosswinds
    elif wind_speed > 20:
        score -= 5   # Moderate wind
    
    # Temperature extremes can affect vehicle performance
    if temperature > 40:
        score -= 10  # Risk of overheating
    elif temperature < 0:
        score -= 15  # Ice risk, engine issues
    
    # Visibility is critical for safety
    if visibility < 1:
        score -= 40  # Very dangerous
    elif visibility < 3:
        score -= 25  # Poor visibility
    elif visibility < 5:
        score -= 10  # Reduced visibility
    
    # Fog is extremely dangerous
    if has_fog:
        score -= 30
    
    # Night driving is inherently more risky
    if not is_daytime:
        score -= 5
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, round(score, 1)))


def get_driving_recommendation(score: float) -> dict:
    """
    Get a human-readable recommendation based on the driving score.
    
    Returns:
        Dictionary with recommendation details
    """
    if score >= 85:
        return {
            "score": score,
            "status": "excellent",
            "icon": "🚗",
            "message": "Excellent driving conditions!",
            "color": "#22c55e"
        }
    elif score >= 70:
        return {
            "score": score,
            "status": "good",
            "icon": "👍",
            "message": "Good driving conditions. Stay alert.",
            "color": "#84cc16"
        }
    elif score >= 50:
        return {
            "score": score,
            "status": "moderate",
            "icon": "⚠️",
            "message": "Moderate conditions. Drive carefully.",
            "color": "#f59e0b"
        }
    elif score >= 30:
        return {
            "score": score,
            "status": "poor",
            "icon": "🚨",
            "message": "Poor driving conditions. Consider delaying.",
            "color": "#f97316"
        }
    else:
        return {
            "score": score,
            "status": "dangerous",
            "icon": "❌",
            "message": "Dangerous driving conditions! Avoid travel.",
            "color": "#ef4444"
        }