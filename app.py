import sys

sys.path.append("N:\python-modules")

from flask import Flask, render_template
import sqlite3
from sqlite3 import Error

DB_NAME = "flowerpot.db"
app = Flask(__name__)


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
    # drop_blog_table = """DROP TABLE entry"""
    # create_table(con, drop_blog_table)
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


@app.route('/')
def home_page():
    return render_template("home.html")


@app.route('/products')
def products_page():
    con = create_connection(DB_NAME)
    query = "SELECT * FROM product"
    cur = con.cursor()
    cur.execute(query)
    products = cur.fetchall()
    print(products)
    con.close()
    return render_template("products.html", products=products)


@app.route('/products/<product_id>')
def individual_product_page(product_id):
    print(product_id)
    con = create_connection(DB_NAME)
    query = "SELECT * FROM product WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (product_id,))
    product_data = cur.fetchall()
    print(product_data)
    con.close()
    return render_template("product.html", product=product_data[0])


@app.route('/contact')
def contact_page():
    return render_template("contact.html")


@app.route('/register')
def register_page():
    return render_template("register.html")


@app.route('/trellos')
def trellos():
    return render_template("trellos.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
