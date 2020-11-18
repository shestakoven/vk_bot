"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True если шаг пройдет, False, если данные введены неверно
"""

import re
import settings
from datetime import datetime

re_phone = re.compile(r'^(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){10,14}(\s*)?$')


def handle_departure_city(text, context):
    text = text.lower()
    for city in settings.CITIES:
        if text in city.lower():
            context['departure_city'] = city
            return True
    else:
        return False


def handle_arrival_city(text, context):
    text = text.lower()
    for city in settings.CITIES:
        if text in city.lower():
            context['arrival_city'] = city
            return True
    else:
        return False


def handle_date(text, context):
    departure_city = context['departure_city']
    arrival_city = context['arrival_city']
    try:
        date = datetime.strptime(text, '%d-%m-%Y')
    except ValueError or TypeError:
        return False
    if date.date() < datetime.today().date():
        return False
    date_list = ''
    for i, available_time in enumerate(settings.FLIGHTS[departure_city][arrival_city]):
        available_time = datetime.strptime(available_time, '%d-%m-%Y %H:%M').strftime('%d-%m-%Y %H:%M')
        date_list += str(i + 1) + '. ' + available_time + '\n'
    context['available_time'] = date_list
    return True


def handle_choose_date(text, context): # todo выводить 5 самых ближайших дат
    departure_city = context['departure_city']
    arrival_city = context['arrival_city']
    try:
        int(text)
    except ValueError or TypeError:
        return False
    for i, available_time in enumerate(settings.FLIGHTS[departure_city][arrival_city]):
        if i == int(text) - 1:
            context['chosen_time'] = datetime.strptime(available_time, '%d-%m-%Y %H:%M').strftime('%d-%m-%Y %H:%M')
            return True
    else:
        return False


def handle_passengers(text, context):
    try:
        passengers = int(text)
    except ValueError:
        return False
    if 1 <= passengers <= 5:
        context['passengers'] = text
        return True
    else:
        return False


def handle_comments(text, context):
    if text.lower() == 'нет':
        context['comments'] = 'Без комментария'
        return True
    else:
        context['comments'] = text
    return True


def handle_check_data(text, context):
    if text.lower() == 'да':
        return True
    elif text.lower() == 'нет':
        return 'repeat'
    else:
        return False


def handle_phone(text, context):
    if re.match(re_phone, text):
        context['phone'] = text
        return True
    else:
        return False
