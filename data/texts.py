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

post_info: Final[str] = """
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

users_statistics: Final[str] = """
Статистика пользователей

Общее кол-во: <b>{all_users_count}</b> чел
-----------------------------------------------
Новых за месяц: <b>{month_users}</b> чел
-----------------------------------------------
Новых за неделю: <b>{week_users}</b> чел
-----------------------------------------------
Новых за день: <b>{day_users}</b> чел
"""


posts_statistics: Final[str] = """
Статистика публикаций

Всего: <b>{all_posts_count}</b>
-----------------------------------------------
Размещено: <b>{placed_posts_count}</b>
-----------------------------------------------
Размещено с закреплением: <b>{placed_with_pin_count}</b>
-----------------------------------------------
Размещено без закрепления: <b>{placed_without_pin_count}</b>
-----------------------------------------------
В ожидании: <b>{posts_waiting_count}</b>
"""


income_statistics: Final[str] = """
Статистика доходов

Доход за всё время: <b>{total_income}</b> руб
-----------------------------------------------
Доход за месяц: <b>{month_income}</b> руб
-----------------------------------------------
Доход за неделю: <b>{week_income}</b> руб
-----------------------------------------------
Доход за день: <b>{day_income}</b> руб
"""


approved_post_text: Final[str] = """
Ваше объявление прошло
модерацию! Вы можете 
произвести оплату 2-мя 
способами:

1) Переводом на банковскую карту (как физ. лицо)

2) По реквизитам счета (как юр. лицо)

Сумма к оплате: <b>{total_cost}</b> руб
"""

service_cost_check: Final[str] = """
● <b>{service_name}</b> -- <i>{service_cost}</i> руб.
"""

payment_check_text: Final[str] = """
Вы оплачиваете услуги:

{services_cost_check}

---------------------------------
Итого: <b>{total_cost}</b> руб.

Оплату можно произвести
переводом на карту ТАКОГО-ТО
банка: <b>{card_number}</b>

После оплаты нажмите на
кнопку
"""

canceled_post_text: Final[str] = """
Пользователь <b>@{username}</b> отменил свою заявку на этапе оплаты.
"""

request_payment_check: Final[str] = """
Пришлите, пожалуйста, фиксаль
ный чек или скриншот, 
подтверждающий оплату
"""


admin_checks_payment_text: Final[str] = """
Благодарю! Администратор
подтвердит вашу оплату в тече
нии 15 минут.

После этого ваша публикация 
встанет в очередь.

У вас будет возможность 
изменить дату/время, если
это необходимо.

Ожидайте, я вас уведомлю
"""


user_confirmed_payment: Final[str] = """
<b>@{username}</b> подтвердил оплату
на <b>{total_cost}</b> руб
"""

failed_payment: Final[str] = """
Ваша оплата не подтвердилась
по каким-то причинам. Свяжи
тесь с администратором для
выяснения причин.
"""

successful_payment: Final[str] = """
Спасибо за ожидание. Ваша
оплата подтверждена.

Публикация: “<b>{text_part}...</b>” будет опубликована в
<i>{chats}</i> 

Дата: <b>{date}</b>
Время: <b>{time}</b>

Вы можете изменить дату и/или
время или подтвердите.

❗️ВНИМАНИЕ❗️
После подтверждения,
изменить дату и время будет
невозможно.
"""

finish_payment: Final[str] = """
Благодарю вас за пользование
нашими услугами! После 
публикации объявления я вас
уведомлю.

Вы можете создать до 5 ожида
ющих публикаций.
"""

finish_all_stages: Final[str] = """
Благодарю вас за пользование
нашими услугами!

Вы можете создать до 5 ожида
ющих публикаций.
"""

post_cancellation_confirm: Final[str] = """
Вы точно хотите отменить 
публикацию?
"""

modify_post: Final[str] = """
Пришлите измененный текст публикации.

Все медиа-файлы нужно будет
прикрепить заново.
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
    "request_admin_moderation_decision": request_admin_moderation_decision,

    "request_payment_check": request_payment_check,
    "admin_checks_payment_text": admin_checks_payment_text,
    "failed_payment": failed_payment,
    "finish_payment": finish_payment,
    "finish_all_stages": finish_all_stages,
    "post_cancellation_confirm": post_cancellation_confirm,
    "modify_post": modify_post

}

templates: Final[Dict] = {
    "placement_type_selection": placement_type_selection,
    "reposted_message_requirements": reposted_message_requirements,
    "complete_place_advertisement": complete_place_advertisement,
    "post_info": post_info,
    "admin_greeting": admin_greeting,
    "post_declined": post_declined,

    "users_statistics": users_statistics,
    "posts_statistics": posts_statistics,
    "income_statistics": income_statistics,

    "approved_post_text": approved_post_text,
    "service_cost_check": service_cost_check,
    "payment_check_text": payment_check_text,

    "canceled_post_text": canceled_post_text,
    "user_confirmed_payment": user_confirmed_payment,
    "successful_payment": successful_payment
}
