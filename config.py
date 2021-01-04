import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'6\xe9\xda\xead\x81\xf7\x8d\xbbH\x87\xe8m\xdd3%'
    UPLOAD_PATH = os.getcwd() + '/application/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    