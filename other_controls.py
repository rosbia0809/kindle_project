import random
import string
from manipulating_database import get_recent_words, get_all_words

HEADER_SIZE = 20
HOME_COLOUR = 'brown'

def clean_word(text):
    word = ''.join([char for char in text if char not in string.punctuation])
    return word

def new_question():
    recents = get_recent_words()
    all_time = get_all_words()

    if len(recents)<1 or len(all_time)<5:
        return None

    correct = random.choice(recents)

    if not correct.definitions:
        return None

    correct_answer = correct.definitions[0].meaning
    correct_word = correct.word

    other_pool = [
        definition.meaning
        for w in all_time
        if w.word != correct_word
        for definition in w.definitions
    ]

    other_pool = list(set(other_pool))

    if len(other_pool)<3:
        return None

    other_options = random.sample(other_pool, 3)
    all_options = other_options + [correct_answer]
    random.shuffle(all_options)

    '''
    else:
        correct = random.choice(recents)
        if correct.definitions:
            correct_answer = correct.definitions[0].meaning
        else:
            correct_answer = 'No definition avaiable'
        correct_word = correct.word

        other_pool = [
            w.meaning
            for w in all_time
            if w.word != correct_word
        ]
        if len(other_pool)<0:
            return None

        other_options = random.sample(other_pool, 3)

        all_options = other_options + [correct_answer]
        random.shuffle(all_options)
    '''
    return all_options, correct_word, correct_answer

def check_answer(chosen,correct):
    if chosen == correct:
        return True
    else:
        return False