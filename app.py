import base64
import os

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Stall(db.Model):
    __tablename__ = 'stalls'
    stall_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30))
    filename = db.Column(db.Text)
    data = db.Column(db.LargeBinary)
    dishes = db.relationship('Dish', backref='stalls')

    def __init__(self, name, filename, data):
        self.name = name
        self.filename = filename
        self.data = data


class Dish(db.Model):
    __tablename__ = 'dishes'
    dish_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50))
    filename = db.Column(db.Text)
    data = db.Column(db.LargeBinary)
    price = db.Column(db.Integer)
    stall_id = db.Column(db.Integer, db.ForeignKey('stalls.stall_id'))

    def __init__(self, name, filename, data, price, stall_id):
        self.name = name
        self.filename = filename
        self.data = data
        self.price = price
        self.stall_id = stall_id


@app.route('/')
def all_stalls():
    stalls = encode_img(Stall.query.all())
    return render_template('index.html', stalls=stalls)


@app.route('/add-dish/<int:stall_id>', methods=['GET', 'POST'])
def add_dish(stall_id):
    if request.method == "POST":
        file = request.files['file']
        data = file.read()
        filename = file.filename
        dish_name = request.form['name']
        price = float(request.form['price'])
        add_dish_db(dish_name, price, stall_id, data, filename)
    dishes = encode_img(list(Dish.query.filter_by(stall_id=stall_id)))

    return render_template('add_dish.html', stall_id=stall_id, dishes=dishes)


@app.route('/menu/<int:stall_id>')
def menu(stall_id):
    dishes = encode_img(list(Dish.query.filter_by(stall_id=stall_id)))
    return render_template('menu.html', dishes=dishes)


@app.route('/settings')
def settings():
    return 'settings!'


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    return "Logout"


@app.route('/sign-up')
def sign_up():
    return "Sign Up"


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        file = request.files['file']
        data = file.read()
        name = file.filename
        add_entry(request.form['name'], name, data)
        return redirect(url_for('all'))
    return render_template('add.html')


@app.route('/all')
def all():
    stalls = encode_img(Stall.query.all())
    return render_template('all.html', stalls=stalls)


def add_entry(name, filename, data):
    entry = Stall(name, filename, data)
    db.session.add(entry)
    db.session.commit()


def add_dish_db(name, price, stall, data, filename):
    entry = Dish(name, filename, data, price, stall)
    db.session.add(entry)
    db.session.commit()


def encode_img(entities):
    for entity in entities:
        entity.img = base64.b64encode(entity.data).decode("utf-8")
    return entities


@app.route('/delete-stall/<int:stall_id>')
def delete_stall(stall_id):
    return f"Deleted {stall_id}!"


if __name__ == '__main__':
    app.run()
