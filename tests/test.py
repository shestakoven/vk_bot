from unittest import TestCase
from unittest.mock import Mock, patch, ANY

from bot import Bot
from vk_api.bot_longpoll import VkBotMessageEvent


class TestBot(TestCase):
    EVENT_RAW = {'type': 'message_new',
                 'object':
                     {'message':
                          {'date': 0, 'from_id': 00, 'id': 0, 'out': 0,
                           'peer_id': 0, 'text': 'hello', 'conversation_message_id': 0, 'fwd_messages': [],
                           'important': False, 'random_id': 0, 'attachments': [], 'is_hidden': False},
                      'client_info':
                          {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link'],
                           'keyboard': True, 'inline_keyboard': True, 'carousel': False, 'lang_id': 0}},
                 'group_id': 0, 'event_id': '52c8a086c0073b3fba80df8305c3d6806e577eca'}

    def test_run(self):
        count = 5
        obj = {}
        events = [obj] * count
        vk_bot_long_poll_listen_mock = Mock()
        vk_bot_long_poll_listen_mock.listen = Mock(return_value=events)
        with patch('bot.vk_api.VkApi'):
            with patch('bot.vk_api.bot_longpoll.VkBotLongPoll', return_value=vk_bot_long_poll_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()
                bot.on_event.assert_called()
                bot.on_event.assert_called_with(obj)
                assert bot.on_event.call_count == count

    def test_on_event(self):
        event = VkBotMessageEvent(raw=self.EVENT_RAW)
        send_mock = Mock()

        with patch('bot.vk_api.VkApi'):
            with patch('bot.vk_api.bot_longpoll.VkBotLongPoll'):
                bot = Bot('', '')
                bot.api = Mock()
                bot.api.messages.send = send_mock
                bot.on_event(event)
                bot.msg = self.EVENT_RAW['object']['message']['text']
                send_mock.assert_called_once_with(
                    message='Кто сказал ' + bot.msg,
                    user_id=event.message.from_id,
                    random_id=ANY
                )
