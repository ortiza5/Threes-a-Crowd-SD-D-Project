from flask import Flask, render_template, flash, redirect, \
                    url_for, session, request, logging
import pymysql, random
from passlib.hash import sha256_crypt
from config import *
from helper import *
from tempdata import FormLinks


app = Flask(__name__)
app.secret_key=SECRET

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
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        # Open database connection
        db = pymysql.connect(HOST,USER,PASSWORD,DBNAME )
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        result = cursor.execute('SELECT * FROM user WHERE rcsid = %s', [username])

        if result>0:
            # Fetch a single row using fetchone() method.
            data = cursor.fetchone()
            password = data[2]
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                db.close()
                print('correct')
                return render_template('correct.html')
            else:
                db.close()
                print('wrong pass')
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            db.close()
            print('wrong name')
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/forms')
def forms():
    # Generate random thumbnails order for forms
    thumbs = []
    choices = ['1', '2', '3', '4', '5','6']
    i = 0
    # Find all the different categories
    categories = set([])

    # Query the 'forminfo' table and store all forminfo
    # in a list of dictionaries
    forms = query_forminfo()

    # forms = FormLinks()



    for form in forms:
        categories.add(form['category'])
        thumbNumber = random.choice(choices)
        # Avoid same image twice in a row
        if ((i == 1) or (i == 2)):
            while (thumbNumber == thumbs[i-1]):
                thumbNumber = random.choice(choices)
        if (i > 2):
            while ((thumbNumber == thumbs[i-1]) or (thumbNumber == thumbs[i-2])or (thumbNumber == thumbs[i-3])):
                thumbNumber = random.choice(choices)
        thumbs.append(thumbNumber)
        i = i + 1
    categories = list(categories)
    categories.sort()

    # Generate Different Accordian View ID groups for categories
    # Currently have a limit set to 10 different form categories
    numberWords = ['One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten']
    accordianIDs = {}
    i = 0
    for category in categories:
        accordianIDs[category] = {'headingID':('heading' + numberWords[i]), \
                            'collapseID':('collapse' + numberWords[i])}
        i = i + 1
    return render_template('forms.html', categories = categories, accordianIDs = accordianIDs, forms = forms, thumbs = thumbs)


@app.route('/form/<int:id>/<string:title>', methods=['GET', 'POST'])
def formfill(id,title):
    formQuestions = []
    # Open database connection
    db = pymysql.connect(HOST,USER,PASSWORD,DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    result = cursor.execute('SELECT * FROM question WHERE fid = %s', [id])
    if result > 0:
        data = cursor.fetchall()
        for row in data:
            newdict = {}
            newdict['type'] = row[1]
            newdict['question'] = row[2]
            newdict['qid'] = 'f'+str(row[0])+'q'+str(row[3])
            newdict['typeparam'] = row[4]
            formQuestions.append(newdict)
    return render_template('form.html', formQuestions = formQuestions, formId = id, formTitle = title)


if __name__ != '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.run(host="0.0.0.0", debug=True)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    # sess.init_app(app)
    app.run(host="0.0.0.0", debug=True)
