import string

HEADER_SIZE = 20
HOME_COLOUR = 'brown'
bg_colour= '#f2e9dc'
font = 'Ariel'

def clean_word(text):
    word = ''.join([char for char in text if char not in string.punctuation])
    return word