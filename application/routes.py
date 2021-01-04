import os
from application import app
from flask import render_template, request
from flask_dropzone import Dropzone

# Dropzone settings
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['DROPZONE_UPLOAD_ON_CLICK'] = True

dropzone = Dropzone(app)


@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        for key, f in request.files.items():
            if key.startswith('file'):
                f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
    return render_template('index.html')

