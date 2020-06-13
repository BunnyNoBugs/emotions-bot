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
                if event.object.message['text'] == '/sorry':
                    user_states[user_id] = restore_state()
                    vk.messages.send(
                        user_id=user_id,
                        random_id=random.getrandbits(50),
                        message='Ладно, прощаю'
                    )
                    send_state(user_id, user_states)
                else:
                    estimation = estimate_sentiment(event.object.message['text'], sentiment_model)
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
