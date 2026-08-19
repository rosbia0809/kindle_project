import requests
import json
from bs4 import BeautifulSoup

class NoDefinition(Exception):
    pass

def get_word_definitions(search):
    dict = f'https://api.dictionaryapi.dev/api/v2/entries/en/{search}'

    page = requests.get(dict)
    soup = BeautifulSoup(page.content, 'html.parser')

    definitions = []

    for element in soup:
        data = json.loads(element.text)

        if 'title' in data:
            raise NoDefinition
        else:
            for word in data:
                for meaning in word['meanings']:
                    first_atr = meaning['definitions'][0]
                    definitions.append(first_atr['definition'])

    return definitions