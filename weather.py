#!/usr/bin/env python3
"""
Fetch current weather for a given city using OpenWeatherMap API.

Usage:
    weather.py [city]
If no city is given, prompt interactively.
The API key must be provided in the environment variable OPENWEATHER_API_KEY.
"""

import os
import sys
import requests
from datetime import datetime, timezone

API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
UNITS = "metric"  # Celsius


class WeatherError(Exception):
    """Custom exception for weather script errors."""
    pass


def get_api_key():
    """Retrieve API key from environment variable.

    Raises:
        WeatherError: If the environment variable is not set.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise WeatherError("OPENWEATHER_API_KEY environment variable not set.")
    return api_key


def fetch_weather(city, api_key):
    """
    Call OpenWeatherMap API and return weather data.

    Args:
        city (str): City name.
        api_key (str): API key.

    Returns:
        dict: Parsed JSON response.

    Raises:
        WeatherError: On invalid input, HTTP errors, connection issues,
            timeout, or invalid JSON response.
    """
    # Basic input validation to avoid empty requests
    if not city.strip():
        raise WeatherError("City name cannot be empty.")

    params = {
        "q": city,
        "appid": api_key,
        "units": UNITS,
    }
    try:
        response = requests.get(API_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code
        if status_code == 404:
            raise WeatherError(f"City '{city}' not found.")
        elif status_code == 401:
            raise WeatherError("Invalid API key. Please check your OPENWEATHER_API_KEY.")
        else:
            raise WeatherError(f"HTTP error: {http_err}")
    except requests.exceptions.ConnectionError:
        raise WeatherError("Could not connect to the weather service. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise WeatherError("Request timed out. Please try again later.")
    except requests.exceptions.RequestException as err:
        raise WeatherError(f"An unexpected network error occurred: {err}")

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise WeatherError("Invalid JSON response from API.")
    return data


def display_weather(data):
    """Pretty-print weather information."""
    city = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")
    weather = data.get("weather", [{}])[0]
    description = weather.get("description", "N/A")
    temp = data.get("main", {}).get("temp")
    feels_like = data.get("main", {}).get("feels_like")
    humidity = data.get("main", {}).get("humidity")
    pressure = data.get("main", {}).get("pressure")
    wind_speed = data.get("wind", {}).get("speed")
    dt = data.get("dt")
    if dt:
        # datetime.utcfromtimestamp is deprecated, use timezone-aware approach
        dt_str = datetime.fromtimestamp(dt, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    else:
        dt_str = "N/A"

    # Format output
    location = f"{city}, {country}" if country else city
    width = 40
    divider = "=" * width

    print(divider)
    print(f"  Weather for {location}")
    print(f"  Last updated: {dt_str}")
    print(divider)
    print(f"  Condition   : {description.capitalize()}")
    if temp is not None:
        print(f"  Temperature : {temp:.1f}\u00b0C")
    if feels_like is not None:
        print(f"  Feels like  : {feels_like:.1f}\u00b0C")
    if humidity is not None:
        print(f"  Humidity    : {humidity}%")
    if pressure is not None:
        print(f"  Pressure    : {pressure} hPa")
    if wind_speed is not None:
        print(f"  Wind Speed  : {wind_speed} m/s")
    print(divider)


def main():
    """Run the script."""
    # Get city from command-line argument or prompt
    if len(sys.argv) > 1:
        city = " ".join(sys.argv[1:]).strip()
    else:
        try:
            city = input("Enter city name: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.", file=sys.stderr)
            sys.exit(0)

    if not city:
        print("Error: No city provided.", file=sys.stderr)
        sys.exit(1)

    try:
        api_key = get_api_key()
        data = fetch_weather(city, api_key)
        display_weather(data)
    except WeatherError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()