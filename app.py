import base64
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'cant33n'
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

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


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text)
    roles = db.Column(db.String(length=25))

    def __init__(self, user_id, password, role):
        self.user_id = user_id
        self.password = password
        self.roles = role

    def get_id(self):
        return self.user_id


@app.route('/')
@login_required
def all_stalls():
    stalls = encode_img(Stall.query.all())
    return render_template('index.html', stalls=stalls)


@app.route('/add-dish/<int:stall_id>', methods=['GET', 'POST'])
@login_required
def add_dish(stall_id):
    if check_role():
        if request.method == "POST":
            file = request.files['file']
            data = file.read()
            filename = file.filename
            dish_name = request.form['name']
            price = float(request.form['price'])
            add_dish_db(dish_name, price, stall_id, data, filename)
        dishes = encode_img(list(Dish.query.filter_by(stall_id=stall_id)))
        return render_template('add_dish.html', stall_id=stall_id, dishes=dishes)
    return redirect(url_for('all_stalls'))


@app.route('/menu/<int:stall_id>')
@login_required
def menu(stall_id):
    dishes = encode_img(list(Dish.query.filter_by(stall_id=stall_id)))
    return render_template('menu.html', dishes=dishes)


@app.route('/settings')
@login_required
def settings():
    return 'settings!'


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(user_id=request.form["username"]).first()
        pswd = request.form['password']
        if not user:
            print("USer")
            flash("Error!")
            return render_template('login.html')
        elif not check_password_hash(user.password, pswd):
            print("Password")
            flash("Error!")
            return render_template('login.html')
        login_user(user, False)
        return redirect(url_for('all_stalls'))
    return render_template('login.html', form='')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('all_stalls'))


@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
    if check_role():
        if request.method == 'POST':
            file = request.files['file']
            data = file.read()
            name = file.filename
            add_entry(request.form['name'], name, data)
            return redirect(url_for('all'))
        return render_template('add.html')
    return redirect(url_for('all_stalls'))


def check_role():
    return True if current_user.roles == 'admin' else False


@app.route('/all')
@login_required
def all():
    if check_role():
        stalls = encode_img(Stall.query.all())
        return render_template('all.html', stalls=stalls)
    return redirect(url_for('all_stalls'))


def add_entry(name, filename, data):
    if check_role():
        entry = Stall(name, filename, data)
        db.session.add(entry)
        db.session.commit()
    return redirect(url_for('all_stalls'))


def add_dish_db(name, price, stall, data, filename):
    if check_role():
        entry = Dish(name, filename, data, price, stall)
        db.session.add(entry)
        db.session.commit()
    return redirect(url_for('all_stalls'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()


def encode_img(entities):
    for entity in entities:
        entity.img = base64.b64encode(entity.data).decode("utf-8")
    return entities


@app.route('/delete-stall/<int:stall_id>')
@login_required
def delete_stall(stall_id):
    if check_role():
        return f"Deleted {stall_id}!"
    return redirect(url_for('all_stalls'))


if __name__ == '__main__':
    app.run()
