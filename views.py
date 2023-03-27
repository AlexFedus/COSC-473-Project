from flask import Blueprint, make_response, render_template, request,  redirect , session, url_for
import requests
from SpotifyAPI import getartisttopten
from SpotifyAPI import get_top_tracks
import spotipy
from spotipy import Spotify
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyOAuth
import datetime
from datetime import timedelta

"""
This file contains all the code for each of the different routes on 
our site.

"""


test = []
finalTrackList = []


SPOTIPY_CLIENT_ID = '83c609c1ed86447ebc5d4ffd526f9730'
SPOTIPY_CLIENT_SECRET = 'ae50126def9a4e96a344385597ab9443'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
SCOPE = 'user-library-read user-read-email user-top-read user-read-private'


views = Blueprint(__name__,"views")

db = SQLAlchemy()


"""
This class defines what information is saved in our
database.
"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    access_token = db.Column(db.String(200))
    refresh_token = db.Column(db.String(200))
    token_expiration = db.Column(db.DateTime)
    display_name = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.spotify_id}>'

# Helper function to get the user's Spotify object
def get_spotify_object(token):
    return Spotify(auth=token)

#The route that displays our homepage
@views.route("/")
def home():
    if not request.cookies.get("user"):
        return render_template("home.html")
    
    spotify = spotipy.Spotify(auth=request.cookies.get("user"))
    user = spotify.current_user()
    
    try:
        profile_picture_url = user["images"][0]["url"]
    except:
        profile_picture_url = url_for('static', filename='images/profilepicimages.png')
        
    topfiftytracks = get_top_tracks()
    return render_template("home.html", top_tracks = topfiftytracks, profile_picture_url=profile_picture_url)

    #top_tracks = get_top_tracks()
    #return render_template("home.html", top_tracks=top_tracks)


    
    
    


    

#This route displays an artists top ten songs on spotify
# It does this by calling a function from "SpotifyAPI.py"

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
                
        spotify = spotipy.Spotify(auth=request.cookies.get("user"))      
        user = spotify.current_user()
        
        try:
            profile_picture_url = user["images"][0]["url"]
        
        except:
            profile_picture_url = url_for('static', filename='images/profilepicimages.png')
        
        
           
        return render_template("index.html", your_list = test, track_list = finalTrackList, profile_picture_url=profile_picture_url)



"""
This route is triggered when a user clicks to log in to spotify
It utilizes our client id and secret to gain an access token

"""
@views.route('/spotifyLogin')
def loginsp():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope='user-library-read user-read-email user-top-read user-read-private'
    )

    #Requesting a code and turning it into a token
    code = request.args.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
       
        
        #Gets the id of who is logging in, if they are not in the database
        #They are added, if they are, their tokens are updated
        #The user is then redirected to the homepage after logging in.
        sp = spotipy.Spotify(auth=access_token)
        user_info = sp.current_user()
        user = User.query.filter_by(spotify_id=user_info['id']).first()
        if not user:
            user = User(
                spotify_id=user_info['id'],
                email=user_info.get('email'),
                access_token=access_token,
                refresh_token=token_info['refresh_token'],
                token_expiration=datetime.fromtimestamp(token_info['expires_at']),
                display_name = user_info['display_name']
            )
            db.session.add(user)
        else:
            user.access_token = access_token
            user.refresh_token = token_info['refresh_token']
            user.token_expiration = datetime.fromtimestamp(token_info['expires_at'])
        db.session.commit()
        session['user'] = {'id': user.id, 'email': user.email, 'display_name' : user.display_name}
        return redirect('/')
    else:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    

# Callback route
@views.route('/callback')
def callback():
    
    
    auth_code = request.args.get('code')

    # Use the auth code to request an access token
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
            display_name = response_data['display_name']
            
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
                user = User(email=email, access_token=access_token, refresh_token=refresh_token, token_expiration=token_expiration, spotify_id = spotify_id, display_name = display_name)
                db.session.add(user)
                db.session.commit()

            # Set the user ID in the session
            session['user_id'] = user.id
            session['email'] = email
            session['display_name'] = display_name

            # Redirect the user to the home page
            #return redirect(url_for('index'))

            resp = make_response(redirect('/'))
            resp.set_cookie('user', user.access_token)
            return resp
            #return redirect('/')
        return 'error'

  
  
    
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
        
        
    spotify = spotipy.Spotify(auth=request.cookies.get("user"))      
    user = spotify.current_user()
    
    try:
        profile_picture_url = user["images"][0]["url"]
        
    except:
        profile_picture_url = url_for('static', filename='images/profilepicimages.png')
       
    return render_template('liked-songs.html', liked_songs=liked_songs, profile_picture_url = profile_picture_url)

# Clears the cookie to logout            
@views.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('session', '', expires=0)
    return resp


#Gets the users top songs from each of the three terms that the spotify api allows
@views.route('/mytop')
def topusersongs():
    
    
    spotify = spotipy.Spotify(auth=request.cookies.get("user"))
    
    
    shortterm = spotify.current_user_top_tracks(limit=20, offset=0, time_range='short_term')
    shortterm_tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in shortterm["items"]]

    mediumterm = spotify.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
    mediumterm_tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in mediumterm["items"]]

    longterm = spotify.current_user_top_tracks(limit=20, offset=0, time_range='long_term')
    longterm_tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in longterm["items"]]

    spotify = spotipy.Spotify(auth=request.cookies.get("user"))      
    user = spotify.current_user()

    try:
            profile_picture_url = user["images"][0]["url"]
        
    except:
            profile_picture_url = url_for('static', filename='images/profilepicimages.png')
        
    return render_template('usertop.html', shortterm=shortterm_tracks, mediumterm=mediumterm_tracks, longterm=longterm_tracks, profile_picture_url=profile_picture_url)

#Gets a users top artists
@views.route('/mytopartists')
def topuserartists():
    
    spotify = spotipy.Spotify(auth=request.cookies.get("user"))
    
    # Retrieve the user's top artists from Spotify's API
    short_term = spotify.current_user_top_artists(limit=20, offset=0, time_range='short_term')
    medium_term = spotify.current_user_top_artists(limit=20, offset=0, time_range='medium_term')
    long_term = spotify.current_user_top_artists(limit=20, offset=0, time_range='long_term')
    
    print(short_term)

    spotify = spotipy.Spotify(auth=request.cookies.get("user"))      
    user = spotify.current_user()
        
    try:
        profile_picture_url = user["images"][0]["url"]
        
    except:
        profile_picture_url = url_for('static', filename='images/profilepicimages.png')

    # Render the template with the top artists data
    return render_template('user_top_artists.html', short_term=short_term, medium_term=medium_term, long_term=long_term, profile_picture_url=profile_picture_url)

