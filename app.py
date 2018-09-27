from flask import Flask, render_template

app = Flask(__name__)
# Index
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/why')
def why():
    return render_template('why.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)