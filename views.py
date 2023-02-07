from flask import Blueprint, render_template, request, url_for, redirect, session
from SpotifyAPI import getartisttopten
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import time
test = []


TOKEN_INFO = "token_info"

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

        trackURIs = []
        try:
            token_info = get_token()
        except:
            print("user not logged in")
            return redirect(url_for("views.home", _external = True))
        sp = spotipy.Spotify(auth = token_info['access_token'])    
        #prints to consol users 50 saved tracks
        all_songs = []
        iteration = 0
     
        if request.method == "POST":
        #checks if access token is expired and gets a refreshed token and check if it has token data
        
       # getting input with name = fname in HTML form
            artist_name = request.form.get("aname")
       # getting input with name = lname in HTML form
            songs = getartisttopten(artist_name)
        
       
            test.clear()
       
            for idx, song in enumerate(songs):
                test.append(f"{idx + 1}. {song['name']}")
        
        while True:
            items = sp.current_user_saved_tracks(limit=50, offset=iteration * 50)['items']
            #track_name = sp.current_user_saved_tracks(limit=50, offset=iteration * 50)['items']
            iteration += 1
            all_songs += items
            if (len(items) < 50):
                break
        print(str(items[0]))
            

           
        return render_template("index.html", your_list = test)

@views.route("/spotifyLogin")    
def spotLogin():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@views.route("/redirect")     
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('views.home', _external=True))

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('views.redirectPage', _external=True),
        scope = "user-library-read"
    ) 

def get_token():
    token_info = session.get(TOKEN_INFO, None)  
    if not token_info:
        raise "exception" 

    now = int(time.time()) 

    is_expired = token_info['expires_at'] - now < 60
    if (is_expired) :
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info    