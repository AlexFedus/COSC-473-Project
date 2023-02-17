from flask import Blueprint, render_template, request, url_for, redirect
from SpotifyAPI import getartisttopten

test = []
finalTrackList = []

TOKEN_INFO = "token_info"

views = Blueprint(__name__,"views")

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["em"]
        password = request.form["pw"]
        #print(user)
        return render_template("login.html")
        #return redirect(url_for("user", usr = user))

        users = get_login(user)
        passwords = get_login(password)
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
        
       
            
        tracks = getUserSavedTracks()
        #inc = 0
        for idx, track in enumerate(tracks):
            if idx == 50:
                break
            finalTrackList.append(f"{idx + 1}. {track['track']['name']}")
            
            
           
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

@views.route("/spotifyLogin")    
def spotLogin():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@views.route("/redirect")     
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('views.home', _external=True))

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('views.redirectPage', _external=True),
        scope = "user-library-read"
    ) 

 