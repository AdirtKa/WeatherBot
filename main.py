from random import choice

from SomeClasses import Weather
from config_reader import config
import Users

import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

users = Users.users
bot = Bot(token=config.bot_token.get_secret_value())
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
base_router = Router()


async def process_users():
    global users
    sleep_time_in_seconds: int = 300
    while True:
        for chat_id, user in users.items():
            if not user["is_checking"]:
                continue

            weather: str = await process_locations(user["locations"])
            await bot.send_message(chat_id=chat_id, text=weather)

        await asyncio.sleep(sleep_time_in_seconds)


async def process_locations(locations: list[tuple[float, float]]) -> str:
    result: str = ""
    for location in locations:
        weather: str = await Weather.get_weather(location)
        result += f"Локация: {location[0], location[1]}. Погода: {weather}\n"

    result += ("Данные о погоде получены при помощи API Gismeteo.\n"
               "https://www.gismeteo.ru/")
    return result


@base_router.message(Command("help"))
async def show_commands(message: types.Message):
    commands = ("/start - Начать пользоваться ботом,\n"
                "/exit - Прекратить пользование,\n"
                "/pause - Приостановить рассылку,\n"
                "/resume - Продолжить рассылку,\n"
                "/add_location <Координата>, <Координата> - Добавить локацию,\n"
                "/pop_location <Номер> - Удалить локацию,\n"
                "/view - Просмотреть локации.")

    await message.reply(commands)


@base_router.message(F.text)
async def default_handler(message: types.Message) -> None:
    PHRASES = [
        "Я не понимаю, что ты говоришь",
        "Такой команды у меня нет",
        "Используй /help, чтобы посмотреть список команд",
        "A1sun лох, кста"
    ]
    await message.answer(choice(PHRASES))


async def start_bot():
    dp = Dispatcher()
    dp.include_routers(Users.router, base_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    await asyncio.gather(start_bot(), process_users())


if __name__ == "__main__":
    asyncio.run(main())
