from typing import Final, Dict

back_button_text: Final[str] = "🔙 Назад"

greeting_text: Final[str] = """
Здравствуйте! 

Я — чат-бот, созданный для помощи в размещении вашей информации и рекламы в чатах микрорайонов города Омска. 

Через меня вы можете:
"""

services_price_text: Final[str] = """
Прайс-лист на размещение информации: 

📌Весь город (65 чатов) - 5000 без закрепления, закрепление 1500 рублей за каждые сутки

Публикация в чатах по округам:
📌КАО (20 чатов) – 2000 без закрепления, закрепление 500 рублей за каждые сутки

📌САО (13 чатов)- 2000 без закрепления, закрепление 500 рублей за каждые сутки

📌ЦАО (13 чатов) - 1500 без закрепления, закрепление 500 рублей за каждые сутки

📌ЛАО (11 чатов) - 1500 без закрепления, закрепление 500 рублей за каждые сутки

📌ОАО (8 чатов) - 1000 без закрепления, закрепление 500 рублей за каждые сутки

📌Отдельно любой чат – 300 без закрепления, закрепление 100 рублей за каждые сутки 

По вопросам долгосрочного сотрудничества обращайтесь к администратору: @chatadmin55
"""

place_advertisement: Final[str] = """
Выберите в каком(их) чатах вы хотите разместить информацию
"""

select_various_chats: Final[str] = """
Выберите несколько чатов, в
которых хотите разместиться
"""

select_pin_time: Final[str] = """
Необходимо ли вам закрепление вашей публикации?
"""

enter_number_of_pin_days: Final[str] = """
Введите количество дней на которое необходимо закрепить публикацию.
Введите только цифры без пробелов и букв, закрепление возможно не более чем на 31 день.
"""

wrong_number_of_pin_days: Final[str] = """
Введены не корректные данные, Введите только цифры без пробелов и букв, закрепление возможно не более чем на 31 день.
"""

datetime_default_string: Final[str] = """
Не забудьте выбрать время и
дату публикации
"""

repost_from_group_description: Final[str] = """
Вы можете прислать сообщение, а также пост из группы или переписки – оно будет опубликовано как пересланное от вашего имени или группы. 
В данном случае все будут видеть отправителя (или группу в которой опубликован пост) и смогут напрямую к нему обратиться или перейти в группу.
"""


post_from_bot_description: Final[str] = """
Вы присылаете мне ваше сообщение и оно будет опубликовано от имени чат-бота. В данном случае никто не будет видеть отправителя.
"""


placement_type_selection: Final[str] = """
<b>Выберите механику размещения</b>

Вариант {option}/2
<b>{placement_type}</b>
{description}
"""

message_from_bot_requirements: Final[str] = """
<b>Требования к сообщению:</b>

<b>Пост без медиа-файлов:</b>
Длина сообщения: до 3950 символов.

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

Принимаю только одно сообщение. Если есть медиафайл, он должен быть прикреплен к сообщению.
Суммарное количество медиафайлов должно быть равно 1
Перешлите мне сообщение из группы, или пришлите мне сообщение от вашего имени.

"""

check_post_details: Final[str] = """
<b>Проверьте текст поста и
выберите следующее 
действие.</b>

<i>{text}</i>
"""

complete_place_advertisement: Final[str] = """
Материалы направлены на модерацию, после прохождения модерации вы получите обратную связь.
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
Ваши материалы не прошли модерацию. Для уточнения подробностей напишите администратору
или направьте отредактированные материалы на повторную модерацию. 
Администратор: @chatadmin55

Правки: <i>{notes}</i>
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
Ваши материалы успешно прошли модерацию!
Вы можете произвести оплату.

Сумма к оплате: <b>{total_cost}</b> руб
"""

service_cost_check: Final[str] = """
● <b>{service_name}</b> -- <i>{service_cost}</i> руб.
"""

payment_check_text: Final[str] = """
Стоимость размещения по заданным параметрам составляет: <b>{total}</b> рублей
Пакет размещения: <b>{chats}</b>
Дата: <b>{date}</b>
Время: <b>{time}</b>
Закрепление на <b>{pin_days}</b> суток

Для оплаты размещения материалов необходимо совершить перевод денежных средств на карту 4274 3201 0643 1458

В случае если оплату будет производить юридическое лицо – необходимо связаться с администратором для выставления счета: @chatadmin55

После оплаты – подтвердите
"""

canceled_post_text: Final[str] = """
Пользователь <b>@{username}</b> отменил свою заявку на этапе оплаты.
"""

request_payment_check: Final[str] = """
Пришлите, пожалуйста, документ подтверждающий оплату – скриншот или чек.
"""


admin_checks_payment_text: Final[str] = """
Благодарю! Администратор подтвердит вашу оплату в ближайшее время.
После этого ваша публикация встанет в очередь.
Ожидайте, после подтверждения от администратора я вас уведомлю
"""


user_confirmed_payment: Final[str] = """
<b>@{username}</b> подтвердил оплату
на <b>{total_cost}</b> руб
"""

failed_payment: Final[str] = """
Оплата не подтверждена. 
Свяжитесь с администратором: @chatadmin55

Для оплаты размещения материалов необходимо совершить перевод денежных средств на карту 4274 3201 0643 1458

В случае если оплату будет производить юридическое лицо – необходимо связаться с администратором для выставления счета: @chatadmin55
"""

successful_payment: Final[str] = """
Ваша оплата принята, ожидайте размещение материалов по заданным параметрам:
Стоимость размещения по заданным параметрам составляет: <b>{total}</b> рублей
Пакет размещения: <b>{chats}</b>
Дата: <b>{date}</b>
Время: <b>{time}</b>
Без закрепления/Закрепление на <b>{pin_days}</b> суток

Для связи с администратором: @chatadmin55
"""

finish_payment: Final[str] = """
Благодарю вас за пользованиенашими услугами! 
После публикации объявления я вас уведомлю.

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

published_successfully: Final[str] = """
Публикация материалов по установленным параметрам успешно произведена. 
Благодарим за обращение к нам!

В случае если вы заинтересованы в регулярном размещении – свяжитесь с администратором для предоставления индивидуальных условий и подписывайтесь на наш канал.
Администратор: @chatadmin55
Наш канал: @gorchat55
"""


texts: Final[Dict] = {
    "greetings": greeting_text,
    "back_button": back_button_text,
    "services_price": services_price_text,
    "place_advertisement": place_advertisement,
    "select_various_chats": select_various_chats,
    "select_pin_time": select_pin_time,
    "enter_number_of_pin_days": enter_number_of_pin_days,
    "wrong_number_of_pin_days": wrong_number_of_pin_days,

    "repost_from_group_description": repost_from_group_description,
    "post_from_bot_description": post_from_bot_description,

    "datetime_default_string": datetime_default_string,

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
    "modify_post": modify_post,
    "published_successfully": published_successfully,

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
