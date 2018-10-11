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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/forms')
def forms():
	return render_template('forms.html')


# THROW AWAY CODE ========================
@app.route('/form1')
def form1():
	return render_template('form1.html')
# THROW AWAY CODE ========================



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
