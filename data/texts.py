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
"""

message_from_bot_requirements: Final[str] = """
<b>Требования к сообщению:</b>

<b>Пост без медиа-файлов:</b>
Длина сообщения: до 3950 символов.

Если есть ссылки, то вводите следующим способом без пробелов:
<a href="Ваша ссылка">название вашей ссылки</a>


<b>Пост с медиа-файлами:</b>
Длина сообщения: до 900 символов, если есть медиа-файлы.
Длительность видео: до 1 минуты.
Фото и видео: до 10 штук.
Суммарный размер медиа-файлов должен быть меньше 10мб.

<b>Цензура:</b> маты запрещены.

<b>Сначала напишите текст сообщения,</b>
<b>согласно типу вашего поста</b>
"""

reposted_message_requirements: Final[str] = """
<b>Требования к сообщению</b>:

Принимаю только одно
сообщение. Если есть медиа-
файл, он должен быть 
прикреплен к сообщению.

Суммарное количество 
медиа-файлов должно быть равно 1

<b>Перешлите мне сообщение из {source}.</b>
"""

from_user_source: Final[str] = "вашей переписки"
from_group_source: Final[str] = "группы"

check_post_details: Final[str] = """
<b>Проверьте текст поста и
выберите следующее 
действие.</b>

<i>{text}</i>
"""

complete_place_advertisement: Final[str] = """
Ваше сообщение находится 
на модерации. Это займет
некоторое время. Пожалуйста,
ожидайте. 

Как только ваш пост пройдет
проверку, я уведомлю вас и вы
сможете произвести оплату.

Итоговая сумма оплаты
составляет <b>{price} руб</b>.

Чтобы не потерять чат,
закрепите его у себя в 
Telegram
"""

attach_media_text: Final[str] = """
Пришлите 1 файл фото/видео.

Чтобы добавить к посту еще
медиа, повторите шаг 
добавления медиа
"""

choose_publish_datetime: Final[str] = """
Пожалуйста, выберите время и
дату публикации ⏰
"""

moderation_text: Final[str] = """
Объявление на модерацию:
От пользователя: <b>@{username}</b>
Дата: <b>{date}</b>
Время: <b>{time}</b>
Закрепление: <b>{pin_days}</b> дней
Чаты: {chats}

------------------------------------------------

"""

admin_greeting: Final[str] = """
Приветствую, <b>{admin_username}</b>!

Вы находитесь в главном 
меню. 

За сегодня к боту
присоединилось <b>{new_users}</b> чел.

Количество постов в ожидании вашей модерации: <b>{posts_waiting_count}</b>.
"""


request_admin_moderation_decision: Final[str] = """
Выберите действие ⬇️
"""


post_declined: Final[str] = """
Ваше объявление не прошло
модерацию. Пожалуйста,
внесите следующие правки:

<i>{notes}</i>
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

    "datetime_default_string": datetime_default_string,

    "from_user_source": from_user_source,
    "from_group_source": from_group_source,

    "message_from_bot_requirements": message_from_bot_requirements,
    "check_post_details": check_post_details,
    "attach_media_text": attach_media_text,
    "choose_publish_datetime": choose_publish_datetime,
    "request_admin_moderation_decision": request_admin_moderation_decision

}

templates: Final[Dict] = {
    "placement_type_selection": placement_type_selection,
    "reposted_message_requirements": reposted_message_requirements,
    "complete_place_advertisement": complete_place_advertisement,
    "moderation_text": moderation_text,
    "admin_greeting": admin_greeting,
    "post_declined": post_declined,

}
