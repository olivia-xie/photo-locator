import os
from application import app
from flask import render_template, request, redirect, url_for
from flask_dropzone import Dropzone
from application.image_processing.detect_landmark import detect_landmarks

# Dropzone settings
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.jpg, .jpeg, .png'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['DROPZONE_UPLOAD_ON_CLICK'] = True
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

dropzone = Dropzone(app)

filename = None


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
    detect_landmarks(os.path.join(app.config['UPLOAD_PATH'], filename))
    return render_template('results.html', file_name = filename)
