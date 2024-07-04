from random import choice

from config_reader import config

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command


def get_all_users() -> dict[int, list[tuple[float, float]]]:
    return {}


logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, current_users: dict):
    await message.answer(f"first command, {str(current_users)}")


@dp.message(F.text)
async def default_handler(message: types.Message):
    PHRASES = [
        "Я не понимаю, что ты говоришь",
        "Такой команды у меня нет",
        "Используй /help, чтобы посмотреть список команд"
    ]
    await message.answer(choice(PHRASES))


async def main():
    users: dict[int, list[tuple[float, float]]] = get_all_users()
    bot = Bot(token=config.bot_token.get_secret_value())
    await bot.delete_webhook(drop_pending_updates=True)
    dp["current_users"] = users
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
