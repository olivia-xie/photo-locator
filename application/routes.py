import os
import json
import shutil
import glob
import time
import boto3
import botocore
from application import app
from flask import render_template, request, redirect, url_for
from flask_dropzone import Dropzone
from application.api_helper import detect_landmarks, get_wiki_intro, reverse_geocode, get_landmark_image
from urllib.request import urlopen
from werkzeug.utils import secure_filename


# AWS Bucket Config
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET
)

# Dropzone settings
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.jpg, .jpeg, .png'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['DROPZONE_UPLOAD_ON_CLICK'] = True
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

dropzone = Dropzone(app)

filename = None


def upload_file_to_s3(file, bucket_name, acl="public-read"):

    s3.upload_fileobj(
        file,
        bucket_name,
        file.filename,
        ExtraArgs={
            "ACL": acl,
            "ContentType": file.content_type
        }
    )

    return "{}{}".format(S3_LOCATION, file.filename)


@app.route('/', methods=['POST', 'GET'])
def upload():
    global filename

    if request.method == 'POST':
        for key, f in request.files.items():
            if key.startswith('file'):
                f.filename = secure_filename(f.filename)
                output = upload_file_to_s3(f, S3_BUCKET)
                filename = str(output)

    return render_template('index.html')


@app.route('/results', methods=['POST', 'GET'])
def results():
    global filename
    
    landmark = detect_landmarks(filename)

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
