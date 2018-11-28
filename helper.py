import pymysql
from config import *

# Takes the information in the database and converts
# it into a usable form (in this case, a list of 
# dictionaries, each of which represents a single form)
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