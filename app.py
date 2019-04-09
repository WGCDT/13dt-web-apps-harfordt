import sys

sys.path.append("N:\python-modules")

from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error

from datetime import datetime
from flask_bcrypt import Bcrypt

# from flask_session import Session

DB_NAME = "flowerpot.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "banana"


def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        connection = sqlite3.connect(db_file)
        # initialise_tables(connection)
        return connection
    except Error as e:
        print(e)

    return None


def create_table(con, query):
    if con is not None:
        try:
            c = con.cursor()
            c.execute(query)
        except Error as e:
            print(e)


def initialise_tables(con):
    create_product_table = """CREATE TABLE IF NOT EXISTS product(
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT NOT NULL,
                            price DECIMAL(6,2) NOT NULL,
                            image TEXT NOT NULL,
                            category TEXT NOT NULL,
                            stock INTEGER NOT NULL
                        )
                        """
    create_table(con, create_product_table)

    products = [["Keyring", "Put all your keys on it", 4.5, "keychain.jpg", "Personal", 20],
                ["Heart mug", "Mug with a heart on it", 8, "mug.jpg", "Personal", 12],
                ["Eazy-E t-shirt", "What your mum wants", 25, "eazy.jpg", "Personal", 3],
                ["Bow and arrow", "Fun for everyone", 40, "bowhunting.jpg", "personal", 7]]

    for product in products:
        sql = """INSERT INTO product(id, name, description, price, image, category,stock) VALUES (NULL,?,?,?,?,?,?);"""
        cur = con.cursor()
        cur.execute(sql, product)
        con.commit()

    create_user_table = """CREATE TABLE IF NOT EXISTS user(
                                id INTEGER PRIMARY KEY,
                                firstname TEXT NOT NULL,
                                lastname TEXT NOT NULL,
                                dob DATE NOT NULL,
                                wananga TEXT NOT NULL,
                                email TEXT NOT NULL,
                                phone_number TEXT NOT NULL,
                                password TEXT NOT NULL,
                                signedup DATETIME NOT NULL
                                )
                        """
    create_table(con, create_user_table)

    users = [["Jim", "Smith", "1985-04-10", "9HFT", "jim.smith@gmail.com", "0212348576", "banana"],
             ["Ada", "Lovelace", "2001-10-07", "9HFK", "ada.lovelace@gmail.com", "02112345456", "banana"],
             ["Mary", "Queen of Scots", "2000-02-02", "10JNM", "mary.socts@gmail.com", "290200", "banana"]]

    for user in users:
        sql = """INSERT INTO user(id, firstname, lastname, dob, wananga, email, phone_number, password, signedup) 
                    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%d %H-%M-%S','now'));"""
        cur = con.cursor()
        cur.execute(sql, user)
        con.commit()


@app.route('/')
def home_page():
    return render_template("home.html")


@app.route('/products')
def products_page():
    # connect to the database
    con = create_connection(DB_NAME)

    # execute the query
    query = "SELECT id, name, description, image FROM product"  # SELECT the things you want from your table(s)
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    products = cur.fetchall()  # puts the results into a list usable in pythons
    # print(products)  # so I can see if/what data is coming from the database
    con.close()  # close the connection, super important

    # pass the results to the template to create the page
    return render_template("products.html", products=products)


@app.route('/products/<product_id>')
def individual_product_page(product_id):
    print(product_id)
    con = create_connection(DB_NAME)
    query = "SELECT * FROM product WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (product_id,))
    product_data = cur.fetchall()
    # print(product_data)
    con.close()
    return render_template("product.html", product=product_data[0])


@app.route('/create-new-user', methods=['POST'])
def create_new_user():
    fname = request.form['fname'].strip().capitalize()
    lname = request.form['lname'].strip().capitalize()
    dob = request.form['dob']
    wananga = request.form['wananga'].strip().upper()
    email = request.form['email'].strip().lower()
    phone = request.form['phone'].strip()
    password = request.form['password'].strip()
    password2 = request.form['password2'].strip()
    # print(fname, lname, dob, wananga, email, phone, password, password2)

    if password != password2:
        return redirect(request.referrer + "?error=Passwords+don't+match")

    for item in [fname, lname, dob, wananga, email, phone, password, password2]:
        if len(item) < 1:
            return redirect(request.referrer + "?error=Please+enter+valid+data+in+all+fields")

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    # print(hashed_password)
    # print(bcrypt.check_password_hash(hashed_password, password))
    con = create_connection(DB_NAME)
    now = datetime.now()
    user = (fname, lname, dob, wananga, email, phone, hashed_password, now)
    query = """INSERT INTO user(id, firstname, lastname, dob, wananga, email, phone_number, password, signedup)
                VALUES (NULL,?,?,?,?,?,?,?,?);"""
    cur = con.cursor()
    cur.execute(query, user)
    con.commit()
    con.close()

    return redirect('/')


@app.route('/login', methods=["POST"])
def log_in():
    email = request.form['login-email']
    password = request.form['login-password']
    # print(email, password)

    query = """SELECT password FROM user WHERE email = ?"""
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (email,))
    db_password = cur.fetchall()

    # check if email is in the database (if it isn't, db_password[0][0] will raise an error)
    try:
        print(db_password[0][0])
    except IndexError:
        return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

    # check if the password is incorrect for that email address
    if not bcrypt.check_password_hash(db_password[0][0], password):
        return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

    session['email'] = email
    return redirect(request.referrer)


@app.route('/contact')
def contact_page():
    return render_template("contact.html")


@app.route('/register')
def register_page():
    return render_template("register.html")


@app.route('/trellos')
def trellos():
    try:
        print(session['email'])
    except KeyError:
        print("NO")
    return render_template("trellos.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
