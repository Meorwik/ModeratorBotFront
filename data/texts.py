from typing import Final, Dict

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


datetime_default_string: Final[str] = """
Не забудьте выбрать время и
дату публикации
"""

repost_from_group_description: Final[str] = """
Пост будет опубликован, как
пересланное сообщение от
имени вашей группы.
"""

repost_from_user_description: Final[str] = """
Пост будет опубликован, как
пересланное сообщение от
имени автора сообщения.
"""

post_from_bot_description: Final[str] = """
Вы пишете мне сообщение, я его
публикую от своего имени
"""


placement_type_selection: Final[str] = """
<b>Выберите механику размещения</b>

Вариант {option}/3

<b>{placement_type}</b>

{description}

{datetime}
"""


texts: Final[Dict] = {
    "greetings": greeting_text,
    "back_button": back_button_text,
    "services_price": services_price_text,
    "place_advertisement": place_advertisement,
    "select_various_chats": select_various_chats,
    "select_pin_time": select_pin_time,
    "enter_number_of_pin_days": enter_number_of_pin_days,

    "repost_from_group_description": repost_from_group_description,
    "repost_from_user_description": repost_from_user_description,
    "post_from_bot_description": post_from_bot_description,
    "datetime_default_string": datetime_default_string

}

templates: Final[Dict] = {
    "placement_type_selection": placement_type_selection
}
