from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template("home.html")

@app.route('/products')
def products_page():
    return render_template("products.html")

@app.route('/contact')
def contact_page():
    return render_template("contact.html")

@app.route('/register')
def register_page():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
