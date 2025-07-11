from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config')

    from .routes import main
    app.register_blueprint(main)

    return app
