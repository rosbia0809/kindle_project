import random
import string
from manipulating_database import get_recent_words, get_all_words

HEADER_SIZE = 20
HOME_COLOUR = 'brown'
bg_colour= '#f2e9dc'
font = 'Ariel'

def clean_word(text):
    word = ''.join([char for char in text if char not in string.punctuation])
    return word

def new_question():
    recents = get_recent_words()
    all_time = get_all_words()

    if len(recents)<1 or len(all_time)<5:
        return None
    else:
        correct = random.choice(recents)
        correct_answer = correct.meaning
        correct_word = correct.word

        other_pool = [w.meaning for w in all_time if w.word != correct_word]
        other_options = random.sample(other_pool, 3)

        all_options = other_options + [correct_answer]
        random.shuffle(all_options)

        return all_options, correct_word, correct_answer

def check_answer(chosen,correct):
    if chosen == correct:
        return True
    else:
        return False