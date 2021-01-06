from urllib.parse import quote
from urllib.request import urlopen
import json
import collections

def get_wiki_intro(search):
    url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=' + quote(search)

    print(url)
    v = urlopen(url).read()
    j = json.loads(v)

    pages = j["query"]["pages"]
    p = list(pages)
    page_id = p[0]

    if page_id == '-1':
        extract = "No information was found on this landmark."
    else:
        extract = pages[page_id]["extract"]

    return extract
