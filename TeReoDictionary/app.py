from flask import Flask, render_template, redirect, request, session
import sqlite3
import datetime
from sqlite3 import Error
from flask_bcrypt import Bcrypt

# DATABASE = "C:/Users/19171/PycharmProjects/OnlineTeReoDictionary/TeReoDictionary/maindictionary.db"
# DATABASE = "D:/13dts/OnlineTeReoDictionary/TeReoDictionary/maindictionary.db"
DATABASE = "maindictionary.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "QLGus49&"


def create_connection(db_file):  # This function will create a connection to the database file
    try:
        connection = sqlite3.connect(db_file)
        return (connection)
    except Error as e:
        print(e)
    return None


def is_logged_in():  # this will simply check if there is someone logged in by checking
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("Logged in")
        return True


def is_teacher():  # this function will check if the person logged in to the session is a teacher or not
    if session.get("permissions") == "teacher":
        print('is teacher')
        return True
    else:
        print("is not teacher")
        return False

def categories():
    con = create_connection(DATABASE)
    query = "SELECT Category FROM Categories"
    cur = con.cursor()
    cur.execute(query)
    Categories = cur.fetchall()
    con.close()
    return Categories

def get_words():
    # This takes the dictionary from the db file and passes it through to the page
    con = create_connection(DATABASE)
    query = "SELECT id, Maori, English, Category, Definition, YearLevel, Author, DateAdded FROM Dictionary"  # Picks certain columns
    # from db file
    cur = con.cursor()
    cur.execute(query)
    allwords = cur.fetchall()
    con.close()
    return allwords

@app.route('/')
def render_home():
    Categories = categories()
    return render_template('home.html', is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories)


@app.route('/words')
def render_dictionary():
    # This takes the dictionary from the db file and passes it through to the page
    con = create_connection(DATABASE)
    query = "SELECT id, Maori, English, Category, Definition, YearLevel, Author, DateAdded FROM Dictionary"  # Picks certain columns
    # from db file
    cur = con.cursor()
    cur.execute(query)
    dictionary = cur.fetchall()
    con.close()
    Categories = categories()
    return render_template('words.html', dictionary=dictionary, is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories)
    # This will return the html page while passing through all the variables


@app.route('/words/<Category>')  # This is a link that passes through what category it's looking for through the link
def render_dictionary_categories(Category):
    con = create_connection(DATABASE)
    query = "SELECT id, Maori, English, Category, Definition, YearLevel, Author, DateAdded FROM Dictionary WHERE Category=?"
    # This query means that it will only take the category that was selected through the link
    cur = con.cursor()
    cur.execute(query, (Category,))
    dictionary = cur.fetchall()
    con.close()
    Categories = categories()
    return render_template('words.html', dictionary=dictionary, is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories)
    # This will pass through the page but now with the variable only having the selected category

@app.route('/<id>')
def render_word(id):
    con = create_connection(DATABASE)
    query = "SELECT id, Maori, English, Category, Definition, YearLevel, Author, wordImage, DateAdded FROM Dictionary WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (id,))
    word = cur.fetchall()
    con.close()
    Categories = categories()
    return render_template('word.html', word=word, is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories)

@app.route('/deletewordconfirmation/<id>')
def deletewordconfirmation(id):
    con = create_connection(DATABASE)
    query = "SELECT id, Maori FROM Dictionary WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (id,))
    word = cur.fetchall()
    con.close()
    return render_template('deletewordconfirmation.html', word=word)
@app.route('/deleteword/<id>')
def deleteword(id):
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "DELETE FROM Dictionary WHERE id = ?"
    cur.execute(query, (id,))
    con.commit()
    con.close()
    Categories = categories()
    return redirect('/')
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
    Categories = categories()
    return render_template("search.html", searchdictionary=dictionary, title=title, is_logged_in=is_logged_in(),
                           is_teacher=is_teacher(), categories=Categories)


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if is_logged_in():
        return redirect('/')
    print("logging in")
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = "SELECT id, fname, lname, password, permissions FROM users WHERE email = ?"
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
            last_name = user_data[2]
            db_password = user_data[3]
            permissions = user_data[4]
        except IndexError:
            return redirect("/login?error=INDEXERROR")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+Password+incorrect")

        session['email'] = email
        session['user_id'] = user_id
        session['firstname'] = first_name
        session['lastname'] = last_name
        session['permissions'] = permissions
        print(session)
        return redirect('/')
    Categories = categories()
    return render_template('login.html', is_teacher=is_teacher(), is_logged_in=is_logged_in(), categories=Categories)


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

    Categories = categories()
    return render_template('signup.html', is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories)


