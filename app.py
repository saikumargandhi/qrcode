# import required packages like flask, sqlite3, flask sessions used for login
from flask import Flask, render_template, request, session
from flask_session import Session
import sqlite3
import hashlib
import random
from fpdf import FPDF
from flask import send_from_directory
import webbrowser
import os
import qrcode
from datetime import datetime
import smtplib
import ssl
from datetime import date

# setting up flask session
global msg
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# smtp credentials
smtp_server = "smtp.hostinger.com"
port = 587  # For starttls
sender_email = "help@qrproject.tech"
password = "Helpqr@48"

# flask route used to go to index or home page


@app.route("/")
def index():
    title = "Home Page"
    data = {
        'title': title
    }
    # the title for the html template page is passed via data variable - this data varibale is called flask varibale
    return render_template("index.html", data=data)

# flask route for contactus page


@app.route("/contactus")
def contactus():
    title = "Contact Us Page"
    data = {
        'title': title
    }
    return render_template("contactus.html", data=data)


# flaks route for logout page
@app.route("/logout")
def logout():
    title = "Logout Page"
    data = {
        'title': title,
        'msg': 'You have been logged out successfully.'
    }
    # logout msg is sent to html page and session are cleared
    session['userid'] = None
    session['role'] = None
    return render_template("logout.html", data=data)

# Change password


# Show all student records


@ app.route("/student_records")
def student_records():
    title = "All Students"
    rows = []
    try:
        # get connected to the database and fetch all trips info posted by users
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            userid = session["userid"]
            cur.execute(
                "select * from users where id!=:who and role=1", {"who": userid})
            rows = cur.fetchall()
            if(rows):
                msg_code = 200
            else:
                msg_code = 400
    except:
        con.rollback()
        msg_code = 404
# throw data into html templates from the backend flask code
    finally:
        data = {
            "title": title,
            "msg_code": msg_code,
        }
        return render_template("student_records.html", data=data, students_data=rows)
        con.close()

# updating student info from edit page


@ app.route("/update_student", methods=['POST'])
def update_student():
    title = "Saving Student Info"
    # if method is post then only executes remaining steps
    if request.method == 'POST':
        try:
            # fetch all variables and store in local variables
            stu_id = request.form['stu_id']
            usermail = request.form['signmail']
            username = request.form['username']
            mobile = request.form['mobile']
            year = request.form['year']
            branch = request.form['branch']
            gender = request.form['gender']
            # check in database whether user with the usermail exists or not
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("update users set name=?,mail=?,mobile=?,gender=?,year=?,branch=? where id=?",
                            (username, usermail, mobile, gender, year, branch, stu_id))
                con.commit()
                msg = 'Student record updated successfully.'
        except:
            con.rollback()
            msg = "Error in connecting to database"
        # pass the flask variable to page to show message to user
        finally:
            data = {
                "title": title,
                "msg": msg,
            }
            return render_template("edit_student.html", data=data)
            con.close()


# closing and deleting trip information that is already posted
@ app.route("/edit_student/<action>/<student_id>/", methods=['GET'])
def edit_student(action, student_id):
    title = "Edit Students"
    student_data = []
    redirect_url = "edit_student.html"
    try:
        # get connected to database
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            userid = session["userid"]
            # if action is close close the trip from database
            if(action == "delete"):
                cur.execute(
                    "delete from users where id!=? and id=?", (userid, student_id))
                msg = "Student record deleted successfully"
                # if action is edit, redirect to another html page and fill forms info of the trip
            elif(action == "edit"):
                cur.execute(
                    "select * from users where id!=? and id=?", (userid, student_id))
                student_data = cur.fetchone()
                msg = "Editing Trip"
                redirect_url = "updating_student.html"
            con.commit()
    except:
        con.rollback()
        msg = "Unable to perform operation"
        # send the fetched info to the front end page
    finally:
        data = {
            "title": title,
            "msg": msg,
            "student_data": student_data
        }
        print(data)
        return render_template(redirect_url, data=data)
        con.close()


