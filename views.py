from flask import Blueprint, render_template, request
from SpotifyAPI import songs
test = []

for idx, song in enumerate(songs):
    test.append(f"{idx + 1}. {song['name']}")


views = Blueprint(__name__,"views")

@views.route("/home")
def home():
    return render_template("home.html")

@views.route("/artist")
def artist():
    
    return render_template("index.html", your_list= test)