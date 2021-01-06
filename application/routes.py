import os
from application import app
from flask import render_template, request, redirect, url_for
from flask_dropzone import Dropzone
from application.image_processing.detect_landmark import detect_landmarks
from application.image_processing.wiki_blurb import get_wiki_intro
from urllib.request import urlopen
import json
import shutil

# Dropzone settings
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.jpg, .jpeg, .png'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['DROPZONE_UPLOAD_ON_CLICK'] = True
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

dropzone = Dropzone(app)

filename = "default.jpeg"


def reverse_geocode(lat, lon):
    key = "AIzaSyDsliI1R8sDXGMUWVcgBl22_ZflbdBZO-Q"
    url = "https://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false&key=%s" % (lat, lon, key)
    print(url)
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


@app.route('/', methods=['POST', 'GET'])
def upload():
    global filename

    if request.method == 'POST':
        for key, f in request.files.items():
            filename = f.filename
            print(filename)
            if key.startswith('file'):
                f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))

    return render_template('index.html')


@app.route('/results', methods=['POST', 'GET'])
def results():
    global filename
    path = os.path.join(app.config['UPLOAD_PATH'], filename)

    landmark = detect_landmarks(path)

    if landmark is None:
        postal_code = country = map_url = extract = None
    else:
        loc = reverse_geocode(landmark.locations[0].lat_lng.latitude,
                              landmark.locations[0].lat_lng.longitude)
        postal_code = loc[0]
        country = loc[1]

        map_url = 'https://www.google.com/maps/embed/v1/place?key=AIzaSyDsliI1R8sDXGMUWVcgBl22_ZflbdBZO-Q&q=' + \
            landmark.description + ','
        if(postal_code is not None):
            map_url += postal_code
        if(country is not None):
            map_url += country

        extract = get_wiki_intro(landmark.description)

        print(postal_code)
        print(country)
        print(map_url)

    return render_template('results.html', landmark=landmark, mapurl=map_url, extract=extract)

