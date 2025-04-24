# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from .routes import api as ping_ns  # 위에서 만든 Namespace

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)

    # Swagger API 등록
    api = Api(app, title="My Flask API", version="1.0", doc="/docs")  # <-- Swagger UI: /docs
    api.add_namespace(ping_ns, path="/api/ping")

    return app
