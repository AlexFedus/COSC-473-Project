from flask import Blueprint, render_template, request, url_for, redirect , session
from SpotifyAPI import getartisttopten, getUserSavedTracks
from dotenv import load_dotenv
import os
import spotipy

from spotipy.oauth2 import SpotifyOAuth
import time



test = []
finalTrackList = []


SPOTIPY_CLIENT_ID = '83c609c1ed86447ebc5d4ffd526f9730'
SPOTIPY_CLIENT_SECRET = 'ae50126def9a4e96a344385597ab9443'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
SCOPE = 'user-library-read,user-read-email'


views = Blueprint(__name__,"views")

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/login", methods=["POST", "GET"])
def loginapp():
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
        #checks if access token is expired and gets a refreshed token and check if it has token data
        
       # getting input with name = fname in HTML form
            artist_name = request.form.get("aname")
       # getting input with name = lname in HTML form
            songs = getartisttopten(artist_name)
        
       
            test.clear()
       
            for idx, song in enumerate(songs):
                test.append(f"{idx + 1}. {song['name']}")
        
       
        """    
        tracks = getUserSavedTracks()
        #inc = 0
        for idx, track in enumerate(tracks):
            if idx == 50:
                break
            finalTrackList.append(f"{idx + 1}. {track['track']['name']}")
        """
            
           
        return render_template("index.html", your_list = test, track_list = finalTrackList)
#@views.route("/artist", methods =["GET", "POST"])
#def userTracks():
        #tracks = getUserSavedTracks()
        #inc = 0
        #for idx, track in enumerate(tracks):
            #if idx == 50:
                #break
            #finalTrackList.append(f"{idx + 1}. {track['track']['name']}")
            #print(track['track']['name'])
            
            
           
        #return render_template("index.html", track_list = finalTrackList)


@views.route("spotifyLogin")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@views.route("/callback")     
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session_id = session.sid
    session_data = session.get('spotify_tokens', {})
    session_data[session_id] = token_info['access_token']
    session['spotify_tokens'] = session_data
    return redirect('/currentuser')


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="83c609c1ed86447ebc5d4ffd526f9730",
        client_secret="ae50126def9a4e96a344385597ab9443",
        redirect_uri=url_for('views.callback', _external=True),
        scope="user-library-read"
    )
    
    
@views.route("/logout")
def logout():
    session.clear()
    return redirect('/') 

@views.route("/currentuser")
def cuser():
    if 'access_token' not in session:
        return redirect('/login')
    access_token = session['access_token']
    sp = spotipy.Spotify(auth=access_token)
    user = sp.current_user()
    return f'Logged in as {user["display_name"]}'