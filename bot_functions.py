from conf import MODEL_PATH, PHRASES_PATH
import pickle
import json
import random
import numpy as np


def load_model():
    with open(MODEL_PATH, 'rb') as f:
        sentiment_model = pickle.load(f)

    return sentiment_model


def load_phrases():
    with open(PHRASES_PATH, encoding='utf-8') as f:
        phrases = json.load(f)

    return phrases


def restore_state():
    return 0


def update_state(estimation, user_id, user_states):
    if user_id not in user_states:
        state = 0
    else:
        state = user_states[user_id]
    new_state = state + 0.2 * estimation
    if new_state < 0:
        new_state = max(new_state, -1)
    elif new_state > 0:
        new_state = min(new_state, 1)

    return new_state


def estimate_sentiment(text, model):
    def scale_prob(prob):
        return prob * 2 - 1

    sentiment = scale_prob(model.predict_proba([text])[0][1])

    return sentiment


def generate_reply(estimation, phrases, n_closest=200):
    phrases = sorted(phrases, key=lambda x: np.abs(x[1] - estimation))[:n_closest]
    output = random.choice(phrases)
    # output = '\n'.join([output[0], str(round(output[1], 2))])
    output = output[0]

    return output
