from flask import Blueprint, render_template, request
from SpotifyAPI import songs
test = []
testArtist = ""
for idx, song in enumerate(songs):
    test.append(f"{idx + 1}. {song['name']}")


views = Blueprint(__name__,"views")

@views.route("/")
def home():
    return render_template("index.html", your_list= test)

@views.route("/artist")
def artist():
    args = request.args
    artistName = args.get('txtArtistName')
    testArtist = artistName
    return render_template("index.html", your_list= test, txtArtistName = artistName)

def getArtist():
    return testArtist
