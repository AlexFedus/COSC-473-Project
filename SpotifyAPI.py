from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


test = []
userSavedTracks = []
json_results = []

TOKEN_INFO = "token_info"

"""
This function is used to retrieve an artist from spotify's
top ten songs. It is called in the views file.

"""

def getartisttopten(artist):
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    #This inner function gets a token. NOTE, a user does not need to be logged in for this
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


    #This inner function is how the search bar works for an artist
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

    #This function makes the api call and returns a json response
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



#For top 50 songs in USA on homepage
def get_top_tracks():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # Set up Spotipy client
    client_credentials_manager = SpotifyClientCredentials (
        client_id = client_id,
        client_secret = client_secret
    ) 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Get tracks from "Top 50 - USA" playlist
    playlist = sp.user_playlist_tracks(user='spotify', playlist_id='37i9dQZEVXbLRQDuF5jeBp', limit=50)

    # Extract relevant information for each track
    top_tracks = []
    for item in playlist['items']:
        track = item['track']
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'image': track['album']['images'][0]['url']
        }
        top_tracks.append(track_info)

    return top_tracks