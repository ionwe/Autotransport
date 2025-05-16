from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db() 