from flask import Flask, render_template, flash, redirect, \
                    url_for, session, request, logging
from flask_mail import Mail, Message
import pymysql
import random
import jsonpickle
from passlib.hash import sha256_crypt
from config import *
from helper import *
from functools import wraps
import usertypes
from threading import Thread
import re
import datetime


app = Flask(__name__)
app.secret_key = SECRET

app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
mail = Mail(app)


# Startpage
@app.route('/')
def startpage():
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


# Home
@app.route('/home', methods=['GET', 'POST'])
@is_logged_in
def home():
    # For adding new forms with the form builder
    if request.method == 'POST':
        # Get a new "safe" value for fid, concurrent creation of new forms will
        # mess it up, SELECT IDENT_CURRENT(%s) does not seem to work in pymysql
        # Open database connection
        db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        result = cursor.execute('SELECT MAX(fid) FROM forminfo')
        if (result > 0):
            new_fid = cursor.fetchone()[0] + 1
        else:
            new_fid = 1
        input = request.form.to_dict()
        old_index = 1
        to_db_formData = {}
        to_db_formQues = []
        new_dict = {}
        for key in input.keys():
            if (key in ['formTitle', 'formCategory', 'formDescription',
                        'formLink']):
                to_db_formData[key] = input[key]
                continue
            sub_fields = key.split('.')
            if (int(sub_fields[2]) == old_index):
                new_dict['fid'] = new_fid
                new_dict['qid'] = sub_fields[2]
                if (sub_fields[1] == '0'):
                    new_dict['type'] = input[key]
                elif (sub_fields[1] == '1'):
                    new_dict['question'] = input[key]
                elif (sub_fields[1] == '2'):
                    new_dict['typeparam'] = input[key]
                elif (sub_fields[1] == '3'):
                    new_dict['required'] = input[key]
            else:
                to_db_formQues.append(new_dict)
                new_dict = {}
                if (sub_fields[1] == '0'):
                    new_dict['type'] = input[key]
                old_index = int(sub_fields[2])
        to_db_formQues.append(new_dict)
        cursor.execute('INSERT INTO forminfo VALUES (%s, %s, %s, %s, %s)',
                       [new_fid, to_db_formData['formCategory'],
                        to_db_formData['formTitle'],
                        to_db_formData['formDescription'],
                        to_db_formData['formLink']])

        for element in to_db_formQues:
            if 'required' not in element:
                element['required'] = 0
            cursor.execute('INSERT INTO question VALUES (%s, %s, %s, %s, %s, \
                           %s)', [element['fid'], element['type'],
                                  element['question'], element['qid'],
                                  element['typeparam'], element['required']])

        db.commit()
        db.close()

    # For creating the home page layout
    forms = []
    user = jsonpickle.decode(session['userOBJ'])
    # Get forms that need to be displayed  in table
    # Open database connection
    db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    if user.getUserType() == "Staff":
        result = cursor.execute('SELECT * FROM completedforms')
    elif user.getUserType() == "Student":
        result = cursor.execute('SELECT * FROM completedforms WHERE \
                                owner=%s', [session['user']])
    elif user.getUserType() == "Faculty":
        result = cursor.execute('SELECT * FROM completedforms WHERE \
                                viewer=%s', [session['user']])
    if result > 0:
        data = cursor.fetchall()
        allforms = query_forminfo()
        formnames = {}
        # Get all the form names based off the fid
        for form in allforms:
            formnames[form['fid']] = form['title']

        # Generate the table information for staff members
        for row in data:
            newdict = {}
            newdict['fid'] = row[0]
            newdict['title'] = formnames[row[0]]
            newdict['username'] = row[1]
            newdict['datetime'] = row[4]
            newdict['approval'] = row[2]
            forms.append(newdict)

    # Renders the webpage according to the information we got above.
    return render_template('home.html', forms=forms, user=user)


# about page
@app.route('/about')
def about():
    return render_template('about.html')


# contact page
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
        db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        result = cursor.execute('SELECT * FROM user WHERE email = %s',
                                [email])

        if result > 0:
            # Fetch a single row using fetchone() method.
            data = cursor.fetchone()
            password = data[1]
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['user'] = email
                db.close()

                #  create the user object for the session
                print('%s', data[3])
                if data[2] == "Student":
                    user = usertypes.Student(data[3], data[4], data[5],
                                             data[0], data[6])
                elif data[2] == "Faculty":
                    user = usertypes.Faculty(data[3], data[4], data[5],
                                             data[0], data[6])
                elif data[2] == "Staff":
                    user = usertypes.StaffMember(data[3], data[4],
                                                 data[5], data[0],
                                                 data[6])
                else:
                    error = 'Not a valid user type. Register again'
                    return render_template('login.html', error=error)
                # store the user object in session
                session['userOBJ'] = jsonpickle.encode(user)
                # successful login
                return redirect(url_for('home'))
            else:
                db.close()
                print('wrong pass')
                error = 'The username and password do not match. \
                         Please try again.'
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
    # clear session cookie
    session.clear()
    return redirect(url_for('login'))


