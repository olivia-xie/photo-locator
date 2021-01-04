import os
from application import app
from flask import render_template, request, redirect, url_for
from flask_dropzone import Dropzone
from PIL import Image
from application.image_processing.detect_landmark import detect_landmarks
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
    v = urlopen(url).read()
    j = json.loads(v)
    components = j['results'][0]['address_components']
    country = town = None
    for c in components:
        if "country" in c['types']:
            country = c['long_name']
        if "postal_town" in c['types']:
            town = c['long_name']

    return town, country


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
        city = country = None
    else:
        loc = reverse_geocode(landmark.locations[0].lat_lng.latitude,
                    landmark.locations[0].lat_lng.longitude)
        city = loc[0]
        country = loc[1]

    return render_template('results.html', landmark=landmark, city=city, country=country)
