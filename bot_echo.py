from random import randint

import vk_api.bot_longpoll
from settings import TOKEN, GROUP_ID
import logging

log = logging.getLogger('bot')


def configure_logging():
    file_handler = logging.FileHandler(filename='bot.log', mode='a', encoding='utf8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                                datefmt='%d-%b-%Y %H:%M:%S'))
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)


class Bot:
    """ echo bot for vk """

    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.bot_long_poll = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

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
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_TYPING_STATE:
            log.info(f'Мне что-то пишет пользователь id{event.object.from_id}')
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_REPLY:
            log.info(f'Я ответил: {self.msg}')
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.info(f'Я получил сообщение от id{event.message.from_id}: {event.message.text}')
            self.msg = 'Кто сказал ' + event.message.text
            self.api.messages.send(message=self.msg,
                                   user_id=event.message.from_id,
                                   random_id=randint(0, 2 ** 64))
        else:
            log.error(f'Я не умею обрабатывать событие типа {event.type}')


if __name__ == '__main__':
    configure_logging()
    bot = Bot(GROUP_ID, TOKEN)
    bot.run()
