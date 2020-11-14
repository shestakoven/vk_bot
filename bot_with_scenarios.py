from random import randint

import vk_api.bot_longpoll
import handlers
import settings
from settings import TOKEN, GROUP_ID
import logging

log = logging.getLogger('bot')

def configure_logging():
    file_handler = logging.FileHandler(filename='bot.log', mode='a', encoding='utf8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                                datefmt='%d-%b-%Y %H:%M:%S'))
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)


class UserState:
    """
    Состояние пользователя внутри сценария
    """

    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}


class Bot:
    """
    Use Python 3.8
    echo bot for vk
    """

    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.bot_long_poll = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()
        self.user_states = dict()  # user_id -> user_state

    def run(self):
        """
        start bot
        """
        for event in self.bot_long_poll.listen():
            log.info('*' * 5 + 'Получено событие' + '*' * 5)
            try:
                self.on_event(event)
            except Exception as err:
                log.exception(err)

    def on_event(self, event):
        """
        Logging events and reply message

        :param event: event from VkBotLongPoll.listen
        :return: None
        """
        if event.type != vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.error(f'Я не умею обрабатывать событие типа {event.type}')
            return
        user_id = event.message.from_id
        post_text = event.message.text.lower()
        long_poll = vk_api.bot_longpoll

        if user_id in self.user_states:
            text_to_send = self.continue_scenario(user_id, post_text)
        else:
            for intent in settings.INTENTS:
                if any(token in post_text for token in intent['tokens']):
                    if intent['answer']:
                        text_to_send = intent['answer']
                        break
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                        break
            else:
                text_to_send = settings.DEFAULT_ANSWERS

        self.api.messages.send(message=text_to_send,
                               user_id=user_id,
                               random_id=randint(0, 2 ** 64))

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send

    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
                # switch_to_next_step
                return text_to_send
            else:
                self.user_states.pop(user_id)
                return text_to_send
                # finis scenario
        else:
            text_to_send = step['failure_text']
            return text_to_send
            # retry step


if __name__ == '__main__':
    configure_logging()
    bot = Bot(GROUP_ID, TOKEN)
    bot.run()
