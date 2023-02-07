from flask import Blueprint, render_template, request, url_for, redirect
from SpotifyAPI import getartisttopten
from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyOAuth
test = []




views = Blueprint(__name__,"views")

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        print(user)
        return render_template("login.html")
        #return redirect(url_for("user", usr = user))
    else:
        return render_template("login.html")
    

#@views.route("/<usr>")
#def user(usr):
    #return f"<h1>{views.usr}</h1>"

@views.route("/artist", methods =["GET", "POST"])
def artist():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       artist_name = request.form.get("aname")
       # getting input with name = lname in HTML form
       songs = getartisttopten(artist_name)
        
       
       test.clear()
       
       for idx, song in enumerate(songs):
            test.append(f"{idx + 1}. {song['name']}")
       
       
    return render_template("index.html", your_list = test)

@views.route("/spotifyLogin")    
def spotLogin():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@views.route("/redirect")     
def redirectPage():
    return 'redirect'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('views.redirectPage', _external=True),
        scope = "user-library-read"
    ) 