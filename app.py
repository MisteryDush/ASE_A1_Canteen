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

    def __init__(self, name, filename, data):
        self.name = name
        self.filename = filename
        self.data = data


@app.route('/')
def all_stalls():  # put application's code here
    stalls = Stall.query.all()
    for stall in stalls:
        stall.img = base64.b64encode(stall.data).decode("utf-8")
    img = stalls[1].img
    print(len(img))
    return render_template('index.html', stalls=stalls)


@app.route('/menu')
def hello_home():  # put application's code here
    return render_template('menu.html')


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
    stalls = Stall.query.all()
    for stall in stalls:
        stall.img = base64.b64encode(stall.data).decode("utf-8")
    print(stalls[0].data)
    return render_template('all.html', stalls=stalls)


def add_entry(name, filename, data):
    entry = Stall(name, filename, data)
    db.session.add(entry)
    db.session.commit()


if __name__ == '__main__':
    app.run()
