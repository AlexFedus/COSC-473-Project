from flask import Blueprint, render_template
from SpotifyAPI import songs
test = []

for idx, song in enumerate(songs):
    test.append(f"{idx + 1}. {song['name']}")


views = Blueprint(__name__,"views")

@views.route("/")

def home():
    return render_template("index.html", name = test)