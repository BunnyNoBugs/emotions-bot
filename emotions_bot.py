import random

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from conf import TOKEN, GROUP_ID
from bot_functions import *

vk_session = VkApi(token=TOKEN)
long_poll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()

sentiment_model = load_model()

generated_phrases = load_phrases()

user_states = {}


def send_help(user_id):
    vk.messages.send(
        user_id=user_id,
        random_id=random.getrandbits(50),
        message='''
                Привет! 
                Я оцениваю тональность тональность ваших сообщений и присылаю фразы с близкой тональностью в ответ.
                Кроме того, мое отношение к вам меняется от отрицительного (-1) до положительного (1) в зависимости от того, что вы мне пишете.

                Возможные команды:

                /help – получить помощь
                /state – узнать мое отношение к вам
                /sorry – обнулить мое отношение к вам
                '''
    )


def send_state(user_id, user_states):
    vk.messages.send(
        user_id=user_id,
        random_id=random.getrandbits(50),
        message=f'Сейчас мое отношение к вам {round(user_states[user_id], 2)}'
    )


def new_message_timeout_error(user_id):
    vk.messages.send(
        user_id=user_id, random_id=random.getrandbits(50),
        message='Я очень долго думаю, давайте еще раз'
    )


def new_message_error(user_id):
    print(event)
    vk.messages.send(
        user_id=user_id, random_id=random.getrandbits(50),
        message='Что-то совсем сломалось, давайте еще раз'
    )


if __name__ == '__main__':
    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.object.message['from_id']
            try:
                message_text = event.object.message['text']
                if message_text == '/help':
                    send_help(user_id)
                elif message_text == '/sorry':
                    user_states[user_id] = restore_state()
                    vk.messages.send(
                        user_id=user_id,
                        random_id=random.getrandbits(50),
                        message='Хорошо, давайте начнем все сначала'
                    )
                    send_state(user_id, user_states)
                elif message_text == '/state':
                    if user_id not in user_states:
                        user_states[user_id] = restore_state()
                    send_state(user_id, user_states)
                else:
                    estimation = estimate_sentiment(message_text, sentiment_model)
                    user_states[user_id] = update_state(estimation, user_id, user_states)
                    reply = generate_reply(estimation, generated_phrases)
                    vk.messages.send(
                        user_id=user_id,
                        random_id=random.getrandbits(50),
                        message=reply
                    )
                    send_state(user_id, user_states)
            except TimeoutError:
                new_message_timeout_error(user_id)
            except:
                new_message_error(user_id)
