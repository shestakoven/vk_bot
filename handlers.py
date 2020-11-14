"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True если шаг пройдет, False, если данные введены неверно
"""

import re
re_name = re.compile(r'^[aA-zZ-аА-яЯ-ёЁ\-\s]{2,40}$')
re_email = re.compile(r'\b[-a-z0-9_.]+@[-a-z0-9]+\.+[a-z]{2,6}\b')


def handle_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    email = re.findall(re_email, text)
    if email:
        context['email'] = email[0]
        return True
    else:
        return False