# Register
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
        db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # execute SQL query using execute() method.
        cursor.execute('SELECT EXISTS(SELECT * FROM user WHERE \
                       email=%s)', [email])
        result = cursor.fetchall()
        print(result[0][0])
        if result[0][0] == 0:
            try:
                newpass = sha256_crypt.hash(password)
                # Execute the SQL command
                # Removed user type selection: (now defaults to student)
                # cursor.execute('INSERT INTO user VALUES (%s, %s, %s, \
                #                %s, %s, %s, %s)', [email, newpass, \
                #                                   utype, first, \
                #                                   middle, last, rin])
                cursor.execute('INSERT INTO user VALUES (%s, %s, %s, %s, \
                               %s, %s, %s)', [email, newpass, 'Student',
                                              first, middle, last, rin])
                # Commit your changes in the database
                db.commit()
                print('added user')
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
    choices = ['1', '2', '3', '4', '5', '6']
    i = 0
    # Find all the different categories
    categories = set([])

    # Query the 'forminfo' table and store all forminfo
    # in a list of dictionaries
    forms = query_forminfo()

    for form in forms:
        categories.add(form['category'])
        thumbNumber = random.choice(choices)
        # Avoid same image twice in a row
        if ((i == 1) or (i == 2)):
            while (thumbNumber == thumbs[i-1]):
                thumbNumber = random.choice(choices)
        if (i > 2):
            while ((thumbNumber == thumbs[i-1]) or
                   (thumbNumber == thumbs[i-2]) or
                   (thumbNumber == thumbs[i-3])):
                thumbNumber = random.choice(choices)
        thumbs.append(thumbNumber)
        i = i + 1
    categories = list(categories)
    categories.sort()

    # Generate Different Accordian View ID groups for categories
    # Currently have a limit set to 10 different form categories
    numberWords = ['One', 'Two', 'Three', 'Four', 'Five', 'Six',
                   'Seven', 'Eight', 'Nine', 'Ten']
    accordianIDs = {}
    i = 0
    for category in categories:
        accordianIDs[category] = {'headingID': ('heading' + numberWords[i]),
                                  'collapseID': ('collapse' + numberWords[i])}
        i = i + 1
    return render_template('forms.html', categories=categories,
                           accordianIDs=accordianIDs, forms=forms,
                           thumbs=thumbs)


@app.route('/form/<int:id>/<string:title>', methods=['GET', 'POST'])
def formfill(id, title):
    formQuestions = []
    # Open database connection
    db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    recipient_mail = formname = recipient_fqid = last_fqid \
                   = first_fqid = last_name = first_name = ''
    result = cursor.execute('SELECT title FROM forminfo WHERE \
                            fid = %s', [id])
    if result > 0:
        formname = cursor.fetchall()[0][0]
    result = cursor.execute('SELECT * FROM question WHERE \
                            fid = %s ORDER BY qid ASC', [id])
    if result > 0:
        data = cursor.fetchall()
        for row in data:
            newdict = {}
            newdict['type'] = row[1]
            newdict['question'] = row[2]
            newdict['fqid'] = str(row[0])+'-'+str(row[3])
            newdict['typeparam'] = row[4]
            if row[5] == 1:
                newdict['req'] = "required"
            else:
                newdict['req'] = ""
            formQuestions.append(newdict)
            if newdict['question'] == 'Recipient Email':
                recipient_fqid = newdict['fqid']
    # get user input
    if request.method == 'POST':
        # get date time
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        input = request.form
        # Get Form Fields
        for key in input:
            print(key, input[key])
            ids = key.split('-')
            cursor.execute('INSERT INTO formfilled VALUES \
                           (%s, %s, %s, %s, %s)',
                           [ids[0], str(session['user']),
                            ids[1], input[key], time])
            if key == recipient_fqid:
                recipient_mail = input[key]
        cursor.execute('INSERT INTO completedforms VALUES \
                       (%s, %s, %s, %s, %s)',
                       [id, str(session['user']), 'Filled',
                        recipient_mail, time])
        db.commit()
        usr = jsonpickle.decode(session['userOBJ'])
        msgstr = 'Hi!\n\n' + usr.getFirst() + ' ' + usr.getLast() \
            + ' just submitted ' + formname + ' to you.\n\n' \
            + 'Check it out on fastforms.ml\n\nThree\'s a Crowd Team'
        if len(recipient_mail) >= 3:
            send_email('Form Submitted', MAIL_USERNAME,
                       [recipient_mail], msgstr)
        return redirect(url_for('home'))
    db.close()
    return render_template('form.html', formQuestions=formQuestions,
                           formId=id, formTitle=title,
                           user=jsonpickle.decode(session['userOBJ']))


@app.route('/search', methods=['GET', 'POST'])
def search():
    searchterm = request.form['term']
    print('here!!!!!!!!!!!')
    # Get Forms that match search term
    formsfound = []
    # Open database connection
    db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    result = cursor.execute('SELECT title, category, fid FROM forminfo')
    allforms = cursor.fetchall()
    print(allforms)
    for form in allforms:
        if re.search(searchterm.lower(), form[0].lower()):
            newdict = {}
            newdict['title'] = form[0]
            newdict['category'] = form[1]
            formsfound.append(newdict)
    if len(formsfound) == 0:
        flash('No search results found!', 'danger')
        return redirect('/')
    else:
        return render_template('search.html', searchterm=searchterm,
                               forms=formsfound)


