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


@app.route('/')
def all_stalls():
    stalls = Stall.query.all()
    for stall in stalls:
        stall.img = base64.b64encode(stall.data).decode("utf-8")
    return render_template('index.html', stalls=stalls)


@app.route('/add_dish/<int:stall_id>')
def add_dish(stall_id):
    return f"Hi {stall_id}"


@app.route('/menu/<int:stall_id>')
def menu(stall_id):
    stall = Stall.query.get(stall_id)
    return render_template('menu.html', stall=stall)


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
        add_entry(request.form['name'], name, data, 'stall')
        return redirect(url_for('all'))
    return render_template('add.html')


@app.route('/all')
def all():
    stalls = Stall.query.all()
    for stall in stalls:
        stall.img = base64.b64encode(stall.data).decode("utf-8")
    return render_template('all.html', stalls=stalls)




def add_entry(name, filename, data, entity):
    if entity == 'stall':
        entry = Stall(name, filename, data)
        db.session.add(entry)
        db.session.commit()


if __name__ == '__main__':
    app.run()
