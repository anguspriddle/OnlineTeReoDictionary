from flask import Flask, render_template, redirect,request,session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

# DATABASE = "C:/Users/19171/PycharmProjects/OnlineTeReoDictionary/TeReoDictionary/maindictionary.db"
DATABASE = "D:/13dts/OnlineTeReoDictionary/TeReoDictionary/maindictionary.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "QLGus49&"

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return(connection)
    except Error as e:
        print(e)
    return None
@app.route('/')
def hello_world():  # put application's code here
    return render_template('base.html')


if __name__ == '__main__':
    app.run()
