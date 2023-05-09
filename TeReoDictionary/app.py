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

def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("Logged in")
        return True

def is_teacher():
    if session.get("permissions") == "teacher":
        print('is teacher')
        return True
    else:
        print("is not teacher")
        return False
@app.route('/')
def hello_world():  # put application's code here
    return render_template('home.html')

@app.route('/words')
def render_dictionary():
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Definition, YearLevel FROM Dictionary"
    cur = con.cursor()
    cur.execute(query)
    dictionary = cur.fetchall()
    con.close()
    print(dictionary)
    return render_template('words.html', dictionary=dictionary)

@app.route('/words/<Category>')
def render_dictionary_categories(Category):
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Definition, YearLevel FROM Dictionary WHERE Category=?"
    cur = con.cursor()
    cur.execute(query, (Category,))
    dictionary = cur.fetchall()
    con.close()
    print(dictionary)
    return render_template('words.html', dictionary=dictionary)

@app.route('/search', methods=['GET', 'POST'])
def render_search():
    search = request.form['search']
    title = "Search for " + search
    con = create_connection(DATABASE)
    query = "SELECT Maori, English, Category, Definition YearLevel FROM Dictionary WHERE " \
            "Maori like ? OR English like ? OR Category like ? OR Definition like ? OR YearLevel like ?"
    search = "%" + search + "%"
    cur = con.cursor()
    cur.execute(query, (search, search, search, search, search))
    dictionary = cur.fetchall()
    con.close()
    return render_template("search.html", searchdictionary = dictionary, title=title)

@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if is_logged_in():
        return redirect('/menu/1')
    print("logging in")
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = "SELECT id, fname, password FROM users WHERE email = ?"
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchone()
        con.close()
        # if given the email is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty result set
        try:
            user_id = user_data[0]
            first_name = user_data[1]
            db_password = user_data[2]
            permissions = user_data[4]
        except IndexError:
            return redirect("/login?error=Invalid+email+or+password")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+Password+incorrect")

        session['email'] = email
        session['user_id'] = user_id
        session['firstname'] = first_name
        session['permissions'] = permissions
        print(session)
        return redirect('/')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if is_logged_in():
        return redirect('/menu/1')
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        permissions = request.form.get('teachercode')

        if permissions == '1111':
            permissions = 'teacher'
        elif permissions == '':
            permissions = 'student'
        else:
            return redirect("\signup?error=Teacher+code+incorrect")

        if password != password2:
            return redirect("\signup?error=Password+do+not+match")

        if len(password) < 8:
            return redirect("\signup?error=Password+must+be+at+least+8+characters")

        hashed_password = bcrypt.generate_password_hash(password)
        con = create_connection(DATABASE)
        query = "INSERT INTO users (fname, lname, email, password, permissions) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()

        try:
            cur.execute(query, (fname, lname, email, hashed_password, permissions))
        except sqlite3.IntegrityError:
            con.close()
            return redirect('\signup?error=Email+is+already+used')

        con.commit()
        con.close()

        return redirect("/login")

    return render_template('signup.html')

@app.route('/admin')
def render_admin():  # put application's code here
    return render_template('admin.html')

if __name__ == '__main__':
    app.run()
