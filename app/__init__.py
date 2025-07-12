from flask import Flask
from dotenv import load_dotenv
import os


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config')

    from .routes.auth import main as main_routes
    app.register_blueprint(main_routes)

    from app.routes.consult import consult_bp
    app.register_blueprint(consult_bp)

    from app.routes.transcript import transcript_bp
    app.register_blueprint(transcript_bp)

    from app.routes.session import session_bp as sessions_bp
    app.register_blueprint(sessions_bp)

    from app.routes.ask_heidi import ask_heidi_bp
    app.register_blueprint(ask_heidi_bp)

    # Add demo blueprint
    from app.routes.demo import demo_bp
    app.register_blueprint(demo_bp)

    return app