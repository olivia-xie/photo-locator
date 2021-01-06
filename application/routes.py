import os
import json
import shutil
from application import app
from flask import render_template, request, redirect, url_for
from flask_dropzone import Dropzone
from application.api_helper import detect_landmarks, get_wiki_intro, reverse_geocode, get_landmark_image
from urllib.request import urlopen


# Dropzone settings
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.jpg, .jpeg, .png'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['DROPZONE_UPLOAD_ON_CLICK'] = True
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

dropzone = Dropzone(app)

filename = "default.jpeg"


@app.route('/', methods=['POST', 'GET'])
def upload():
    global filename

    if request.method == 'POST':
        for key, f in request.files.items():
            filename = f.filename
            if key.startswith('file'):
                f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))

    return render_template('index.html')


@app.route('/results', methods=['POST', 'GET'])
def results():
    global filename
    path = os.path.join(app.config['UPLOAD_PATH'], filename)

    landmark = detect_landmarks(path)

    if landmark is None:
        postal_code = country = map_url = extract = pic = None
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
        pic = get_landmark_image(landmark.description)


    return render_template('results.html', landmark=landmark, mapurl=map_url, extract=extract, picurl=pic)

