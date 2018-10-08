from flask import Flask, render_template

app = Flask(__name__)
# Index
@app.route('/')
def index():
    return render_template('startpage.html')

@app.route('/home')
def why():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# TO-DO:
# Add templates and routing for Forms and Contact pages

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
