from keyboards.inline.callbacks import ActionCallback, BackCallback
from keyboards.inline.keyboards import MainMenuBuilder, InlineBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from data.texts import texts
from aiogram import Router
from typing import Final, List
from loader import bot
from aiogram import F


main_menu_router: Final[Router] = Router(name='main_menu')


@main_menu_router.callback_query(ActionCallback.filter(F.menu_level == MainMenuBuilder.get_menu_level()))
async def handle_main_menu(call: CallbackQuery):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    print(call.data)
    if callback_components.action == "place_advertisement":
        ...

    elif callback_components.action == "services_price":
        old_keyboard: List = call.message.reply_markup.inline_keyboard
        new_keyboard: List = old_keyboard.copy()
        new_keyboard.remove(old_keyboard[1])
        new_keyboard.append([InlineBuilder().get_back_button()])

        await call.message.edit_text(
            text=texts.get("services_price"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
        )


@main_menu_router.callback_query(BackCallback.filter(F.go_to == MainMenuBuilder.get_menu_level()))
async def handle_back_button(call: CallbackQuery):
    await call.message.edit_text(
        text=texts.get("greetings"),
        reply_markup=MainMenuBuilder().get_keyboard()
    )
