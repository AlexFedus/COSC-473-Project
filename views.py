from flask import Blueprint, render_template, request
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from bs4 import BeautifulSoup

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

defaultArtist = 'Drake'
test = []
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

#def print_top_ten():
    #token = get_token()
    #result = search_for_artist(token, defaultArtist)
    #artist_id = result["id"]
    #songs = get_songs_by_artist(token, artist_id)

    #for idx, song in enumerate(songs):
        #print(f"{idx + 1}. {song['name']}")

    #for idx, song in enumerate(songs):
        #test.append(f"{idx + 1}. {song['name']}")
    
#tempArtist = ""
def send_artist(artist):
    tempArtist = artist
    return tempArtist 




views = Blueprint(__name__,"views")

@views.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template()

@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"

@views.route("/artist")
def artist():
    args = request.args
    artistName = args.get('txtArtistName')
    defaultArtist = artistName
    #send_artist(artistName)
    print(artistName)
    print(defaultArtist)

    #html = """<p>{{ your_list_element }} </p>"""

    #soup = BeautifulSoup(html, 'html.parser')
    #old_tag = soup.p
    #new_tag = soup.new_tag("h1")
    #new_tag.string = old_tag.string
    #old_tag.replace_with(new_tag)

    token = get_token()
    result = search_for_artist(token, defaultArtist)
    artist_id = result["id"]
    songs = get_songs_by_artist(token, artist_id)
    for idx, song in enumerate(songs):
        test.append(f"{idx + 1}. {song['name']}")
    for idx, song in enumerate(songs):
        print(f"{idx + 1}. {song['name']}")
    return render_template("index.html", your_list= test, txtArtistName = artistName)