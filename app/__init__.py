from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config')

    from .routes.auth import main as main_routes
    app.register_blueprint(main_routes)

    from .routes.consult import main as main_consult_routes
    app.register_blueprint(main_consult_routes)
    return app

