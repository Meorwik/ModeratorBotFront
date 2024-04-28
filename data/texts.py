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

texts = {
    "greetings": greeting_text,
    "back_button": back_button_text,
    "services_price": services_price_text
}
