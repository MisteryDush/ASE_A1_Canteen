from flask import Flask, render_template

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run()