# validating qrcode from bonafide certificate
@ app.route("/validate/<userid>/", methods=['GET'])
def validate(userid):
    title = "Validating Student"
    student_data = []
    redirect_url = "validate_student.html"
    try:
        # get connected to database
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            # if action is close close the trip from database
            cur.execute("select * from users where id=:who", {"who": userid})
            student_data = cur.fetchone()
            if(student_data):
                msg = "Student belongs to Bridgewater State University"
            else:
                msg = "Student doesn't belong to Bridgewater State University"
            con.commit()
    except:
        con.rollback()
        msg = "Unable to perform operation"
        # send the fetched info to the front end page
    finally:
        data = {
            "title": title,
            "msg": msg,
            "student_data": student_data
        }
        print(data)
        return render_template(redirect_url, data=data)
        con.close()


# validating qrcode from idcard certificate
@ app.route("/fetch_student/<userid>/<hashmail>", methods=['GET'])
def fetch_student(userid, hashmail):
    title = "Fetching Student Info"
    student_data = []
    msg = "Unable to Fetch Student Info, Params mismatch"
    msg_code = ""
    books_data = []
    fdate = date.today().strftime('%Y-%m-%d')
    redirect_url = "fetch_student.html"
    try:
        # get connected to database
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            # if action is close close the trip from database
            cur.execute("select * from users where id=:who", {"who": userid})
            student_data = cur.fetchall()
            cur.execute("select * from books")
            books_data = cur.fetchall()
            if(student_data):
                print(hashmail)
                print(hashlib.sha256(student_data[0][2].encode()).hexdigest())
                if(hashlib.sha256(student_data[0][2].encode()).hexdigest() == hashmail):
                    message = """From:BSU Admin <help@qrproject.tech>
To: me
MIME-Version: 1.0
Content-type: text/html
Subject: Student Info Accessed by Admin

Your ID Card QR Code has been used to access your Student Information by BSU Admin.<br><br>If you haven't provided your ID Card for scanning, please report it at Office.<br><br>Regards,<br><br>BSU Admin,<br><br>help@qrproject.tech
"""
                    # Create a secure SSL context
                    context = ssl.create_default_context()
                    # Try to log in to server and send email
                    try:
                        server = smtplib.SMTP(smtp_server, port)
                        server.ehlo()  # Can be omitted
                        # Secure the connection
                        server.starttls(context=context)
                        server.ehlo()  # Can be omitted
                        server.login(sender_email, password)
                        server.sendmail(
                            sender_email, student_data[0][2], message)
                    except Exception as e:
                        # Print any error messages to stdout
                        print(e)
                    finally:
                        server.quit()
                    msg_code = "ok"
            else:
                msg_code = "no"
            con.commit()
    except:
        con.rollback()
        msg = "Unable to perform operation"
        msg_code = "dberror"
        # send the fetched info to the front end page
    finally:
        data = {
            "title": title,
            "msg": msg,
            "msg_code": msg_code,
            "student_data": student_data,
            "books_data": books_data,
            "assign_date": fdate
        }
        print(data)
        return render_template(redirect_url, data=data)
        con.close()


# flask route for registration page


