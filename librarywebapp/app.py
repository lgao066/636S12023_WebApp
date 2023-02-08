from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

#region SQL Queries
search_avaiable_books = '''SELECT bookcopies.bookcopyid, books.booktitle, books.author, format, 
                            IF(min(returned)=1, "On Loan", "Available")  AS returned, 
                            DATE_ADD(max(loandate), INTERVAL 28 DAY)  AS duedate
                            FROM bookcopies
                            inner join books on books.bookid = bookcopies.bookid
                            left join loans on bookcopies.bookcopyid = loans.bookcopyid
                            group by bookcopies.bookcopyid
                            having books.booktitle like %s and books.author like %s
                            order by books.booktitle asc;'''

search_available_borrowers = '''SELECT * FROM borrowers where firstname like %s and familyname like %s and %s;'''

add_new_borrower = '''INSERT INTO borrowers(firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s);'''

edit_existing_borrower = '''update borrowers SET %s %s %s %s %s %s %s %s where borrowerid = %s;'''

sql_update_loan = '''INSERT INTO loans(bookcopyid, borrowerid, loandate, returned)
                    VALUES(%s, %s, CURDATE(), 0);'''
#endregion


def listbooks(page = "publicbooklist.html"):
    connection = getCursor()
    connection.execute("SELECT * FROM books;")
    bookList = connection.fetchall()
    print(bookList)
    return render_template(page, booklist = bookList)

def searchbooks(page = "publicbooksearch.html"):
    connection = getCursor()
    author = request.form.get('author')
    author = "" if author is None else author.strip()
    title = request.form.get('title')
    title = "" if title is None else title.strip()
    sqlauthor = "%" + author + "%"  
    sqltitle = "%" + title + "%"  
    connection.execute(search_avaiable_books, (sqltitle, sqlauthor,))
    bookList = connection.fetchall()
    return render_template(page, booklist = bookList, author = author, title = title)

def listborrowers(page = "staffborrowersearch.html"):
    connection = getCursor()
    
    firstname = request.form.get('firstname')
    firstname = "" if firstname is None else firstname.strip()

    lastname = request.form.get('lastname')
    lastname = "" if lastname is None else lastname.strip()
    
    borrowerid = request.form.get('borrowerid')
    borrowerid = "" if borrowerid is None else borrowerid.strip()
    
    sqlfirstname = "'%" + firstname + "%'"
    sqllastname = "'%" + lastname + "%'"
    sqlborrowerid = "1=1" if borrowerid == "" else "borrowerid = " + borrowerid

    sql = search_available_borrowers % (sqlfirstname, sqllastname, sqlborrowerid,)
    connection.execute(sql)
    borrowerList = connection.fetchall()
    return render_template(page, borrowerlist = borrowerList, firstname = firstname, lastname = lastname, borrowerid = borrowerid)

#region App routing

# Main pages
@app.route("/")
def public_home():
    return render_template("publicbase.html")

@app.route("/staff")
def staff_home():
    return render_template("staffbase.html")

# Search pages
@app.route("/staff/search")
@app.route("/staff/search", methods=["POST"])
def staff_searchbooks():
    return searchbooks("staffbooksearch.html")

@app.route("/search")
@app.route("/search", methods=["POST"])
def public_searchbooks():
    return searchbooks()

# Book list pages
@app.route("/staff/listbooks")
def staff_listbooks():
    return listbooks("staffbooklist.html")

@app.route("/listbooks")
def public_listbooks():
    return listbooks()

# Borrower pages
@app.route("/staff/listborrowers")
@app.route("/staff/listborrowers", methods=["POST"])
def searchborrowers():
    return listborrowers()

@app.route("/staff/editborrowers")
def editborrowers():
    return listborrowers("staffeditborrower.html")

@app.route("/staff/editborrowers", methods=["POST"])
def editoraddborrowers():
    borrowerid = request.form.get('borrowerid')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    dob = request.form.get('dob')
    housenum = request.form.get('housenum')
    street = request.form.get('street')
    town = request.form.get('town')
    city = request.form.get('city')
    postcode = request.form.get('postcode')
    connection = getCursor()
    if borrowerid == "":
        connection.execute(add_new_borrower, (firstname, lastname, dob, housenum, street, town, city, postcode, ))
    else:
        print("edit")
        #connection.execute(edit_existing_borrower, (firstname, lastname, dob, housenum, street, town, city, postcode, borrowerid, ))
    return listborrowers("staffeditborrower.html")

#  pages
@app.route("/staff/loanbook")
def loanbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    sql = """SELECT * FROM bookcopies
inner join books on books.bookid = bookcopies.bookid
 WHERE bookcopyid not in (SELECT bookcopyid from loans where returned <> 1 or returned is NULL);"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("addloan.html", loandate = todaydate,borrowers = borrowerList, books= bookList)

@app.route("/staff/loan/add", methods=["POST"])
def addloan():
    borrowerid = request.form.get('borrower')
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (borrowerid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",(borrowerid, bookid, str(loandate),))
    return redirect("/currentloans")

@app.route("/staff/currentloans")
def currentloans():
    connection = getCursor()
    sql=""" select br.borrowerid, br.firstname, br.familyname,  
                l.borrowerid, l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
                b.category, b.yearofpublication, bc.format 
            from books b
                inner join bookcopies bc on b.bookid = bc.bookid
                    inner join loans l on bc.bookcopyid = l.bookcopyid
                        inner join borrowers br on l.borrowerid = br.borrowerid
            order by br.familyname, br.firstname, l.loandate;"""
    connection.execute(sql)
    loanList = connection.fetchall()
    return render_template("currentloans.html", loanlist = loanList)
#endregion



if __name__=="__app__":
    app.run(debug=True)