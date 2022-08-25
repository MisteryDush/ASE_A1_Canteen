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

    def __init__(self, name):
        self.name = name


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/Home')
def hello_home():  # put application's code here
    return render_template('index.html')


@app.route('/settings')
def settings():
    return 'settings!'


@app.route('/login')
def login():
    return "Login"


@app.route('/logout')
def logout():
    return "Logout"


@app.route('/sign-up')
def sign_up():
    return "Sign Up"


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        add_entry(request.form['name'])
        return redirect(url_for('all'))
    return render_template('add.html')


@app.route('/all')
def all():
    return render_template('all.html', stalls=Stall.query.all())


def add_entry(name):
    entry = Stall(name)
    db.session.add(entry)
    db.session.commit()


if __name__ == '__main__':
    app.run()
