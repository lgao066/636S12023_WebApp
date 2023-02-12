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
avaiable_books_for_borrow = '''SELECT * FROM bookcopies
                                inner join books on books.bookid = bookcopies.bookid
                                WHERE bookcopyid not in (SELECT loans.bookcopyid from loans 
                                                            inner join bookcopies on bookcopies.bookcopyid = loans.bookcopyid
                                                            where (returned <> 1 or returned is NULL)
                                                            and format not in ('eBook', 'Audio Book')
                                                            );'''

search_avaiable_books = '''SELECT bookcopies.bookcopyid, books.booktitle, books.author, format, 
                            IF(min(returned)=1, "Available", "On Loan")  AS returned, 
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

edit_existing_borrower = '''update borrowers SET %s where borrowerid = %s;'''

sql_update_loan = '''INSERT INTO loans(bookcopyid, borrowerid, loandate, returned)
                    VALUES(%s, %s, CURDATE(), 0);'''

sql_update_loan = '''INSERT INTO loans(bookcopyid, borrowerid, loandate, returned)
                    VALUES(%s, %s, CURDATE(), 0);'''

sql_list_newly_added_loan = '''SELECT loanid as LoanID, bookcopyid as BookCopyID, borrowerid AS BorrowerID, 
                    loandate as LoanDate, returned as Returned FROM library.loans 
                    WHERE bookcopyid = %s and borrowerid = %s and loandate = CURDATE();'''

sql_overdue_books = '''SELECT borrowers.familyname As "Family Name", 
                    borrowers.firstname As "First Name", 
                    DATEDIFF(CURDATE(), loandate) As "Days On Loan",
                    books.booktitle As Title
                    FROM loans
                    INNER JOIN borrowers ON loans.borrowerid = borrowers.borrowerid
                    INNER JOIN bookcopies ON loans.bookcopyid = bookcopies.bookcopyid
                    INNER JOIN books ON books.bookid = bookcopies.bookid
                    WHERE returned <> 1 and loandate < DATE_ADD(CURDATE(), INTERVAL -35 DAY)
                    ORDER BY DATEDIFF(CURDATE(), loandate) desc;'''

sql_most_loaned_books = '''SELECT count(loans.loanid) As "Borrowed Times", b.booktitle as Title, b.author as Author, b.category as Category, b.yearofpublication as Year FROM loans
                    INNER JOIN bookcopies ON loans.bookcopyid = bookcopies.bookcopyid
                    RIGHT JOIN books b ON b.bookid = bookcopies.bookid
                    group by b.bookid
                    ORDER BY count(loans.loanid) desc;'''

sql_borrower_summary_in_detail = '''select br.borrowerid, br.firstname, br.familyname,  
                                    l.borrowerid, l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
                                    b.category, b.yearofpublication, bc.format 
                                    from books b
                                    inner join bookcopies bc on b.bookid = bc.bookid
                                    inner join loans l on bc.bookcopyid = l.bookcopyid
                                    inner join borrowers br on l.borrowerid = br.borrowerid
                                    order by br.familyname, br.firstname, l.loandate;''';

sql_borrower_summary = '''select br.borrowerid, br.firstname, br.familyname, count(loanid) as "Num. of Loans"
                            from books b
                            inner join bookcopies bc on b.bookid = bc.bookid
                            inner join loans l on bc.bookcopyid = l.bookcopyid
                            inner join borrowers br on l.borrowerid = br.borrowerid
                            group by br.borrowerid
                            order by count(loanid) desc, borrowerid asc;'''
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
    
    firstname = convert_to_string_stripped(request.form.get('firstname'))
    lastname = convert_to_string_stripped(request.form.get('lastname')) 
    borrowerid = convert_to_string_stripped(request.form.get('borrowerid'))
    
    sqlfirstname = "'%" + firstname + "%'"
    sqllastname = "'%" + lastname + "%'"
    sqlborrowerid = "1=1" if borrowerid == "" else "borrowerid = " + borrowerid

    sql = search_available_borrowers % (sqlfirstname, sqllastname, sqlborrowerid,)
    connection.execute(sql)
    borrowerList = connection.fetchall()
    return render_template(page, borrowerlist = borrowerList, firstname = firstname, lastname = lastname, borrowerid = borrowerid)

def listeditoraddborrowers(page = "staffborrowersearch.html", message = ""):
    connection = getCursor()
    borrowerid = convert_to_string_stripped(request.form.get('borrowerid'))
    sqlborrowerid = "1=1" if borrowerid == "" else "borrowerid = " + borrowerid
    sql = search_available_borrowers % ("'%%'", "'%%'", sqlborrowerid,)
    connection.execute(sql)
    borrowerList = connection.fetchall()
    return render_template(page, borrowerlist = borrowerList, message = message)

def convert_to_string_stripped(ele):
    return "" if (ele is None or ele == None) else ele.strip()

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
    borrowerid = convert_to_string_stripped(request.form.get('borrowerid'))
    firstname = convert_to_string_stripped(request.form.get('firstname'))
    lastname = convert_to_string_stripped(request.form.get('lastname'))
    dob = convert_to_string_stripped(request.form.get('dob'))
    housenum = convert_to_string_stripped(request.form.get('housenum'))
    street = convert_to_string_stripped(request.form.get('street'))
    town = convert_to_string_stripped(request.form.get('town'))
    city = convert_to_string_stripped(request.form.get('city'))
    postcode = convert_to_string_stripped(request.form.get('postcode'))

    borrowerdict = {
        "firstname": firstname,
        "familyname": lastname,
        "dateofbirth": dob,
        "housenumbername": housenum,
        "street": street,
        "town": town,
        "city": city,
        "postalcode": postcode
    }
    
    message = ""
    connection = getCursor()
    if borrowerid == "":
        connection.execute(add_new_borrower, (firstname, lastname, dob, housenum, street, town, city, postcode, ))
    else:
        # Validate if the borrowerId is valid
        sqlborrowerid = "borrowerid = " + borrowerid
        sql = search_available_borrowers % ("'%%'", "'%%'", sqlborrowerid,)
        connection.execute(sql)
        borrower = connection.fetchall()
        if (len(borrower) == 0):
            # borrower trying to edit is not valid
            message = "The current borrower is not found. Please try again!"
            print("error message")
        else:
            sql_set_value = ""
            for key in borrowerdict:
                if (borrowerdict[key] != ""): # value to update
                    sql_set_value = sql_set_value + key + " = '" + borrowerdict[key] + "',"
            sql_update = edit_existing_borrower % (sql_set_value[:-1], borrowerid,)
            connection.execute(sql_update)
    return listeditoraddborrowers("staffeditborrower.html", message = message)

# Add a new loan
@app.route("/staff/loanbook")
def loanbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    connection.execute(avaiable_books_for_borrow)
    bookList = connection.fetchall()
    return render_template("addloan.html", loandate = todaydate,borrowers = borrowerList, books= bookList)

@app.route("/staff/loan/add", methods=["POST"])
def addloan():
    borrowerid = request.form.get('borrower')
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (borrowerid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",(borrowerid, bookid, str(loandate),))
    return redirect("/staff/currentloans")

# Return a book page


# Display a list of all overdue books & their borrowers
@app.route("/staff/overdues")
def overduesummary():
    connection = getCursor()
    connection.execute(sql_most_loaned_books)
    overduesummary = connection.fetchall()
    return render_template("staffoverdues.html", overduesummary = overduesummary)

# Display a Loan Summary
@app.route("/staff/loansummary")
def loansummary():
    connection = getCursor()
    connection.execute(sql_most_loaned_books)
    loansummary = connection.fetchall()
    return render_template("staffloansummary.html", loansummary = loansummary)

# Display a Borrower Summary
@app.route("/staff/currentloans")
def currentloans():
    connection = getCursor()
    connection.execute(sql_borrower_summary_in_detail)
    detailedloanList = connection.fetchall()
    connection.execute(sql_borrower_summary)
    borrowersummary = connection.fetchall()
    return render_template("staffborrowersummary.html", loanlist = detailedloanList, borrowersummary = borrowersummary)
#endregion

if __name__=="__app__":
    app.run(debug=True)