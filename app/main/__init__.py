from flask import Flask
from flask_bcrypt import Bcrypt

from .config import config_by_name

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['UPLOAD_FOLDER'] = "./app/main/images"
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    """flask_bcrypt.init_app(app)"""
    return app