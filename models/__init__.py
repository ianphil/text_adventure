from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_app(app):
    """Initialize the SQLAlchemy app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()