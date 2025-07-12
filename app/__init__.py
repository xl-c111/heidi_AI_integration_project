# app/__init__.py - Fixed with better error handling and imports
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables first
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config')

    # Import and register blueprints with error handling
    try:
        # Main routes (auth)
        from app.routes.auth import main as main_routes
        app.register_blueprint(main_routes)
        print("✅ Auth routes registered")
    except ImportError as e:
        print(f"❌ Failed to import auth routes: {e}")

    try:
        # Consult routes
        from app.routes.consult import consult_bp
        app.register_blueprint(consult_bp)
        print("✅ Consult routes registered")
    except ImportError as e:
        print(f"❌ Failed to import consult routes: {e}")

    try:
        # Transcript routes
        from app.routes.transcript import transcript_bp
        app.register_blueprint(transcript_bp)
        print("✅ Transcript routes registered")
    except ImportError as e:
        print(f"❌ Failed to import transcript routes: {e}")

    try:
        # Session routes
        from app.routes.session import session_bp as sessions_bp
        app.register_blueprint(sessions_bp, url_prefix="/sessions")
        print("✅ Session routes registered")
    except ImportError as e:
        print(f"❌ Failed to import session routes: {e}")

    try:
        # Ask Heidi routes
        from app.routes.ask_heidi import ask_heidi_bp
        app.register_blueprint(ask_heidi_bp)
        print("✅ Ask Heidi routes registered")
    except ImportError as e:
        print(f"❌ Failed to import ask_heidi routes: {e}")
        print("This might be due to missing enhanced functions - continuing without enhanced ask_heidi")

    try:
        # Demo routes
        from app.routes.demo import demo_bp
        app.register_blueprint(demo_bp)
        print("✅ Demo routes registered")
    except ImportError as e:
        print(f"❌ Failed to import demo routes: {e}")

    try:
        # Document routes
        from app.routes.document import document_bp
        app.register_blueprint(document_bp)
        print("✅ Document routes registered")
    except ImportError as e:
        print(f"❌ Failed to import document routes: {e}")

    # Add a simple health check route
    @app.route('/health')
    def health_check():
        return {
            "status": "healthy",
            "message": "Heidi AI Integration Server is running",
            "endpoints": [
                "/demo",
                "/test-jwt",
                "/test-session",
                "/debug-api",
                "/process-document",
                "/ask-question"
            ]
        }

    # Add environment check route
    @app.route('/env-check')
    def env_check():
        env_vars = {
            "HEIDI_API_KEY": bool(os.getenv("HEIDI_API_KEY")),
            "HEIDI_EMAIL": bool(os.getenv("HEIDI_EMAIL")),
            "HEIDI_USER_ID": bool(os.getenv("HEIDI_USER_ID"))
        }
        all_set = all(env_vars.values())
        return {
            "all_env_vars_set": all_set,
            "env_vars": env_vars,
            "message": "All environment variables set" if all_set else "Some environment variables missing"
        }

    print(f"🚀 Flask app created successfully!")
    return app