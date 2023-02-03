from flask import Blueprint, render_template, request
from SpotifyAPI import getartisttopten

test = []




views = Blueprint(__name__,"views")

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/artist", methods =["GET", "POST"])
def artist():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       artist_name = request.form.get("aname")
       # getting input with name = lname in HTML form
       songs = getartisttopten(artist_name)
        
       
       test.clear()
       
       for idx, song in enumerate(songs):
            test.append(f"{idx + 1}. {song['name']}")
       
       
    return render_template("index.html", your_list = test)