from flask import Flask, request, url_for, session, redirect
from views import views
from views import db
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
import os
import spotipy
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyOAuth


#from SpotifyAPI import songs


app = Flask(__name__)

app.secret_key = "0afafa34v"
#app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql9598812:uJVAVztfRj@sql9.freesqldatabase.com:3306/sql9598812'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




app.register_blueprint(views, url_prefix="/")



if __name__ == "__main__":
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True, port=8000)
