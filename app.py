from flask import Flask, render_template, flash, redirect, url_for, session, request, logging

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

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/home')
    return render_template('login.html', error=error)

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
