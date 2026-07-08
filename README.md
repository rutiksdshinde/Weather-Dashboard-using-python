# Weather Dashboard - India

A comprehensive weather dashboard with activity scoring specifically designed for Indian users. This application goes beyond basic weather information by providing actionable insights for daily activities based on weather conditions.

## Links
- **Portfolio:** https://prismatic-alpaca-376b6f.netlify.app
- **LinkedIn:** https://www.linkedin.com/in/rutik-shinde-09a438237
- **GitHub:** https://github.com/rutiksdshinde

## Features

### Core Features
- **Real-time Weather Data**: Current weather, 5-day forecast, and hourly updates
- **Activity Scoring System**: Unique scoring algorithms for:
  - 🧺 **Laundry Score**: Best conditions for drying clothes outdoors
  - 🚗 **Driving Score**: Road safety assessment based on weather
  - 🌤️ **Outdoor Activity Score**: Comfort level for outdoor activities
  - 💧 **Irrigation Score**: Optimal timing for watering plants/crops
  - ⚡ **Power Cut Risk**: Likelihood of power outages (especially relevant for Indian cities)

### Advanced Features
- **City Search**: Search any city worldwide with special optimization for Indian cities
- **Saved Cities**: Save and manage multiple cities for quick access
- **Historical Trends**: View score trends over time with interactive charts
- **Alert System**: Get notified when thresholds are crossed (power risk, heavy rain)
- **Smart Caching**: 10-minute cache to reduce API calls and improve performance

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Weather API**: Open-Meteo (free, no API key required)
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS
- **Charts**: Chart.js for trend visualizations
- **Styling**: Tailwind CSS (via CDN)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd weather-dashboard
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:8000`

## Project Structure

```
weather-dashboard/
├── app.py                  # Main FastAPI application
├── weather_api.py          # Open-Meteo API integration
├── requirements.txt        # Python dependencies
├── database/
│   ├── __init__.py
│   └── models.py          # SQLAlchemy database models
├── scoring/
│   ├── __init__.py
│   ├── laundry.py         # Laundry score calculator
│   ├── driving.py         # Driving score calculator
│   ├── outdoor.py         # Outdoor activity score calculator
│   ├── irrigation.py      # Irrigation score calculator
│   └── power_risk.py      # Power cut risk calculator
├── templates/
│   └── index.html         # Main dashboard HTML template
└── static/                # Static assets (CSS, JS, images)
```

## API Endpoints

### Weather Endpoints
- `POST /api/search` - Search for a city
- `POST /api/weather` - Get weather and scores for coordinates
- `GET /api/weather/{city_name}` - Get weather by city name

### User Preferences
- `GET /api/preferences` - List saved cities
- `POST /api/preferences` - Save a new city
- `DELETE /api/preferences/{id}` - Delete a saved city
- `GET /api/preferences/{id}/weather` - Get weather for a saved city

### Historical Data
- `GET /api/history/{preference_id}` - Get historical scores
- `POST /api/history/record` - Record daily scores (scheduler task)

### Alerts
- `GET /api/alerts/{preference_id}` - Get alert history
- `POST /api/alerts/check` - Check and create new alerts
- `POST /api/alerts/{alert_id}/send` - Mark alert as sent

## Scoring Algorithms

### Laundry Score (0-100, higher is better)
Considers: humidity, rain chance, wind speed, temperature, UV index, daytime
- Ideal: Low humidity, no rain, gentle breeze, warm temperature, sunny

### Driving Score (0-100, higher is better)
Considers: rain chance, wind speed, temperature, visibility, fog, daytime
- Ideal: Clear weather, good visibility, moderate temperature, no wind

### Outdoor Activity Score (0-100, higher is better)
Considers: temperature, humidity, wind speed, rain chance, UV index
- Ideal: 15-25°C, 40-60% humidity, light wind, no rain, moderate UV

### Irrigation Score (0-100, higher is better)
Considers: temperature, humidity, wind speed, rain chance, time of day
- Ideal: Cool morning, no rain expected, low wind, moderate humidity

### Power Cut Risk Score (0-100, higher means HIGHER RISK)
Considers: temperature, humidity, wind speed, rain chance, thunderstorms, lightning
- Risk factors: Extreme heat (high grid load), thunderstorms, heavy rain, high winds

## Customization

### Adding New Scoring Functions
1. Create a new Python file in the `scoring/` directory
2. Implement a `calculate_*_score()` function
3. Implement a `get_*_recommendation()` function
4. Import and integrate in `app.py`

### Modifying Alert Thresholds
Users can set custom thresholds through the preferences system:
- Power risk threshold (default: 70%)
- Rain alert toggle

### Extending for Specific Regions
The `weather_api.py` includes a dictionary of Indian cities. Add more cities:
```python
INDIAN_CITIES = {
    "cityname": {"lat": 00.0000, "lon": 00.0000},
    # Add more cities...
}
```

## Deployment

### Production Considerations

1. **Database**: Switch from SQLite to PostgreSQL for production
2. **Environment Variables**: Use `.env` file for sensitive configuration
3. **Background Jobs**: Use Celery or APScheduler for alert checking
4. **Caching**: Implement Redis for better caching performance
5. **HTTPS**: Always use HTTPS in production
6. **Rate Limiting**: Add rate limiting to prevent API abuse

### Deployment Options
- **Docker**: Containerize the application
- **Cloud Platforms**: Deploy to AWS, Google Cloud, Azure, or Heroku
- **VPS**: Deploy to a virtual private server with Nginx + Gunicorn

## Future Enhancements

1. **Telegram Bot Integration**: Send alerts via Telegram
2. **Email Notifications**: Email alerts for saved cities
3. **SMS Alerts**: SMS notifications for critical weather events
4. **Mobile App**: React Native or Flutter mobile application
5. **Advanced Analytics**: Machine learning for better predictions
6. **Multi-language Support**: Support for Hindi and other Indian languages
7. **Air Quality Index**: Add AQI data and health recommendations
8. **Agricultural Insights**: Crop-specific recommendations for farmers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available for educational and commercial use.

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check existing documentation
- Review the API endpoints for integration possibilities

## Acknowledgments

- **Open-Meteo**: For providing free, accurate weather data
- **FastAPI**: For the excellent web framework
- **Tailwind CSS**: For the beautiful UI components
- **Chart.js**: For the interactive charts

---

**Built with ❤️ for Indian users by considering local weather challenges and needs.**
