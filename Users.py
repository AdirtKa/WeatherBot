import json

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.filters.state import State, StatesGroup
from SomeClasses import User


router = Router()
users: dict[int, User] = {}


class StateUser(StatesGroup):
    name = State()
    location = State()


def get_all_users():
    global users
    try:
        with open('user_data.json', 'r', encoding="utf-8-sig") as f:
            users = json.load(f)
            users = {int(k): v for k, v in users.items()}

    except FileNotFoundError:
        users = {}


get_all_users()


def exist_user(user_id: int):
    global users
    return user_id in users.keys()


@router.message(StateFilter(None), Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    if exist_user(message.from_user.id):
        await message.answer("Вы уже зарегистрированы")
        return

    await state.set_state(StateUser.name)
    await message.reply("Как к вам обращаться?")


@router.message(StateUser.name, F.text)
async def name_is_received(message: Message, state: FSMContext):
    message_text: str = message.text
    if len(message_text.split()) > 1:
        await message.answer("Введите имя одним словом")
        return

    await state.update_data(username=message.text.lower())
    await message.reply("Отлично, теперь добавьте геопозицию локации двумя координатами через запятую."
                        "Как разделитель дробной части используйте точку")
    await state.set_state(StateUser.location)


@router.message(StateUser.location, F.text)
async def location_is_received(message: Message, state: FSMContext):
    location = message.text.split(",")

    if len(location) != 2:
        await message.answer("Введите две координаты через запятую")
        return

    try:
        parsed_location: tuple = tuple(float(x) for x in location)
        await state.update_data(location=parsed_location)
        await add_user(message.chat.id, state)
        await message.answer("Вы добавлены")

    except ValueError:
        await message.answer("Неправильно введены данные")

    except Exception as ex:
        print(type(ex))
        await message.answer("SWW")
        return


async def add_user(chat_id: int, state: FSMContext):
    global users
    user_data = await state.get_data()
    users[chat_id] = User(
        name=user_data["username"],
        locations=[user_data["location"]],
        is_checking=True
    )
    save_users()

    await state.clear()


def save_users():
    global users
    with open('user_data.json', 'w', encoding="utf-8-sig") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


@router.message(Command("pause"))
async def pause(message: Message):
    chat_id = message.chat.id
    if chat_id in users:
        users[chat_id]["is_checking"] = False
        await message.reply("Рассылка остановлена для вас.")
    else:
        await message.reply("Вы еще не зарегистрированы. Пожалуйста, начните с команды /start.")


@router.message(Command("resume"))
async def pause(message: Message):
    chat_id = message.chat.id
    if chat_id in users:
        users[chat_id]["is_checking"] = True
        await message.reply("Рассылка запущена для вас.")
    else:
        await message.reply("Вы еще не зарегистрированы. Пожалуйста, начните с команды /start.")


@router.message(Command("add_location"))
async def add_location(message: Message, command: CommandObject):
    global users

    chat_id = message.chat.id
    if chat_id not in users:
        await message.reply("Вы еще не зарегистрированы. Пожалуйста, начните с команды /start.")

    if command.args is None:
        await message.answer("Не переданы аргументы")
        return

    latitude, longitude = command.args.split(",", maxsplit=1)
    try:
        location: tuple[float, float] = (float(latitude), float(longitude))
        users[chat_id]["locations"].append(location)
        save_users()
        await message.reply("Локация добавлена")

    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/add_location <координата>, <координата>"
        )


@router.message(Command("pop_location"))
async def pop_location(message: Message, command: CommandObject):
    global users

    chat_id = message.chat.id
    if chat_id not in users:
        await message.reply("Вы еще не зарегистрированы. Пожалуйста, начните с команды /start.")

    if command.args is None:
        await message.answer("Не переданы аргументы")
        return

    try:
        location = users[chat_id]["locations"].pop(int(command.args) - 1)
        await message.answer(f"Локация {location} успешно удалена")
        save_users()
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/pop_location <Номер локации>"
        )
    except IndexError:
        await message.answer(
            "Нет локации под таким номером"
        )


@router.message(Command("exit"))
async def delete_user(message: Message):
    del users[message.chat.id]
    save_users()
    await message.answer("Вы успешно удалены")


@router.message(Command("view"))
async def view_locations(message: Message):
    answer = "Ваши локации:\n"
    for idx, location in enumerate(users[message.chat.id]["locations"], start=1):
        answer += f"{idx}. {location[0], location[1]},\n"
    await message.answer(answer)


if __name__ == "__main__":
    print(users)
    print(exist_user(1018707880))
