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


if __name__ == '__main__':
    app.run()
