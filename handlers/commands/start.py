from keyboards.inline.admin_keyboards import AdminMainMenuKeyboard
from keyboards.inline.keyboards import MainMenuBuilder
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from data.texts import texts, templates
from database.models import User, Roles
from states.states import StateGroup
from loader import postgres
from typing import Final
from aiogram import Router


command_start = Router(name="start")


async def open_admin_menu(message: Message, state: FSMContext):
    admin_keyboard: Final[AdminMainMenuKeyboard] = AdminMainMenuKeyboard()
    await message.answer(
        text=templates.get("admin_greeting").format(
            admin_username=message.from_user.username,
            new_users=await postgres.count_users_joined_today(),
            posts_waiting_count=await postgres.count_requests_waiting_for_moderation(),
        ),
        reply_markup=admin_keyboard.get_keyboard()
    )
    await state.set_state(StateGroup.admin)


async def open_user_menu(message: Message):
    message_to_delete: Message = await message.answer(
        text="Загрузка...",
        reply_markup=ReplyKeyboardRemove()
    )
    await message_to_delete.delete()
    await message.answer(
        text=texts.get("greetings"),
        reply_markup=MainMenuBuilder().get_keyboard()
    )


@command_start.message(CommandStart())
async def bot_start(message: Message, state: FSMContext):
    user = await postgres.get_user(user_id=message.from_user.id)

    if not user:
        user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        await postgres.add_user(user)

    if user.role == Roles.admin:
        await open_admin_menu(message, state)

    else:
        await open_user_menu(message)
