from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from views import views
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
import os
import spotipy


#from SpotifyAPI import songs


app = Flask(__name__)

app.secret_key = "0afafa34v"
app.config['SESSION_COOKIE_NAME'] = 'COSC Cookie'



app.register_blueprint(views, url_prefix="/")



if __name__ == "__main__":
    app.run(debug=True, port=8000)


#Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']