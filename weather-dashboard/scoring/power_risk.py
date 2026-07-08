"""
Power Cut Risk Score Calculator
Estimates the likelihood of power outages based on weather conditions
Particularly relevant for Indian cities where weather affects power infrastructure
Score: 0-100 (higher means HIGHER RISK of power cut)
"""

def calculate_power_risk_score(
    temperature: float,
    humidity: float,
    wind_speed: float,
    rain_chance: float,
    has_thunderstorm: bool = False,
    has_lightning: bool = False,
    time_of_day: str = "day"
) -> float:
    """
    Calculate power cut risk score based on weather conditions.
    
    This is particularly relevant for Indian cities where:
    - High temperatures increase load on the grid (AC usage)
    - Thunderstorms and lightning can damage infrastructure
    - Heavy rain can flood substations
    - High winds can bring down power lines
    
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity percentage (0-100)
        wind_speed: Wind speed in km/h
        rain_chance: Probability of rain percentage (0-100)
        has_thunderstorm: Whether thunderstorm is forecast
        has_lightning: Whether lightning is forecast
        time_of_day: "day" or "night" (affects load patterns)
    
    Returns:
        Score from 0-100 (higher means higher risk of power cut)
    """
    # Start with low risk
    score = 0.0
    
    # High temperatures increase grid load dramatically
    # Above 35°C, AC usage spikes
    if temperature > 40:
        score += 30  # Extreme heat, very high load
    elif temperature > 35:
        score += 20  # High heat, high load
    elif temperature > 30:
        score += 10  # Warm, moderate load increase
    elif temperature > 25:
        score += 5   # Slight load increase
    
    # High humidity combined with heat makes it worse
    if temperature > 30 and humidity > 70:
        score += 10  # Heat index effect, more AC usage
    
    # Thunderstorms are a major risk factor
    if has_thunderstorm:
        score += 25  # Can cause immediate outages
    
    # Lightning is extremely dangerous for power infrastructure
    if has_lightning:
        score += 20  # Can damage transformers, substations
    
    # Heavy rain can flood equipment
    if rain_chance > 80:
        score += 15  # Risk of flooding
    elif rain_chance > 50:
        score += 8
    
    # High winds can bring down lines
    if wind_speed > 60:
        score += 20  # Very dangerous for power lines
    elif wind_speed > 40:
        score += 10
    elif wind_speed > 25:
        score += 5
    
    # Night time peak hours (7-10 PM) have higher baseline load
    if time_of_day == "evening":
        score += 5  # Peak load time
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, round(score, 1)))


def get_power_risk_recommendation(score: float) -> dict:
    """
    Get a human-readable recommendation based on the power risk score.
    
    Returns:
        Dictionary with recommendation details
    """
    if score >= 70:
        return {
            "score": score,
            "status": "very_high",
            "icon": "🚨",
            "message": "Very high power cut risk! Charge devices, save work.",
            "color": "#ef4444",
            "advice": [
                "Charge all devices immediately",
                "Save your work and close applications",
                "Keep refrigerator doors closed",
                "Have flashlights ready"
            ]
        }
    elif score >= 50:
        return {
            "score": score,
            "status": "high",
            "icon": "⚠️",
            "message": "High power cut risk. Be prepared.",
            "color": "#f97316",
            "advice": [
                "Consider charging devices",
                "Save important work periodically",
                "Keep UPS/inverter ready"
            ]
        }
    elif score >= 30:
        return {
            "score": score,
            "status": "moderate",
            "icon": "📊",
            "message": "Moderate power cut risk. Normal precautions.",
            "color": "#f59e0b",
            "advice": [
                "Normal precautions are sufficient",
                "Keep devices charged as usual"
            ]
        }
    elif score >= 10:
        return {
            "score": score,
            "status": "low",
            "icon": "✅",
            "message": "Low power cut risk. Stable power expected.",
            "color": "#84cc16",
            "advice": []
        }
    else:
        return {
            "score": score,
            "status": "very_low",
            "icon": "⚡",
            "message": "Very low power cut risk. Excellent stability.",
            "color": "#22c55e",
            "advice": []
        }