import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def get_weather(location: str) -> dict[str, Any]:
    """
    Get weather information for a given location.

    Args:
        location (str): City name or location string

    Returns:
        dict[str, Any]: Weather information
    """
    # Artificial delay to simulate API call
    logger.info(f'Fetching weather for {location}...')
    await asyncio.sleep(2)  # 2 second delay
    logger.info(f'Weather data retrieved for {location}')

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
