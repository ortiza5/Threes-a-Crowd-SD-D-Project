from flask import Flask, render_template, flash, redirect, \
                    url_for, session, request, logging
from flask_mail import Mail, Message
import pymysql, random
import jsonpickle
from passlib.hash import sha256_crypt
from config import *
from helper import *
from functools import wraps
import usertypes

app = Flask(__name__)
app.secret_key=SECRET
mail = Mail(app)

# Index
@app.route('/')
def index():
    return render_template('startpage.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/home')
@is_logged_in
def home():
    forms = []
    # Get forms that need to be displayed  in table
    if jsonpickle.decode(session['userOBJ']).getUserType() == "Staff":
        # Open database connection
        db = pymysql.connect(HOST,USER,PASSWORD,DBNAME)
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        result = cursor.execute('SELECT * FROM formfilled')
        if result > 0:
            data = cursor.fetchall()
            allforms = query_forminfo()
            formnames = {}
            # Get all the form names based off the fid
            for form in allforms:
                formnames[form['fid']] = form['title']
            newform = ''

            # Generate the table information for staff members
            for row in data:
                if (str(row[0])+str(row[1])+str(row[2])) != newform:
                    newform = (str(row[0])+str(row[1])+str(row[2]))
                    newdict = {}
                    newdict['fid'] = row[0]
                    newdict['title'] = formnames[row[0]]
                    newdict['username'] = row[1].split('@')[0]
                    newdict['approval'] = 'Not Approved'
                    forms.append(newdict)

    return render_template('home.html',forms=forms, usertype=str(jsonpickle.decode(session['userOBJ'])))

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
        email = request.form['email']
        password_candidate = request.form['password']
        # Open database connection
        db = pymysql.connect(HOST,USER,PASSWORD,DBNAME )
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        result = cursor.execute('SELECT * FROM user WHERE email = %s', [email])

        if result>0:
            # Fetch a single row using fetchone() method.
            data = cursor.fetchone()
            password = data[1]
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['user'] = email
                db.close()

                #  create the user object for the session
                print('%s',data[3])
                if data[2] == "Student":
                    user = usertypes.Student(data[3], data[4], data[5], data[0], data[6])
                elif data[2] == "Faculty":
                    user = usertypes.Faculty(data[3], data[4], data[5], data[0], data[6])
                elif data[2] == "Staff":
                    user = usertypes.StaffMember(data[3], data[4], data[5], data[0], data[6])
                else:
                    error = 'Not a valid user type. Register again'
                    return render_template('login.html', error=error)
                session['userOBJ'] = jsonpickle.encode(user)
                # successful login
                return redirect(url_for('home'))
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

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password = request.form['password']
        utype = request.form['utype']
        first = request.form['first']
        middle = request.form['middle']
        last = request.form['last']
        rin = request.form['rin']

        print(email)
        # Open database connection
        db = pymysql.connect(HOST,USER,PASSWORD,DBNAME )
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        cursor.execute('SELECT EXISTS(SELECT * FROM user WHERE email=%s)', [email])
        result = cursor.fetchall()
        print(result[0][0])
        if result[0][0]==0:
            try:
                newpass = sha256_crypt.hash(password)
                # Execute the SQL command
                cursor.execute('INSERT INTO user VALUES (%s, %s, %s, %s, %s, %s, %s)', [email, newpass, utype, first, middle, last, rin])
                # Commit your changes in the database
                db.commit()
                print('added user')
                # ALEX: I think we shouldn't log them in when they register
                # session['logged_in'] = True
                # session['user'] = email
            except:
                # Rollback in case there is any error
                db.rollback()
                error = 'Invalid register'
                return render_template('register.html', error=error)
            db.close()
            print('registered')
            msg = 'Registration Success'
            flash('You are now registered and can log in', 'success')
            # return render_template('register.html', msg=msg)
            return redirect(url_for('login'))
        else:
            db.close()
            print('Email address is already registered')
            error = 'Invalid register'
            return render_template('register.html', error=error)
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
            newdict['fqid'] = str(row[0])+'-'+str(row[3])
            newdict['typeparam'] = row[4]
            formQuestions.append(newdict)
    '''get user input'''
    if request.method == 'POST':
        input = request.form
        print('look----',input)
        # Get Form Fields
        for key in input:
            print(key, input[key])
            ids = key.split('-')
            cursor.execute('INSERT INTO formfilled VALUES (%s, %s, %s, %s)', [ids[0], str(session['user']), ids[1], input[key]])
        db.commit()
        htmlbody = '<h1>HTML body</h1>'
        send_email('test send', MAIL_USERNAME,'jingsting@gmail.com', 'hello this is a test', htmlbody)
        return redirect(url_for('home'))
    db.close()
    return render_template('form.html', formQuestions = formQuestions, formId = id, formTitle = title, user=jsonpickle.decode(session['userOBJ']))

@app.route('/search/<string:searchterm>', methods=['GET', 'POST'])
def search(searchterm):
    # Get Forms that match search term
    forms = []
    # Open database connection
    db = pymysql.connect(HOST,USER,PASSWORD,DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    # result = cursor.execute('SELECT * FROM )


    return render_template('search.html', searchterm=searchterm, forms=forms)

@app.route('/delete_filledform/<string:fid>', methods=['POST'])
@is_logged_in
def delete_filledform(fid):
    # Open database connection
    db = pymysql.connect(HOST,USER,PASSWORD,DBNAME)

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Execute the SQL command
    cursor.execute('DELETE  FROM completedforms WHERE fid = %s AND owner = %s',[fid,session['user']])
    cursor.execute('DELETE  FROM formfilled WHERE fid = %s AND username = %s',[fid,session['user']])

    # Commit your changes in the database
    db.commit()

    db.close()

    flash('Form Deleted', 'success')

    return redirect(url_for('home'))



@app.route('/edit_filledform/<int:fid>/<string:title>', methods=['GET', 'POST'])
@is_logged_in
def edit_filledform(fid,title):
    formQuestions = []
    oldFormInputs = {}
    # Open database connection
    db = pymysql.connect(HOST,USER,PASSWORD,DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    result = cursor.execute('SELECT * FROM question WHERE fid = %s', [fid])
    if result > 0:
        data = cursor.fetchall()
        for row in data:
            newdict = {}
            newdict['type'] = row[1]
            newdict['question'] = row[2]
            newdict['fqid'] = str(row[0])+'-'+str(row[3])
            newdict['typeparam'] = row[4]
            formQuestions.append(newdict)

    # Get the old answers from the database
    result = cursor.execute('SELECT * FROM formfilled WHERE fid = %s AND username = %s',[fid,session['user']])
    if result > 0:
        data = cursor.fetchall()
        for row in data:
            oldFormInputs[str(row[0])+'-'+str(row[2])] = row[3]

    '''get user input'''
    if request.method == 'POST':
        input = request.form
        print('look----',input)
        # Get Form Fields
        for key in input:
            print(key, input[key])
            ids = key.split('-')
            cursor.execute('UPDATE formfilled SET answer=%s WHERE fid=%s AND username=%s AND qid=%s',[input[key], ids[0], str(session['user']), ids[1]])
        db.commit()
        return redirect(url_for('home'))
    db.close()
    return render_template('editform.html', formQuestions = formQuestions, answers = oldFormInputs, formId = id, formTitle = title, user=jsonpickle.decode(session['userOBJ']))



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

    
# if __name__ != '__main__':
#     app.config['SESSION_TYPE'] = 'filesystem'
#     sess.init_app(app)
#     app.run(host="0.0.0.0", debug=True)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    # sess.init_app(app)
    app.run(host="0.0.0.0", debug=True)
