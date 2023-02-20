from flask import Blueprint, make_response, render_template, request, url_for, redirect , session
import requests
from SpotifyAPI import getartisttopten, getUserSavedTracks
from dotenv import load_dotenv
import os
import spotipy

from spotipy import Spotify, util
import time
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyOAuth
import datetime
from datetime import timedelta




test = []
finalTrackList = []


SPOTIPY_CLIENT_ID = '83c609c1ed86447ebc5d4ffd526f9730'
SPOTIPY_CLIENT_SECRET = 'ae50126def9a4e96a344385597ab9443'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
SCOPE = 'user-library-read user-read-email user-top-read user-read-private'


views = Blueprint(__name__,"views")

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(100), nullable=False)
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
        scope='user-library-read user-read-email user-read-private'
    )

    code = request.args.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
       
        
        
        sp = spotipy.Spotify(auth=access_token)
        user_info = sp.current_user()
        user = User.query.filter_by(spotify_id=user_info['id']).first()
        if not user:
            user = User(
                spotify_id=user_info['id'],
                email=user_info.get('email'),
                access_token=access_token,
                refresh_token=token_info['refresh_token'],
                token_expiration=datetime.fromtimestamp(token_info['expires_at'])
            )
            db.session.add(user)
        else:
            user.access_token = access_token
            user.refresh_token = token_info['refresh_token']
            user.token_expiration = datetime.fromtimestamp(token_info['expires_at'])
        db.session.commit()
        session['user'] = {'id': user.id, 'email': user.email}
        print(access_token)
        return redirect('/')
    else:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    

# Callback route
@views.route('/callback')
def callback():
    
    
    auth_code = request.args.get('code')

    # Use the authorization code to request an access token
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': SPOTIPY_REDIRECT_URI,
        'client_id': SPOTIPY_CLIENT_ID,
        'client_secret': SPOTIPY_CLIENT_SECRET
    })

    # Parse the response and extract the access token
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        
        print("callback function:" + access_token)
        
        refresh_token = response_data['refresh_token']
        token_expiration = datetime.datetime.now() + timedelta(seconds=response_data['expires_in'])

        # Use the access token to get the user's Spotify profile information
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        print(response.text)

        # Parse the response and extract the user's email address
        if response.status_code == 200:
            response_data = response.json()
            email = response_data['email']
            spotify_id = response_data['id']
            
            print(email)

            # Check if the user already exists in the database
            user = User.query.filter_by(email=email).first()

            if user:
                # Update the user's access token, refresh token, and token expiry
                user.access_token = access_token
                user.spotify_id = spotify_id
                
                if token_expiration > user.token_expiration:
                    user.token_expiration = token_expiration
                
                if user.token_expiration < datetime.datetime.now():
                    response = requests.post('https://accounts.spotify.com/api/token', data={
                        'grant_type': 'refresh_token',
                        'refresh_token': user.refresh_token,
                        'client_id': SPOTIPY_CLIENT_ID,
                        'client_secret': SPOTIPY_CLIENT_SECRET
                    })
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        user.access_token = response_data['access_token']
                        user.token_expiration = datetime.datetime.now() + timedelta(seconds=response_data['expires_in'])
                    
                db.session.commit()
            else:
                # Create a new user record in the database
                user = User(email=email, access_token=access_token, refresh_token=refresh_token, token_expiration=token_expiration, spotify_id = spotify_id)
                db.session.add(user)
                db.session.commit()

            # Set the user ID in the session
            session['user_id'] = user.id
            session['email'] = email

            # Redirect the user to the home page
            #return redirect(url_for('index'))

            return redirect('/')
        return 'error'
"""
def callback():
    
    
    auth_code = request.args.get('code')

    # Use the authorization code to request an access token
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': SPOTIPY_REDIRECT_URI,
        'client_id': SPOTIPY_CLIENT_ID,
        'client_secret': SPOTIPY_CLIENT_SECRET
    })

    # Parse the response and extract the access token
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        
        print("callback function:" + access_token)
        
        refresh_token = response_data['refresh_token']
        token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=response_data['expires_in'])

        # Use the access token to get the user's Spotify profile information
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)

        # Parse the response and extract the user's email address
        if response.status_code == 200:
            response_data = response.json()
            email = response_data['email']
            spotify_id = response_data['id']
            
            print(email)

            # Check if the user already exists in the database
            user = User.query.filter_by(email=email).first()

            if user:
                # Update the user's access token, refresh token, and token expiry
                user.access_token = access_token
                user.refresh_token = refresh_token
                user.token_expiration = token_expiration
                user.spotify_id = spotify_id
                db.session.commit()
            else:
                # Create a new user record in the database
                user = User(email=email, access_token=access_token, refresh_token=refresh_token, token_expiration=token_expiration, spotify_id = spotify_id)
                db.session.add(user)
                db.session.commit()

            # Set the user ID in the session
            session['user_id'] = user.id
            session['email'] = email

            # Redirect the user to the home page
            #return redirect(url_for('index'))

            return redirect('/')
        return 'error'
    # If there was an error, redirect the user to an error page
    
"""
  
  
    
# Top songs route
@views.route('/liked-songs')
def liked_songs():
    
    
    user_id = session.get('user_id')
    if not user_id:
        # If the user is not logged in, redirect them to the login page
        return redirect('/spotifyLogin')
    
    # Retrieve the user's access token from the database
    user = User.query.filter_by(email=session['email']).first()
    access_token = user.access_token
    print(access_token)
    
    # Make a request to the Spotify API for the user's saved tracks (i.e., liked songs)
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get('https://api.spotify.com/v1/me/tracks', headers=headers, params={'limit': 10})
    print(response.text)
    
    # Parse the response and extract the relevant information
    if response.status_code == 200:
        data = response.json()
        
        liked_songs = []
        for item in data['items']:
            track = item['track']
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            album_art = track['album']['images'][0]['url']
            liked_songs.append({'name': song_name, 'artist': artist_name, 'image': album_art})
    else:
        liked_songs = None
       
    return render_template('liked-songs.html', liked_songs=liked_songs)
            
@views.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('session', '', expires=0)
    return resp



    
    