@app.route('/admin', methods=['POST', 'GET'])
def render_admin():  # put application's code here
    if not is_teacher():
        return redirect('/')
    Categories = categories()
    return render_template('admin.html', is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories)

@app.route('/admin/word', methods=['POST', 'GET'])
def render_wordadmin():
    Categories = categories()
    if not is_teacher():
        return redirect('/')
    listwords = get_words()
    if request.method == 'POST':
        Maori = request.form.get('Maori').title().strip()
        English = request.form.get('English').title().strip()
        Category = request.form.get('Category').title().strip()
        Definition = request.form.get('Definition').strip()
        YearLevel = request.form.get('YearLevel')
        Author = session.get("firstname") + ' ' + session.get("lastname")
        DateAdded = datetime.date.today()
        con = create_connection(DATABASE)
        cur = con.cursor()

        # Check if the record already exists
        query = "SELECT COUNT(*) FROM Dictionary WHERE Maori = ?"
        cur.execute(query, (Maori,))
        result = cur.fetchone()

        if result[0] > 0:
            # Record already exists, show an error, do not execute
            Error = "Word Already Exists"
            return render_template('adminwords.html', Error=Error, is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories)

        # Record doesn't exist, proceed with insertion
        query = "INSERT INTO Dictionary (Maori, English, Category, Definition, YearLevel, Author, DateAdded) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cur.execute(query, (Maori, English, Category, Definition, YearLevel, Author, DateAdded))
        con.commit()
        con.close()

        return redirect('/admin/word')
    return render_template('adminwords.html', is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=Categories, listwords=listwords)

@app.route('/deleteadminwordconfirmation/<id>')
def deleteadminwordconfirmation(id):
    con = create_connection(DATABASE)
    query = "SELECT id, Maori FROM Dictionary WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (id,))
    word = cur.fetchall()
    con.close()
    return render_template('deletewordconfirmation.html', word=word)
@app.route('/deleteadminword/<id>')
def deleteadminword(id):
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "DELETE FROM Dictionary WHERE id = ?"
    cur.execute(query, (id,))
    con.commit()
    con.close()
    Categories = categories()
    return redirect('/')

@app.route('/admin/category', methods=['POST', 'GET'])
def render_categories():
    if not is_teacher():
        return redirect('/')
    Categories = categories()
    return render_template('categories.html', Categories=Categories, is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=categories())

@app.route('/addcategory', methods=['POST', 'GET'])
def render_add_category():
    if request.method == 'POST':
        Category = request.form.get('Category').title().strip()
        con = create_connection(DATABASE)
        query = "INSERT INTO Categories (Category) VALUES (?)"
        print(query)
        cur = con.cursor()
        cur.execute(query, (Category, ))
        con.commit()
        con.close()
        return redirect('/admin/category')
@app.route('/deletecategory', methods=['POST', 'GET'])
def render_delete_category():
    if request.method == 'POST':
        cat = request.form.get('Category')
        con = create_connection(DATABASE)
        query = f"SELECT id, Category FROM Categories WHERE Category = '{cat}'"
        cur = con.cursor()
        cur.execute(query)
        category = cur.fetchone()
        con.close()
        print(category)
        return render_template('categorydeleteconfirm.html', cat=category, Categories=categories(), is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=categories())
    return render_template('categories.html', Categories=categories(), is_logged_in=is_logged_in(), is_teacher=is_teacher(), categories=categories())

@app.route('/deletecategory/<int:cat_id>', methods=['POST'])
def render_delete_categoryConfirmed(cat_id):
    print(cat_id)
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "DELETE FROM Categories WHERE id = ?"
    cur.execute(query, (cat_id,))
    con.commit()
    con.close()
    Categories = categories()
    return redirect('/')

@app.route('/logout')
def render_logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=see+you+next+time!')



if __name__ == '__main__':
    app.run()
