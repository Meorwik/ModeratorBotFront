from keyboards.inline.keyboards import MainMenuBuilder
from aiogram.filters.command import CommandStart
from data.texts import texts
from aiogram import Router
from aiogram import types

command_start = Router(name="start")


@command_start.message(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(
        text=texts.get("greetings"),
        reply_markup=MainMenuBuilder().get_keyboard()
    )
