from keyboards.inline.keyboards import MainMenuBuilder
from aiogram.filters.command import CommandStart
from database.models import User
from loader import postgres
from data.texts import texts
from aiogram import Router
from aiogram import types

command_start = Router(name="start")


@command_start.message(CommandStart())
async def bot_start(message: types.Message):
    user = await postgres.get_user(user_id=message.from_user.id)

    if not user:
        user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        await postgres.add_user(user)

    await message.answer(
        text=texts.get("greetings"),
        reply_markup=MainMenuBuilder().get_keyboard()
    )
