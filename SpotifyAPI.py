from dotenv import load_dotenv
from flask import url_for, redirect, session ,request
import os
import base64
from requests import post, get
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import time

test = []
userSavedTracks = []
json_results = []

TOKEN_INFO = "token_info"

def getartisttopten(artist):
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    def get_token():
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token

    def get_auth_header(token):
        return {"Authorization": "Bearer " + token}

    def search_for_artist(token, artist_name):
        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        query = f"?q={artist_name}&type=artist&limit=1"

        query_url = url + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)["artists"]["items"]
        if len(json_result) == 0:
            print("No artist with this name exists...")
            return None

        return json_result[0]

    def get_songs_by_artist(token, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["tracks"]
        return json_result


    token = get_token()
    result = search_for_artist(token, artist)
    artist_id = result["id"]
    songs = get_songs_by_artist(token, artist_id)

    return songs



def getUserSavedTracks():
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

    while True:
            items = sp.current_user_saved_tracks(limit=50, offset=iteration * 50)['items']
            iteration += 1
            all_songs += items
            if (len(items) < 50):
                print(sp.current_user())
                break
            
            
    #json_result = items[0]
    #for item in items:
        #tracks = json_result['track']['name']
    return all_songs


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

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('views.redirectPage', _external=True),
        scope = "user-library-read"
    ) 



def logout_spotify():
    # Remove the token info from the session
    session.pop(TOKEN_INFO, None)

    # Create a SpotifyOAuth instance
    sp_oauth = create_spotify_oauth()

    # Get the logout URL with show_dialog=True
    logout_url = sp_oauth.get_authorize_url(show_dialog=True)

    # Redirect the user to the Spotify logout page
    return redirect(logout_url)
