import io
import json
import collections
from google.cloud import vision
from config import Config
from urllib.request import urlopen
from urllib.parse import quote


def detect_landmarks(path):

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    for landmark in landmarks:
        return landmark


def get_wiki_intro(search):
    url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=' + \
        quote(search)

    v = urlopen(url).read()
    j = json.loads(v)

    pages = j["query"]["pages"]
    p = list(pages)
    page_id = p[0]

    if page_id == '-1':
        extract = None
    else:
        extract = pages[page_id]["extract"]

    return extract


def reverse_geocode(lat, lon):
    key = "AIzaSyDsliI1R8sDXGMUWVcgBl22_ZflbdBZO-Q"
    url = "https://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false&key=%s" % (lat, lon, key)
    v = urlopen(url).read()
    j = json.loads(v)
    components = j['results'][0]['address_components']
    country = postal_code = None
    for c in components:
        if "country" in c['types']:
            country = c['long_name']
        if "postal_code" in c['types']:
            postal_code = c['long_name']

    return postal_code, country


def get_landmark_image(search):
    key = "5LSxHhQ7Am_jUmrirkdHFwECMKQlMjsr7cL55MVckZE"
    url = "https://api.unsplash.com/search/photos/?query=" + quote(search) + "&per_page=1&client_id=" + key

    print(url)

    v = urlopen(url).read()
    j = json.loads(v)
    photo_link = j["results"][0]["urls"]["regular"]

    print(photo_link)

    return photo_link

