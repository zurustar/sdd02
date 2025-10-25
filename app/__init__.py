from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    login.login_view = 'main.login' # Blueprint名を指定
    login.login_message_category = 'info'

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

