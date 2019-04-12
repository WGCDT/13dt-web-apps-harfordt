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
        initialise_tables(connection)
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

    # products = [["Keyring", "Put all your keys on it", 4.5, "keychain.jpg", "Personal", 20],
    #             ["Heart mug", "Mug with a heart on it", 8, "mug.jpg", "Personal", 12],
    #             ["Eazy-E t-shirt", "What your mum wants", 25, "eazy.jpg", "Personal", 3],
    #             ["Bow and arrow", "Fun for everyone", 40, "bowhunting.jpg", "personal", 7]]
    #
    # for product in products:
    #     sql = """INSERT INTO product(id, name, description, price, image, category,stock) VALUES (NULL,?,?,?,?,?,?);"""
    #     cur = con.cursor()
    #     cur.execute(sql, product)
    #     con.commit()

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

    # users = [["Jim", "Smith", "1985-04-10", "9HFT", "jim.smith@gmail.com", "0212348576", "banana"],
    #          ["Ada", "Lovelace", "2001-10-07", "9HFK", "ada.lovelace@gmail.com", "02112345456", "banana"],
    #          ["Mary", "Queen of Scots", "2000-02-02", "10JNM", "mary.socts@gmail.com", "290200", "banana"]]
    #
    # for user in users:
    #     sql = """INSERT INTO user(id, firstname, lastname, dob, wananga, email, phone_number, password, signedup)
    #                 VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%d %H-%M-%S','now'));"""
    #     cur = con.cursor()
    #     cur.execute(sql, user)
    #     con.commit()

    create_fp_order_table = """CREATE TABLE IF NOT EXISTS fp_order(
                                    id INTEGER PRIMARY KEY,
                                    userid INTEGER NOT NULL ,
                                    ordertime DATETIME NOT NULL
                                )"""
    create_table(con, create_fp_order_table)



    create_order_item_table = """CREATE TABLE IF NOT EXISTS order_item(
                                    id INTEGER PRIMARY KEY,
                                    orderid INTEGER NOT NULL ,
                                    productid INTEGER NOT NULL
                                )"""
    create_table(con, create_order_item_table)


@app.route('/')
def home_page():
    return render_template("home.html", logged_in=is_logged_in(), session=session)


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
    return render_template("products.html", products=products, logged_in=is_logged_in(), session=session)


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


@app.route('/profile')
def profile_page():
    if is_logged_in():
        return render_template("profile.html", logged_in=is_logged_in(), session=session)
    else:
        return redirect('/')


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

    query = """SELECT id, firstname, password FROM user WHERE email = ?"""
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (email,))
    user_data = cur.fetchall()

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
        return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

    session['email'] = email
    session['userid'] = userid
    session['firstname'] = firstname
    return redirect(request.referrer)


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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
