import configparser
from urllib.parse import urlencode

import telebot
from telebot import types
import threading
import time

from database.admin_functions import create_connection, get_all_validations, execute_run_once_sql
from datetime import datetime, timedelta

from database.standart_functions.add_validation import add_validation_for_user
from database.standart_functions.delete_validation import delete_validation_by_id
from database.standart_functions.get_validation import get_all_validations_user, get_validations_by_user_id, \
    get_validations_for_days
from database.standart_functions.modificate_validation import update_validation_name, update_validation_datetime, \
    update_validation_description

config = configparser.ConfigParser()
config.read('config_bot.ini')
bot_token = config['telegram']['token']
print(bot_token)

bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text == "Назад")
def show_main_menu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton("Редактировать задачи")
    button2 = types.KeyboardButton("Просмотреть текущие задачи")
    button3 = types.KeyboardButton("Создать задачу")
    keyboard.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Выберите пункт меню", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Редактировать задачи")
@bot.message_handler(func=lambda message: message.text == "Отмена")
def show_validation_list_for_change(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    all_validations = get_all_validations_user(message.from_user.id)
    if all_validations:
        for validation in all_validations:
            validation_id = str(validation[0])
            user_id = str(validation[4])
            validation_name = validation[2]

            button = types.InlineKeyboardButton(text=validation_name, callback_data=f"validation_{validation_id}"
                                                                                    f"_{user_id}"
                                                )
            keyboard.add(button)
    back_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
    keyboard.add(back_button)
    bot.send_message(message.chat.id, "Выберите задачу", reply_markup=keyboard)


# key back handler
@bot.callback_query_handler(func=lambda call: call.data == "back")
def handle_back_button(call):
    show_main_menu(call.message)


# change validation handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("validation_"))
def handle_selected_validation_for_change(call):
    data_parts = call.data.split("_")
    validation_id = int(data_parts[1])
    user_id = data_parts[2]

    validation = get_validations_by_user_id(user_id, validation_id)
    if validation:
        validation_datetime = validation[0][1]
        validation_description = validation[0][3]
        validation_id = validation[0][0]
        validation_name = validation[0][2]
        user_id = validation[0][4]

        response = f"Название задачи:   {validation_name}\n"
        response += f"Дедлайн:          {validation_datetime}\n"
        response += f"Описание:         {validation_description}"
        keyboard = types.InlineKeyboardMarkup()
        delete_button = types.InlineKeyboardButton("Удалить задачу", callback_data=f"delete_{validation_id}")
        change_button = types.InlineKeyboardButton("Изменить данные", callback_data=f"edit_{validation_id}"
                                                                                    f"_{user_id}")
        keyboard.row(delete_button)
        keyboard.row(change_button)
        bot.send_message(call.message.chat.id, response, reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id, "Задача не найдена")


# changed validation handler
@bot.message_handler(func=lambda message: message.text != "Назад" and
                                          message.text in [v[2] for v in
                                                           get_all_validations_user(message.from_user.id)])
def handler_selected_validation_for_change(message):
    validation_id = int(message.data)
    validation_name = message.text
    print("selected validation id for change: ", validation_id)

    validation = get_validations_by_user_id(str(message.from_user.id), int(validation_id))

    if validation:
        validation_datetime = validation[0][1]
        validation_description = validation[0][3]
        validation_id = validation[0][0]
        validation_name = validation[0][2]
        user_id = validation[0][4]
        response = f"Название задачи:   {validation_name}\n"
        response += f"Дедлайн:          {validation_datetime}\n"
        response += f"Описание:         {validation_description}"
        keyboard = types.InlineKeyboardMarkup()
        delete_button = types.InlineKeyboardButton("Удалить задачу", callback_data=f"delete_{validation_id}")
        change_button = types.InlineKeyboardButton("Изменить данные", callback_data=f"edit_{validation_id}"
                                                                                    f"_{user_id}")
        keyboard.row(delete_button)
        keyboard.row(change_button)
        bot.send_message(message.chat.id, response, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Задача не найдена")


# delete validation handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_validation_handler(call):
    validation_id = call.data.split("_")[1]

    delete_validation_by_id(int(validation_id), str(call.from_user.id))

    bot.send_message(call.message.chat.id, f"Задача успешно удалена")
    show_main_menu(call.message)


# edit validation handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_validation_handler(call):
    validation_id = int(call.data.split("_")[1])
    user_id = call.data.split("_")[2]

    validation = get_validations_by_user_id(user_id, validation_id)
    validation_datetime = validation[0][1]
    validation_description = validation[0][3]
    validation_id = validation[0][0]
    validation_name = validation[0][2]
    user_id = validation[0][4]

    response = f"Название задачи:   {validation_name}\n"
    response += f"Дедлайн:          {validation_datetime}\n"
    response += f"Описание:         {validation_description}"
    keyboard = types.InlineKeyboardMarkup()
    change_name_button = types.InlineKeyboardButton("Название", callback_data=f"change_name_{validation_id}")
    change_date_button = types.InlineKeyboardButton("Дата", callback_data=f"change_date_{validation_id}")
    change_description_button = types.InlineKeyboardButton("Описание",
                                                           callback_data=f"change_description_{validation_id}")
    keyboard.row(change_name_button)
    keyboard.row(change_date_button)
    keyboard.row(change_description_button)
    bot.send_message(call.message.chat.id, "Изменяемый параметр:", reply_markup=keyboard)


# edit validation sub-handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("change_"))
def edit_validation(call):
    action, validation_id = call.data.split("_")[1:]
    if action == "name":
        bot.send_message(call.message.chat.id, "Введите новое название задачи:")
        bot.register_next_step_handler(call.message, lambda message: update_validation_name_handler(
            message.text, int(validation_id), str(call.from_user.id)))
    elif action == "date":
        bot.send_message(call.message.chat.id, "Введите новое время задачи (в формате ГГГГ ММ ДД ЧЧ:ММ):")
        bot.register_next_step_handler(call.message, lambda message: update_validation_datetime_handler(call,
                                                                                                        message.text,
                                                                                                        int(validation_id),
                                                                                                        str(call.from_user.id)))
    elif action == "description":
        bot.send_message(call.message.chat.id, "Введите новое описание задачи:")
        bot.register_next_step_handler(call.message, lambda message: update_validation_description_handler(
            message.text, int(validation_id), str(call.from_user.id)))
    else:
        bot.send_message(call.message.chat.id, "Неверное действие")


def update_validation_name_handler(name, validation_id, user_id):
    update_validation_name(name, validation_id, user_id)
    bot.send_message(user_id, f"Название задачи изменено на '{name}'")


def update_validation_datetime_handler(call, date_time, validation_id, user_id):
    try:
        datetime_obj = datetime.strptime(date_time, "%Y %m %d %H:%M")
        formatted_datetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
        update_validation_datetime(formatted_datetime, validation_id, user_id)
        bot.send_message(user_id, f"Дата изменена на '{formatted_datetime}'")
    except ValueError:
        bot.send_message(call.message.chat.id, "Неверный формат даты и времени.")
        edit_validation(call)


def update_validation_description_handler(description, validation_id, user_id):
    update_validation_description(description, validation_id, user_id)
    bot.send_message(user_id, f"Описание изменено на '{description}'")


@bot.message_handler(func=lambda message: message.text == "Просмотреть текущие задачи")
def view_next_validations(message):
    keyboard = types.InlineKeyboardMarkup()
    all_button = types.InlineKeyboardButton("Все", callback_data="view_all")
    next_days_button = types.InlineKeyboardButton("Следующие N дней", callback_data="view_next_days")
    keyboard.row(all_button, next_days_button)
    bot.send_message(message.chat.id, "Выберите опцию для просмотра:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "view_all")
def handle_view_all(call):
    validations = get_all_validations_user(call.from_user.id)
    send_validations(call.message.chat.id, validations)


@bot.callback_query_handler(func=lambda call: call.data == "view_next_days")
def handle_view_next_days(call):
    bot.send_message(call.message.chat.id, "Введите количество дней для просмотра:")
    bot.register_next_step_handler(call.message, handle_view_next_days_input)


def handle_view_next_days_input(message):
    try:
        num_days = int(message.text)
        if num_days <= 0:
            bot.send_message(message.chat.id, "Пожалуйста, введите положительное число дней.")
            return
        validations = get_validations_for_days(num_days, str(message.from_user.id))
        send_validations(message.chat.id, validations)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное число дней.")


@bot.message_handler(func=lambda message: message.text == "Создать задачу")
def create_task(message):
    bot.send_message(message.chat.id, "Введите название новой задачи:")
    bot.register_next_step_handler(message, lambda call: create_task_name_handler(
        message, call.text))


from datetime import datetime


def create_task_name_handler(message, name):
    bot.send_message(message.chat.id, "Введите дату и время задачи (в формате ГГГГ ММ ДД ЧЧ:ММ):")

    def validate_datetime_input(message, name, datetime_str):
        try:
            datetime_obj = datetime.strptime(datetime_str, '%Y %m %d %H:%M')
            formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
            create_task_datetime_handler(message, name, formatted_datetime)
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат даты и времени.")
            create_task_name_handler(message, name)

    bot.register_next_step_handler(message, lambda call: validate_datetime_input(
        message, name, call.text))


def create_task_datetime_handler(message, name, date_time):
    bot.send_message(message.chat.id, "Введите описание задачи:")
    bot.register_next_step_handler(message, lambda call: create_task_description_handler(
        name, date_time, call.text, message))


from datetime import datetime

def create_task_description_handler(name, date_time, description, message):
    date_time_str = str(date_time) if isinstance(date_time, datetime) else date_time

    formatted_date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    print(formatted_date_time)

    validation_id = add_validation_for_user(formatted_date_time, name, description, message.chat.id)
    create_single_notification_thread(validation_id, formatted_date_time.strftime("%Y %m %d %H:%M"), name, message.chat.id)
    bot.send_message(message.chat.id,
                     f"Новая задача создана:\nНазвание: {name}\nДата и время:"
                     f"{formatted_date_time.strftime('%Y %m %d %H:%M')}\nОписание: {description}")


def send_validations(chat_id, validations):
    if validations:
        response = ""
        for validation in validations:
            validation_name = validation[2]
            validation_datetime = validation[1]
            if isinstance(validation_datetime, datetime):  # Проверяем, является ли объект datetime
                formatted_datetime = validation_datetime.strftime("%Y %m %d %H:%M")
            else:
                formatted_datetime = datetime.strptime(validation_datetime, "%Y-%m-%d %H:%M:%S").strftime(
                    "%Y %m %d %H:%M")
            validation_description = validation[3]
            response += f"Название задачи:   {validation_name}\n"
            response += f"Дедлайн:          {formatted_datetime}\n"
            response += f"Описание:         {validation_description}\n\n"
        bot.send_message(chat_id, response)
    else:
        bot.send_message(chat_id, "Нет доступных напоминаний")


def send_notification(chat_id, validation_name, validation_datetime, validation_description):
    if isinstance(validation_datetime, datetime):  # Проверяем, является ли объект datetime
        formatted_datetime = validation_datetime.strftime("%Y %m %d %H:%M")
    else:
        formatted_datetime = datetime.strptime(validation_datetime, "%Y-%m-%d %H:%M:%S").strftime("%Y %m %d %H:%M")

    response = "Напоминание!\n"
    response += f"Название задачи:  {validation_name}\n"
    response += f"Дедлайн:          {formatted_datetime}\n"
    response += f"Описание:         {validation_description}\n\n"
    bot.send_message(chat_id, response)


def create_notifications_threads():
    list_notif = get_all_validations()
    print(list_notif)
    for notification in list_notif:
        task_id = notification[0]
        date_time = notification[1]
        task_name = notification[2]
        user_id = int(notification[4])
        print(date_time)

        days_until_notification = (date_time - datetime.now()).days
        if days_until_notification <= 4:
            daemon_thread = threading.Thread(target=daemon_notification_function,
                                             args=(user_id, task_id))
            daemon_thread.daemon = True
            daemon_thread.start()
        else:
            print(f"Notification for task '{task_name}' will occur in more than 4 days. Skipping...")


def daemon_notification_function(user_id, task_id):
    validation = get_validations_by_user_id(user_id, task_id)
    if not validation:
        print("task ", task_id, " was deleted. ", "notification canceled")
        return
    task_id = validation[0][0]
    date_time = validation[0][1]
    task_name = validation[0][2]
    task_description = validation[0][3]
    current_time = datetime.now()
    time_difference = (date_time - current_time).total_seconds()
    if time_difference > 0:
        print(f"Daemon thread sleeping for {time_difference} seconds")
        time.sleep(time_difference)
    send_notification(user_id, task_name, date_time, task_description)
    delete_validation_by_id(int(task_id), str(user_id))
    print(f"Notification for task '{task_name}' with description '{task_description}' sent to user {user_id}")


def create_single_notification_thread(task_id, date_time_str, task_name, user_id):
    date_time = datetime.strptime(date_time_str, "%Y %m %d %H:%M")
    days_until_notification = (date_time - datetime.now()).days
    if days_until_notification <= 4:
        daemon_thread = threading.Thread(target=daemon_notification_function,
                                         args=(user_id, task_id))
        daemon_thread.daemon = True
        daemon_thread.start()
    else:
        print(f"Notification for task '{task_name}' will occur in more than 4 days. Skipping...")


if __name__ == "__main__":
    execute_run_once_sql()
    create_notifications_threads()
    bot.polling(none_stop=True)
