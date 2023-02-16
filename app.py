from flask import Flask, request, url_for, session, redirect
from views import views
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
import os
import spotipy
from flask_session import Session


#from SpotifyAPI import songs


app = Flask(__name__)

app.secret_key = "0afafa34v"




app.register_blueprint(views, url_prefix="/")



if __name__ == "__main__":
    app.run(debug=True, port=8000)
