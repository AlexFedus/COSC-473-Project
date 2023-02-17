<<<<<<< Updated upstream
from flask import Flask
=======
from flask import Flask, request, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
>>>>>>> Stashed changes
from views import views
#from SpotifyAPI import songs


app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")



if __name__ == "__main__":
    app.run(debug=True, port=8000)