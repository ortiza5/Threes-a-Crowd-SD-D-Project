import pymysql
from threading import Thread
from config import *

def query_forminfo():
    forms = []

    # Open database connection
    db = pymysql.connect(HOST,USER,PASSWORD,DBNAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    result = cursor.execute('SELECT * FROM forminfo')
    if result > 0:
        data = cursor.fetchall()
        # print(data[1][2])
        for row in data:
            newdict = {}
            newdict['fid'] = row[0]
            newdict['category'] = row[1]
            newdict['title'] = row[2]
            newdict['description'] = row[3]
            newdict['pdflink'] = row[4]
            forms.append(newdict)
    return forms



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()