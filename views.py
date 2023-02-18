from flask import Blueprint, render_template, request, url_for, redirect , session
from SpotifyAPI import getartisttopten, getUserSavedTracks
from dotenv import load_dotenv
import os
import spotipy

from spotipy import Spotify, util
import time
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from datetime import timedelta



test = []
finalTrackList = []


SPOTIPY_CLIENT_ID = '83c609c1ed86447ebc5d4ffd526f9730'
SPOTIPY_CLIENT_SECRET = 'ae50126def9a4e96a344385597ab9443'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
SCOPE = 'user-library-read,user-read-email'


views = Blueprint(__name__,"views")

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    access_token = db.Column(db.String(200))
    refresh_token = db.Column(db.String(200))
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.spotify_id}>'

# Helper function to get the user's Spotify object
def get_spotify_object(token):
    return Spotify(auth=token)

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


@views.route('/spotifyLogin')
def loginsp():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )

    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Callback route
@views.route('/callback')
def callback():
    
    
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope='user-library-read'
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']
    expires_in = token_info['expires_in']
    
    sp = spotipy.Spotify(auth=access_token)
    user_info = sp.current_user()
    user_id = user_info['id']
    email = user_info['email']

    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_expiration = datetime.now() + timedelta(seconds=expires_in)
    else:
        # Create a new user
        user = User(
            id=user_id,
            email=email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiration=datetime.now() + timedelta(seconds=expires_in)
        )
        db.session.add(user)
    db.session.commit()
    
    """
    user = User(
        access_token=access_token,
        refresh_token=refresh_token,
        token_expiration=datetime.now() + timedelta(seconds=expires_in)
    )
    db.session.add(user)
    db.session.commit()

    """
    return email
    
# Top songs route
@views.route('/top_songs')
def top_songs():
    # Get the user's access token from the database
    user = User.query.filter_by(id=session['user_id']).first()
    token = user.access_token

    # Get the user's top tracks from Spotify
    spotify = get_spotify_object(token)
    top_tracks = spotify.current_user_top_tracks(limit=10, time_range='short_term')['items']

    # Render the top songs template with the user's top tracks
    return render_template('top_songs.html', top_tracks=top_tracks)