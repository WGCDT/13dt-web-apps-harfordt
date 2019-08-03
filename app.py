import sys

sys.path.append("N:\python-modules")

import os
from os import path
from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error

from datetime import datetime
from flask_bcrypt import Bcrypt

from bs4 import BeautifulSoup
import requests

# from flask_session import Session

DB_NAME = "flowerpot.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "banana"

UPLOAD_FOLDER = '/static/images/profiles'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
ROOT = path.dirname(path.realpath(__file__))

def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        # connection = sqlite3.connect(db_file)
        connection = sqlite3.connect(path.join(ROOT, db_file))
        # initialise_tables(connection)
        print(connection)
        return connection
    except Error as e:
        print(e)

    return None


@app.route('/')
def home_page():
    return render_template("home.html", logged_in=is_logged_in(), session=session)


@app.route('/products')
def products_page():
    # connect to the database
    con = create_connection(DB_NAME)

    query = "SELECT id, name, image FROM product"  # SELECT the things you want from your table(s)
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    products = cur.fetchall()  # puts the results into a list usable in python
    print("Product data", products)
    con.close()  # close the connection, super important

    # pass the results to the template to create the page
    # return render_template("products.html")
    return render_template("products.html", products=products, logged_in=is_logged_in())


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
    return render_template("product.html", product=product_data[0], logged_in=is_logged_in(), session=session)


@app.route('/addtocart/<productid>')
def add_to_cart(productid):
    # check if the order list exists in the session
    try:
        session['order']
    except KeyError:
        session['order'] = []

    # can't directly append to list in session, so need to fetch it, append, then overwrite in session
    order_list = session['order']
    order_list.append(productid)
    session['order'] = order_list
    print(session['order'])
    # con = create_connection(DB_NAME)
    # query = "INSERT INTO purchase(id, userid, productid, ordertime) VALUES (NULL,?,?,?)"
    # print(query)
    # now = datetime.now()
    # cur = con.cursor()
    # cur.execute(query, (session['userid'], productid, now))
    # con.commit()
    # con.close()
    return redirect(request.referrer + "?message=Added")


@app.route('/cart')
def cart_page():
    con = create_connection(DB_NAME)

    # 1) Make an empty order list.
    # 2) Check if there is an order list in the session (get it, or write the empty list to the session
    order = []
    try:
        order = session['order']
    except KeyError:
        session['order'] = order

    query = """SELECT id, name, price FROM product WHERE id =(?)"""
    order_items = []
    print("ORDER ITEMS")
    for item in order:
        cur = con.cursor()
        cur.execute(query, (item,))
        order_data = cur.fetchall()
        order_items.append(order_data[0])
    con.close()
    print(order_items)
    return render_template("cart.html", logged_in=is_logged_in(), session=session, order_items=order_items)


@app.route('/profile')
def profile_page():
    if is_logged_in():
        print('static/images/profiles/' + str(session['userid']) + '.jpg')
        exists = os.path.isfile('static/images/profiles/' + str(session['userid']) + '.jpg')
        print(exists)
        return render_template("profile.html", logged_in=is_logged_in(), session=session, profile=exists)
    else:
        return redirect('/')


@app.route('/create-new-user', methods=['POST'])
def create_new_user():
    fname = request.form['fname'].strip().capitalize()
    lname = request.form['lname'].strip().capitalize()
    dob = request.form['dob']
    wananga = request.form['wananga'].strip().upper()
    email = request.form['email'].strip().lower()
    password = request.form['password'].strip()
    password2 = request.form['password2'].strip()
    # print(fname, lname, dob, wananga, email, phone, password, password2)

    if password != password2:
        print()
        return redirect(request.referrer + "?error=Passwords+don't+match")

    for item in [fname, lname, dob, wananga, email, password]:
        if len(item) < 1:
            return redirect(request.referrer + "?error=Please+enter+valid+data+in+all+fields")

    hashed_password = bcrypt.generate_password_hash(password)
    # print("Hashed:",hashed_password)

    con = create_connection(DB_NAME)
    now = datetime.now()
    user = (fname, lname, dob, wananga, email, hashed_password, now)
    query = """INSERT INTO user(id, firstname, lastname, dob, wananga, email, password, signedup)
                VALUES (NULL,?,?,?,?,?,?,?);"""
    cur = con.cursor()
    cur.execute(query, user)
    con.commit()
    con.close()

    return redirect('/')


@app.route('/login', methods=["POST"])
def log_in():
    email = request.form['login-email'].strip().lower()
    password = request.form['login-password'].strip()
    # print(email, password)

    query = """SELECT id, firstname, password FROM user WHERE email = ?"""
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (email,))
    user_data = cur.fetchall()
    print(user_data)
    # if given the email is not in the database this will raise an error
    # would be better to find out how to see if the query return an empty resultset
    try:
        userid = user_data[0][0]
        firstname = user_data[0][1]
        db_password = user_data[0][2]
    except IndexError:
        return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

    # check if the password is incorrect for that email address
    if not bcrypt.check_password_hash(db_password, password):
        print("email or pw prob")
        return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

    session['email'] = email
    session['userid'] = userid
    session['firstname'] = firstname
    print(session)
    return redirect(request.referrer)


@app.route('/profilepic', methods=['get', 'post'])
def upload_profile():
    file = request.files['profilepic']
    # print(file.filename)
    # extension = os.path.splitext(file.filename)[-1].lower()
    file.filename = str(session['userid']) + '.jpg'
    file.save('static/images/profiles/' + file.filename)
    return redirect("/profile")


@app.route('/contact')
def contact_page():
    return render_template("contact.html", logged_in=is_logged_in(), session=session)


@app.route('/register')
def register_page():
    if is_logged_in():
        return redirect("/" + "?error=Whoops+you+tried+to+go+somewhere+you+shouldnt")
    return render_template("register.html")


def is_logged_in():
    try:
        print(session['email'])
        return True
    except KeyError:
        print("NO")
        return False


@app.route('/robson')
def robson():
    return render_template('robson.html')

@app.route('/trellos')
def trellos():
    ################################################################
    # this route is just for testing, it isn't a page in the app ###
    ################################################################
    try:
        print("##### SESSION DATA #####")
        for key in session.keys():
            print(session[key])
    except KeyError:
        print("NO")
    print("### END SESSION DATA ###")
    return render_template("trellos.html")


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/' + '?message=See+you+next+time!')


@app.route('/getphp')
def get_php():
    # use BeautifulSoup to fetch the data from the php script
    temp_url = "http://dtweb/websites2018/salpadorume/plant_health_monitor/"
    r = requests.get(temp_url)
    tempdata = BeautifulSoup(r.text, features="html.parser")
    print(tempdata)

    # the text is in a BeautifulSoup object which I can't do much with.
    # This extracts the text from the page, splitting the values by the
    # '|' separators and adding them to a list
    tempdata = tempdata.get_text().split("|")[:-1]

    # Loops through the data, extracts the datetime and reading values
    # and builds a new list from them
    newtempdata = []
    for reading in tempdata:
        value = reading.split(",")
        print(value)
        newtempdata.append([value[2], float(value[1])])
    print(newtempdata)
    return render_template('charts.html', tempdata=newtempdata)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    # pass