@app.route("/register", methods=["POST"])
def register():
    title = "Adding Student Info"
    # if method is post then only executes remaining steps
    if request.method == 'POST':
        try:
            # fetch all variables and store in local variables
            usermail = request.form['signmail']
            username = request.form['username']
            mobile = request.form['mobile']
            year = request.form['year']
            branch = request.form['branch']
            gender = request.form['gender']
            role = "1"
            # encode pwd with sha256 algorithm
            userpwd = hashlib.sha256(
                request.form['userpassword'].encode()).hexdigest()
            # check in database whether user with the usermail exists or not
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("select * from users where mail=:who",
                            {"who": usermail})
                rows = cur.fetchone()
                # if exists show user exists and stop
                if(rows):
                    msg = "Mail already exists."
                else:
                    # if usermail doesnt exist then insert the form values into the database
                    cur.execute("INSERT INTO users(name,mail,mobile,pwd,gender,role,year,branch)VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                (username, usermail, mobile, userpwd, gender, role, year, branch))
                    con.commit()
                    cur.execute(
                        "select id from users where mail=:who", {"who": usermail})
                    rows = cur.fetchone()
                    if(rows):
                        stu_id = rows[0]
                        message = """From:BSU Admin <help@qrproject.tech>
To: me
MIME-Version: 1.0
Content-type: text/html
Subject: Account Created in BSU

An account has been created by BSU Admin for you.<br><br>Your student id is """+str(stu_id)+""", login mail id is """+usermail+""" and your password is '"""+request.form['userpassword']+"""'.<br><br>You can login into your account by using <a href="https://qrcode-flask.herokuapp.com/" target="_blank">this link</a>.<br><br>Userid and Password are confidential.<br><br>Regards,<br><br>BSU Admin,<br><br>help@qrproject.tech
"""
                        # Create a secure SSL context
                        context = ssl.create_default_context()
                        # Try to log in to server and send email
                        try:
                            server = smtplib.SMTP(smtp_server, port)
                            server.ehlo()  # Can be omitted
                            # Secure the connection
                            server.starttls(context=context)
                            server.ehlo()  # Can be omitted
                            server.login(sender_email, password)
                            server.sendmail(
                                sender_email, usermail, message)
                        except Exception as e:
                            # Print any error messages to stdout
                            print(e)
                        finally:
                            server.quit()
                    msg = 'Registered Successfully.'

        except Exception as e:
            con.rollback()
            print(e)
            msg = "Error in connecting to database"
        # pass the flask variable to page to show message to user
        finally:
            data = {
                "title": title,
                "msg": msg,
            }
            return render_template("register.html", data=data)
            con.close()

# flask route to login


@app.route("/login", methods=["POST"])
def login():
    title = "Login Page"
    # if method is post then only executes remaining steps
    if request.method == 'POST':
        try:
            # fetch usermail and pwd from login form
            # encrypt pwd with sha256 and cross verify the usermail and encrypted pwd with values in database
            usermail = request.form['usermail']
            userpwd = hashlib.sha256(
                request.form['password'].encode()).hexdigest()
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                # cur.execute('select * from users')
                cur.execute(
                    "select * from users where mail=? and pwd=?", (usermail, userpwd))
                rows = cur.fetchall()
                if(rows):
                    msg = 'Logged in Successfully.'
                    msg_code = 200
                    session["userid"] = rows[0][0]
                    session["role"] = rows[0][6]
                    if(rows[0][3] == "male"):
                        session["profile_icon"] = "icons/m" + \
                            str(random.randint(1, 4))+".png"
                    elif(rows[0][3] == "female"):
                        session["profile_icon"] = "icons/g" + \
                            str(random.randint(1, 7))+".png"
                else:
                    msg = 'Invalid Credentials'
                    msg_code = 400
                    # if credentials match assign a random icon as profile photo and set login session
        except:
            con.rollback()
            msg = "Error in connecting to database"
            msg_code = 404

        finally:
            # pass the messgae to the html template
            data = {
                "title": title,
                "msg": msg,
                "msg_code": msg_code
            }
            print(data)
            return render_template("login.html", data=data)
            con.close()


# flask routing method to dashboard page


@app.route("/assigned_books")
def assigned_books():
    title = "Assigned Books Page"
    assigned_data = []
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        userid = session["userid"]
        cur.execute("select * from assign_books inner join users on users.id=assign_books.stu_id inner join books on assign_books.assign_book_id=books.book_id")
        assigned_data = cur.fetchall()
    con.close()
    data = {
        'title': title,
        'assigned_data': assigned_data
    }
    print(data)
    return render_template("assigned_books.html", data=data)

# flask routing method to dashboard page


@ app.route("/dashboard")
def dashboard():
    title = "Dashboard Page"
    data = {
        'title': title,
    }
    return render_template("dashboard.html", data=data)

# flask routing method to student dashboard page


@ app.route("/stu_dashboard")
def stu_dashboard():
    title = "Dashboard Page"
    data = {
        'title': title,
    }
    return render_template("stu_dashboard.html", data=data)


# assign books to students
@ app.route("/assign_book", methods=["POST"])
def assign_book():
    title = "Assigning Book"
    data = {
        'title': title,
    }
    try:
        stu_id = request.form['stu_id']
        tod_date = request.form['tod_date']
        assign_book = request.form['assign_book']
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("insert into assign_books (stu_id,assign_book_id,assign_date) VALUES (?,?,?)",
                        (stu_id, assign_book, tod_date))
            con.commit()
        con.close()
        msg = "Book Assigned Successfully"
    except Exception as e:
        msg = e
    data["msg"] = msg
    print(data)
    return render_template("assign_book.html", data=data)

# update profile


@ app.route("/update_profile", methods=["POST"])
def update_profile():
    title = "Updating Profile"
    data = {
        'title': title,
    }
    try:
        username = request.form['profilename']
        usermail = request.form['profilemail']
        usermob = request.form['profilemobile']
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            userid = session["userid"]
            cur.execute(
                "update users set mail=?,name=?,mobile=? where id=?", (usermail, username, usermob, userid))
            con.commit()
        con.close()
        msg = "Profile Updated Successfully"
    except Exception as e:
        msg = e
    data["msg"] = msg
    print(data)
    return render_template("updateprofile.html", data=data)

# flask route to invoke profile page


@ app.route("/my_profile")
def my_profile():
    title = "My Profile Page"
    data = {
        'title': title,
    }
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        userid = session["userid"]
        cur.execute("select * from users where id="+str(userid))
        rows = cur.fetchall()
        data["user_name"] = rows[0][1]
        data["user_mail"] = rows[0][2]
        data["user_mob"] = rows[0][5]
    con.close()
    print(data)
    return render_template("profile.html", data=data)


# download id card


@ app.route("/download_id_card")
def download_id_card():
    title = "ID Card"
    data = {
        'title': title,
    }
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        userid = session["userid"]
        cur.execute("select * from users where id=:who", {"who": userid})
        rows = cur.fetchall()
        if(rows):
            if(rows[0][6] == 1):
                path = "./static/idcards/"
                qrcode.make('https://qrcode-flask.herokuapp.com/fetch_student/' +
                            str(userid)+"/"+hashlib.sha256(rows[0][2].encode()).hexdigest()).save(path + rows[0][1]+".png")
                pdf = FPDF('P', 'mm', 'A4')
                pdf.add_page()
                pdf.image(path+"base_card.png", x=20, y=20, w=150, h=80)
                pdf.image(path+rows[0][1]+".png", x=25, y=50, w=55, h=48)
                pdf.set_font('Arial', '', 12)
                pdf.ln(42)
                pdf.cell(18)
                pdf.cell(70)
                pdf.cell(25, 5, rows[0][1]+" (ID: "+str(rows[0][0])+")", 0, 1)

                pdf.ln(7)
                pdf.cell(18)
                pdf.cell(70)
                pdf.cell(25, 5, rows[0][5], 0, 1)

                pdf.ln(7)
                pdf.cell(18)
                pdf.cell(70)
                pdf.cell(25, 5, rows[0][8], 0, 1)

                pdf.ln(7)
                pdf.cell(30)
                pdf.cell(70)
                pdf.cell(25, 5, rows[0][7], 0, 1)
                data["filename"] = path+rows[0][1]+'_ID Card.pdf'
                pdf.output(name=data["filename"], dest="F")
                # return send_from_directory(directory='./idcards', path=filename_pdf)
                # data["filename"] =os.path.abspath(data["filename"])
            return render_template("download_files.html", data=data)
    con.close()


@ app.route("/change_password", methods=["POST"])
def change_password():
    title = "Change Password"
    data = {
        'title': title,
    }
    if request.method == 'POST':
        try:
            userid = session["userid"]
            userpwd = hashlib.sha256(
                request.form['userpassword'].encode()).hexdigest()
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                # cur.execute('select * from users')
                cur.execute("update users set pwd=? where id=?",
                            (userpwd, userid))
                con.commit()
                msg = "Password updated successfully"
        except:
            con.rollback()
            msg = "Error in connecting to database"
            msg_code = 404

        finally:
            # pass the messgae to the html template
            data = {
                "title": title,
                "msg": msg
            }
            session["target"] = request.form['from_which']
            return render_template("change_password.html", data=data)
            con.close()


@ app.route("/download_bonafide_card")
def download_bonafide_card():
    title = "ID Card"
    data = {
        'title': title,
    }
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        userid = session["userid"]
        cur.execute("select * from users where id=:who", {"who": userid})
        rows = cur.fetchall()
        if(rows):
            if(rows[0][6] == 1):
                path = "./static/idcards/"
                qrcode.make('https://qrcode-flask.herokuapp.com/validate/' +
                            str(userid)+"/").save(path + rows[0][1]+".png")
                pdf = FPDF('P', 'mm', 'A4')
                pdf.add_page()

                pdf.ln(15)
                pdf.set_font('Arial', 'B', 15)
                pdf.cell(40)
                pdf.cell(25, 5, "Bridgewater State University", 0, 1)
                pdf.set_font('Arial', '', 12)
                pdf.image(path+rows[0][1]+".png", x=140, y=32, w=44, h=38)

                pdf.ln(12)
                pdf.cell(18)
                pdf.cell(25, 5, "Date: " +
                         datetime.today().strftime('%d-%m-%Y'), 0, 1)
                pdf.ln(2)
                pdf.cell(18)
                pdf.cell(25, 5, "Time: " +
                         datetime.today().strftime('%H:%M:%S'), 0, 1)

                pdf.ln(18)
                pdf.cell(68)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(25, 5, "Bonafide Certificate", 0, 1)
                pdf.set_font('Arial', '', 12)

                pdf.ln(15)
                pdf.cell(10)
                pdf.multi_cell(
                    0, 8, "Bridgewater State University is a public university with its main campus in Bridgewater, Massachusetts. It is the largest of nine state universities in Massachusetts.", 0, 1)

                pdf.ln(5)
                pdf.cell(10)
                pdf.multi_cell(0, 8, "This is to certify that Mr/Ms. "+rows[0][1]+" of ID "+str(rows[0][0])+" is a student of "+rows[0]
                               [7]+" of "+rows[0][8]+" branch of the Bridgewater State University (Massachusetts). ", 0, 1)

                pdf.ln(5)
                pdf.cell(10)
                pdf.multi_cell(
                    0, 8, "He/She is a Bonafide Student of Bridgewater State University (Massachusetts). ", 0, 1)

                pdf.ln(3)
                pdf.cell(10)
                pdf.multi_cell(
                    0, 8, "He/She is reliable, sincere, hardworking and bears a good moral charecter.", 0, 1)

                pdf.line(155, 178, 200, 178)

                pdf.ln(30)
                pdf.cell(144)
                pdf.cell(25, 5, "Principal/Registrar/Dean", 0, 1)

                pdf.ln(10)
                pdf.cell(11)
                pdf.cell(25, 5, "Bridgewater State University", 0, 1)
                pdf.set_font('Arial', '', 9)
                pdf.cell(15)
                pdf.cell(25, 5, "Bridgewater, Massachusetts", 0, 1)

                pdf.ln(10)
                pdf.cell(35)
                pdf.multi_cell(
                    0, 5, "This Bonafide Certificate is generated automatically and doesn't require any Signature or Stamp.", 0, 1)
                pdf.cell(42)
                pdf.multi_cell(
                    0, 5, "Validity of this Certificate can be verified by scanning the QR code present at the top.", 0, 1)
                data["filename"] = path+rows[0][1]+'_Bonafide Certificate.pdf'
                pdf.output(name=data["filename"], dest="F")
                # return send_from_directory(directory='./idcards', path=filename_pdf)
                # data["filename"] =os.path.abspath(data["filename"])
            return render_template("download_files.html", data=data)
    con.close()


# main flask call, this calls the routing method and starts the server
# debug is set to true to start the debug log
if __name__ == "__main__":
    app.run(debug=True)
