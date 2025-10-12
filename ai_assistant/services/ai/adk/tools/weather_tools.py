from typing import Any


async def get_weather(location: str) -> dict[str, Any]:
    """
    Get weather information for a given location.

    Args:
        location (str): City name or location string

    Returns:
        dict[str, Any]: Weather information
    """
    # TODO: Implement actual weather API (e.g., OpenWeatherMap, WeatherAPI)
    return {
        'location': location,
        'temperature': 22,
        'unit': 'celsius',
        'condition': 'Sunny',
        'humidity': 65,
        'wind_speed': 10,
        'note': 'Mock data - implement real weather API',
    }
