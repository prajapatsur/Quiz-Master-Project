from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#database creation
db= SQLAlchemy()
login_manager= LoginManager()

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']= "mysecretkey"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///quiz_master.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    return app