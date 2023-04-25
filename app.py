from flask import Flask
from views import views
from views import db


"""
This File is the file that is ran when you want to start the development server.

In this file, our database is connected and our blueprint file is linked. 

"""




app = Flask(__name__)

app.secret_key = "0afafa34v"
#capp.config['SESSION_TYPE'] = 'filesystem'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql9598812:uJVAVztfRj@sql9.freesqldatabase.com:3306/sql9598812'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://freedb_cosc473:uQzS965UXf8M&s?@sql.freedb.tech/freedb_Cosc473'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql9614332:Te2CMyu1pV@sql9.freemysqlhosting.net/sql9614332'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# All of our routes are kept in a "views.py" for organization
app.register_blueprint(views, url_prefix="/")



if __name__ == "__main__":
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True, port=8000)
