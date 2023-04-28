from flask import Flask, render_template, redirect,request,session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = "C:/Users/19171/PycharmProjects/OnlineTeReoDictionary/TeReoDictionary/maindictionary.db"
# DATABASE = "D:/13dts/OnlineTeReoDictionary/TeReoDictionary/maindictionary.db"
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
    return render_template('home.html')

@app.route('/full')
def render_fulldictionary():
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Definition, YearLevel FROM FullDictionary"
    cur = con.cursor()
    cur.execute(query)
    dictionary = cur.fetchall()
    con.close()
    print(dictionary)
    return render_template('full.html', fulldictionary=dictionary)

@app.route('/full/<Category>')
def render_fulldictionary_categories(Category):
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Definition, YearLevel FROM FullDictionary WHERE Category=?"
    cur = con.cursor()
    cur.execute(query, (Category,))
    query = "SELECT id, Category FROM Categories"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    dictionary = cur.fetchall()
    con.close()
    print(dictionary)
    return render_template('full.html', dictionary=dictionary, category_list=category_list)

@app.route('/search', methods=['GET', 'POST'])
def render_search():
    search = request.form['search']
    title = "Search for " + search
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Definition YearLevel FROM FullDictionary WHERE " \
            "Maori like ? OR English like ? OR Category like ? OR Definition like ? OR YearLevel like ?"
    search = "%" + search + "%"
    cur = con.cursor()
    cur.execute(query, (search, search, search, search, search))
    dictionary = cur.fetchall()
    con.close()
    return render_template("search.html", searchdictionary = dictionary, title=title)

if __name__ == '__main__':
    app.run()
