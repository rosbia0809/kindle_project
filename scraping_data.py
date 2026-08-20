import gutenbergpy.textget as g_tg # for get_book
import requests
from bs4 import BeautifulSoup
from thefuzz import fuzz
import json

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

def get_gutenberg_details(search):

    #getting the content of project gutenberg
    URL = f"https://www.gutenberg.org/ebooks/search/?query={search}&submit_search=Go%21"

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    #looking into the content page
    results = soup.find(id="content")
    #returning all the values that have an href
    m_results = results.find_all(href = True)

    #trying to see if the values in m_results match up to the book
    t_results = results.find_all('span', {'class':'title'})[1]
    a_results = results.find_all('span', {'class':'subtitle'})[1]
    scr = fuzz.ratio(search, t_results.text)
    print (scr)
    if scr < 60:
        return None

    else:
        found = False
        count = 0

        while not found:
            item = m_results[count]

            href = item['href']

            if href[8:].isdigit():
                g_id = href[8:]
                found = True
            else:
                count = count + 1

        return t_results.text, a_results.text, int(g_id)

def get_book(g_id):
    # download the book via its id
    # to find a book's ID, look it up on the gutenberg website (the number in its URL is the ID)
    raw_book = g_tg.get_text_by_id(g_id)

    # strip the Gutenberg header/footer boilerplate
    clean_book = g_tg.strip_headers(raw_book)

    # decodes the bytes to a string
    text = clean_book.decode('utf-8')
    return text