# Delete filled forms when Delete button is clicked
@app.route('/delete_filledform/<int:fid>/<string:owner>/\
           <string:date_time>', methods=['POST'])
@is_logged_in
def delete_filledform(fid, owner, date_time):
    # Open database connection
    db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Execute the SQL command
    cursor.execute('DELETE FROM completedforms WHERE \
                   fid = %s AND owner = %s AND \
                   datetime = %s', [fid, owner, date_time])
    cursor.execute('DELETE FROM formfilled WHERE \
                   fid = %s AND username = %s AND \
                   datetime = %s', [fid, owner, date_time])

    # Commit your changes in the database
    db.commit()
    db.close()

    flash('Form Deleted', 'success')

    return redirect(url_for('home'))


# display a filled form when user clicks that form in dashboard
@app.route('/edit_filledform/<string:username>/<int:fid>/<string:title>/<string:date_time>', methods=['GET', 'POST'])
@is_logged_in
def edit_filledform(username, fid, title, date_time):
    formQuestions = []
    oldFormInputs = {}
    # Open database connection
    db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    result = cursor.execute('SELECT * FROM question WHERE \
                            fid = %s ORDER BY qid ASC', [fid])
    if result > 0:
        data = cursor.fetchall()
        for row in data:
            newdict = {}
            newdict['type'] = row[1]
            newdict['question'] = row[2]
            newdict['fqid'] = str(row[0])+'-'+str(row[3])
            newdict['typeparam'] = row[4]
            if row[5] == 1:
                newdict['req'] = "required"
            else:
                newdict['req'] = ""
            formQuestions.append(newdict)

    # Get the old answers from the database
    result = cursor.execute('SELECT * FROM formfilled WHERE \
                            fid = %s AND username = %s AND \
                            datetime = %s', [fid, username, date_time])
    if result > 0:
        data = cursor.fetchall()
        for row in data:
            oldFormInputs[str(row[0])+'-'+str(row[2])] = row[3]

    # get user input
    if request.method == 'POST':
        input = request.form
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('look----', input)
        # Get Form Fields
        for key in input:
            print(key, input[key])
            ids = key.split('-')
            cursor.execute('UPDATE formfilled SET answer=%s, \
                           datetime=%s WHERE fid=%s AND username=%s AND \
                           qid=%s AND datetime=%s', [input[key], time,
                                                     ids[0],
                                                     str(session['user']),
                                                     ids[1], date_time])
        cursor.execute('UPDATE completedforms SET datetime=%s \
                       WHERE fid=%s AND owner=%s AND datetime=%s',
                       [time, fid, username, date_time])
        db.commit()
        return redirect(url_for('home'))
    db.close()
    # determine if the viewer can only edit or view
    editPermission = (username == session['user'])
    if not editPermission:
        editability = 'disabled'
    else:
        editability = ''
    return render_template('editform.html', edit=editability,
                           formQuestions=formQuestions,
                           answers=oldFormInputs, formId=id,
                           formTitle=title)


# Updates the status of the form to Approved or Dennied
@app.route('/update_status/<int:fid>/<string:owner>/<string:date_time>/<string:status>', methods=['GET', 'POST'])
@is_logged_in
def update_status(fid, owner, status, date_time):
    # Open database connection
    db = pymysql.connect(HOST, USER, PASSWORD, DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Execute the SQL command
    cursor.execute('UPDATE completedforms SET status=%s WHERE \
                   fid=%s AND owner=%s AND datetime=%s',
                   [status, fid, owner, date_time])
    cursor.execute('SELECT title FROM forminfo WHERE fid=%s', [fid])
    formname = cursor.fetchall()[0][0]
    # Commit your changes in the database
    db.commit()
    db.close()

    msgstr = 'Hi!\n\nThe form ' + formname + ' you submitted has been ' \
        + status + '.\n\nFor more information please go to \
        fastforms.ml\n\nThree\'s a Crowd Team'

    send_email('Status update', MAIL_USERNAME, [owner], msgstr)

    flash(('Status chagned to ' + status), 'success')

    return redirect(url_for('home'))

# def send_async_email(app, msg):
#     with app.app_context():
#         mail.send(msg)


def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    # msg.html = html_body
    mail.send(msg)
    # Thread(target=send_async_email, args=(app, msg)).start()


# if __name__ != '__main__':
#     app.config['SESSION_TYPE'] = 'filesystem'
#     sess.init_app(app)
#     app.run(host="0.0.0.0", debug=True)
#     gunicorn_logger = logging.getLogger(‘gunicorn.error’)
#     app.logger.handlers = gunicorn_logger.handlers
#     app.logger.setLevel(gunicorn_logger.level)


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.run(host="0.0.0.0", debug=True)
