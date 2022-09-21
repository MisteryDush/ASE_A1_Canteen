import base64
from datetime import datetime
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

"""Setting up the app and connection with the database"""

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

"""Database entities"""


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
    stall_id = db.Column(db.Integer, db.ForeignKey('stalls.stall_id'), nullable=True)

    def __init__(self, user_id, password, role):
        self.user_id = user_id
        self.password = password
        self.roles = role

    def get_id(self):
        return self.user_id


class PendingOrder(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    stall_id = db.Column(db.Integer, db.ForeignKey('stalls.stall_id'))
    user_id = db.Column(db.Text, db.ForeignKey('users.user_id'))
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.dish_id'))
    time = db.Column(db.DateTime)

    def __init__(self, stall_id, user_id, dish_id, time):
        self.stall_id = stall_id
        self.user_id = user_id
        self.dish_id = dish_id
        self.time = time


class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.dish_id'))
    user_id = db.Column(db.Text, db.ForeignKey('users.user_id'))

    def __init__(self, dish_id, user_id):
        self.dish_id = dish_id
        self.user_id = user_id


"""App functions"""


@app.route('/')
@login_required
def all_stalls():
    stalls = encode_img(Stall.query.all())
    return render_template('index.html', stalls=stalls)


@app.route('/add-dish/<int:stall_id>', methods=['GET', 'POST'])
@login_required
def add_dish(stall_id):
    """function for admins and stall owners to add dishes"""
    if check_role_admin() or (check_role_owner() and stall_id == current_user.stall_id):
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
    """page to display menu of a particular stall"""
    dishes = encode_img(list(Dish.query.filter_by(stall_id=stall_id)))
    return render_template('menu.html', dishes=dishes)


# TODO: Finish settings page
@app.route('/settings')
@login_required
def settings():
    return 'settings!'


@app.route('/login', methods=["GET", "POST"])
def login():
    """main login page"""
    if request.method == "POST":
        user = User.query.filter_by(user_id=request.form["username"]).first()
        pswd = request.form['password']
        if not user:
            flash("This username does not exist", category='username_error')
            return render_template('login.html')
        elif not check_password_hash(user.password, pswd):
            flash("Wrong password!", category='wrong_pass')
            return render_template('login.html')
        login_user(user, False)
        if current_user.roles == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.roles == 'Stall owner':
            return redirect(url_for('owner_dashboard'))
        return redirect(url_for('all_stalls'))
    return render_template('login.html', form='')


@app.route('/logout')
@login_required
def logout():
    """logout page"""
    logout_user()
    return redirect(url_for('all_stalls'))


@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if check_role_admin():
        return render_template('admin_dashboard.html')


@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
    if check_role_admin():
        if request.method == 'POST':
            file = request.files['file']
            data = file.read()
            name = file.filename
            add_entry(request.form['name'], name, data)
            return redirect(url_for('all'))
        return render_template('add.html')
    return redirect(url_for('all_stalls'))


@app.route('/all')
@login_required
def all():
    if check_role_admin():
        stalls = encode_img(Stall.query.all())
        return render_template('all.html', stalls=stalls)
    return redirect(url_for('all_stalls'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()


@app.route('/add-to-cart/<int:picked_dish_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(picked_dish_id):
    dish = Dish.query.filter_by(dish_id=picked_dish_id).first()
    user_id = current_user.user_id
    cart = Cart(picked_dish_id, user_id)
    db.session.add(cart)
    db.session.commit()
    return render_template('add_to_cart.html', dish=dish)


@app.route('/delete-stall/<int:stall_id>')
@login_required
def delete_stall(stall_id):
    if check_role_admin():
        stall = Stall.query.filter_by(stall_id=stall_id).first()
        db.session.delete(stall)
        db.session.commit()
        return redirect(url_for('all'))


@app.route('/checkout')
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.user_id).all()
    dishes = []
    for dish in cart:
        dishes.append(Dish.query.filter_by(dish_id=dish.dish_id).first())
    dishes = encode_img(dishes)
    return render_template('checkout.html', cart=dishes)


@app.route('/add-owner', methods=['GET', 'POST'])
@login_required
def add_owner():
    if request.method == 'POST':
        if check_role_admin():
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            stall_id = int(request.form['chosen_stall'])
            user = User(username, password, 'Stall owner')
            user.stall_id = stall_id
            add_owner_db(user)
    owners = User.query.filter_by(roles='Stall owner').all()
    stalls = Stall.query.all()
    return render_template('add_owner.html', owners=owners, stalls=stalls)


@app.route('/delete-owner/<owner_id>')
@login_required
def delete_owner(owner_id):
    if check_role_admin():
        owner = User.query.filter_by(user_id=owner_id).first()
        db.session.delete(owner)
        db.session.commit()
        return redirect(url_for('add_owner'))


@app.route('/delete-from-cart/<int:dish_id>', methods=['POST'])
@login_required
def delete_from_cart(dish_id):
    user_id = current_user.user_id
    order = Cart.query.filter_by(user_id=user_id).filter_by(dish_id=dish_id).first()
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('checkout'))


@app.route('/make-order', methods=['GET', 'POST'])
@login_required
def make_order():
    today = datetime.today()
    order_time = datetime(today.year, today.month, today.day, int(request.form['time'][0:2]),
                          int(request.form['time'][3:]))
    if order_time < datetime.now():
        flash('Order time is less than current time')
        return redirect(url_for('checkout'))
    user_id = current_user.user_id
    cart = Cart.query.filter_by(user_id=user_id).all()
    create_order(user_id, cart, order_time)
    return render_template('make-order.html')


@app.route('/owner-dashboard')
@login_required
def owner_dashboard():
    if check_role_owner():
        return render_template('owner_dashboard.html', stall_id=current_user.stall_id)


@app.route('/pending-orders/<int:stall_id>')
@login_required
def pending_orders(stall_id):
    if check_role_owner():
        orders = {}
        ids = PendingOrder.query.filter_by(stall_id=stall_id).all()
        for i, id in enumerate(ids):
            if not (id.user_id in orders.keys()):
                orders[id.user_id] = [[Dish.query.filter_by(dish_id=id.dish_id).first(), ids[i].time]]
            else:
                orders[id.user_id].append([Dish.query.filter_by(dish_id=id.dish_id).first(), ids[i].time])
        return render_template('pending-orders.html', orders=orders)


@app.route('/complete-order/<user_id>/<int:dish_id>', methods=['POST'])
@login_required
def complete_order(user_id, dish_id):
    if request.method == 'POST':
        order = PendingOrder.query.filter_by(user_id=user_id).filter_by(dish_id=dish_id).first()
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('pending_orders', stall_id=current_user.stall_id))


def add_entry(name, filename, data):
    if check_role_admin():
        entry = Stall(name, filename, data)
        db.session.add(entry)
        db.session.commit()
    return redirect(url_for('all_stalls'))


def add_dish_db(name, price, stall, data, filename):
    if check_role_admin():
        entry = Dish(name, filename, data, price, stall)
        db.session.add(entry)
        db.session.commit()
    return redirect(url_for('all_stalls'))


def encode_img(entities):
    for entity in entities:
        entity.img = base64.b64encode(entity.data).decode("utf-8")
    return entities


def add_owner_db(owner):
    db.session.add(owner)
    db.session.commit()


def check_role_admin():
    return True if current_user.roles == 'Admin' else False


def check_role_owner():
    return True if current_user.roles == 'Stall owner' else False


def create_order(user_id, cart, order_time):
    for dish in cart:
        dish_id = dish.dish_id
        stall_id = Dish.query.filter_by(dish_id=dish_id).first().stall_id
        order = PendingOrder(stall_id, user_id, dish_id,
                             datetime(year=order_time.year, month=order_time.month, day=order_time.day,
                                      hour=order_time.hour, minute=order_time.minute))
        db.session.add(order)
        db.session.delete(dish)
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=False)
