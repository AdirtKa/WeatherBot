from config_reader import config
import aiohttp

from typing import TypedDict


class User(TypedDict):
    name: str
    locations: list[tuple[float, float]]
    is_checking: bool


class Weather:
    API_TOKEN: str = config.weather_token.get_secret_value()
    url: str = "https://api.gismeteo.net/v2/weather/current/?latitude={}&longitude={}"

    @staticmethod
    async def __fetch_weather(location: tuple[float, float]) -> str:
        async with aiohttp.ClientSession() as session:
            header = {
                "X-Gismeteo-Token": Weather.API_TOKEN
            }
            url = Weather.url.format(*location)
            async with session.get(url, headers=header) as response:
                data = await response.json()

        return data["response"]["description"]["full"]

    @staticmethod
    async def __int_weather_to_string(weather_id: int) -> str:
        pass

    @staticmethod
    async def get_weather(location: tuple[float, float]) -> str:
        # weather_id = await Weather.__fetch_weather(location)
        # weather = await Weather.__int_weather_to_string(weather_id)
        weather = await Weather.__fetch_weather(location)
        print(weather)
        return weather


if __name__ == '__main__':
    pass
