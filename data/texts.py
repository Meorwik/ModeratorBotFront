from typing import Final

back_button_text: Final[str] = "🔙 Назад"

greeting_text: Final[str] = """
Приветственное сообщение!

Описание бота и его
финкционала. Подробное
описание кнопок
"""

services_price_text: Final[str] = """
Прайс:

Услуга 1 Текст описания. Текст 
описания. Текст описания. 
Текст описания. 
Стоимость: ХХХХ руб

Услуга 2 Текст описания. Текст 
описания. Текст описания. 
Текст описания. 
Стоимость: ХХХХ руб

...
"""

place_advertisement: Final[str] = """
Выберите в каком(их) чатах
вы хотите разместиться
"""

select_various_chats: Final[str] = """
Выберите несколько чатов, в
которых хотите разместиться
"""

select_pin_time: Final[str] = """
Выберите, какое размещение
вам интересно
"""

enter_number_of_pin_days: Final[str] = """
Введите количство дней без
пробелов и букв. Или
вернитесь назад
"""


texts = {
    "greetings": greeting_text,
    "back_button": back_button_text,
    "services_price": services_price_text,
    "place_advertisement": place_advertisement,
    "select_various_chats": select_various_chats,
    "select_pin_time": select_pin_time,
    "enter_number_of_pin_days": enter_number_of_pin_days,
}
