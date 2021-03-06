from flask import Flask, session, render_template,request, url_for,redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from itsdangerous import URLSafeTimedSerializer
import smtplib
import math,random
from email.message import EmailMessage

import os
app = Flask(__name__)


# Configure session to use filesystem

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://tlkbyctryyffkn:b0ab12cc98ffab444f5d1d07329271b38c4e253f6cf3d1368bed287623e3dda8@ec2-54-235-86-101.compute-1.amazonaws.com:5432/d4bmrsh5lptv18")
db = scoped_session(sessionmaker(bind=engine))

notes = []
#notes.append(note)
# Python code to illustrate Sending mail from
# your Gmail account

def generateotp():
    digits = "0123456789"
    OTP =""
    for i in range(4):
        OTP+=digits[math.floor(random.random() *10)]
    return OTP

OTP = generateotp()

#flag = 0
def sendotp(sender):
    EMAIL_ADDRESS = "software.engwkze@gmail.com"
    EMAIL_PASSWORD = "April@2017"

    #contacts = ['surajkr143singh@gmail.com', 'rashikrishna16@example.com']

    msg = EmailMessage()
    msg['Subject'] = 'Your OTP for '
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = sender

    msg.set_content(OTP)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

#@app.route("/verify")
#def verify():
#    flag = int(request.form.get("flag"))

@app.route("/verify", methods=["POST"])
def otpcheck():
    #entered_otp = request.form.get("otp")
    sender = request.form.get("sender")
    sendotp(sender)
    #if(entered_otp == OTP):
    #    print(entered_otp)
    #    return "Successfully Verified"
    #else :
    #    return "Incorrect OTP"
    return "otp send"






@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST" :
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        category = request.form.get('category')
        gender = request.form.get('gender')
        age = request.form.get('age')
        branch = request.form.get('branch')
        position = request.form.get("position")

        if category == "admin" :
            if (db.execute("SELECT * FROM admin WHERE userid=:username",{"username":username}).fetchone() is None) :
                #sendotp()
                #while flag==0:
                #    pass
                #print(flag)
                db.execute("INSERT INTO admin (name,userid,password) VALUES (:name,:username,:password)",{"username":username, "name":name, "password":password})
                db.commit()
                query = db.execute("SELECT * FROM admin WHERE userid=:username",{"username":username}).fetchone()
                id = query.id
                db.execute("INSERT INTO admin_info (id,name,age,gender) VALUES (:id,:name,:age,:gender)",{"name":name,"id":id,"age":age,"gender":gender})
                db.commit()
                message = ("Successfully Registered as Admin")
            else :
                message = ("Username Already exists")

        elif category == "faculty":
            if (db.execute("SELECT * FROM faculty WHERE userid=:username",{"username":username}).fetchone() is None) :
                db.execute("INSERT INTO faculty (name,userid,password) VALUES (:name,:username,:password)",{"username":username, "name":name, "password":password})
                db.commit()
                query = db.execute("SELECT * FROM faculty WHERE userid=:username",{"username":username}).fetchone()
                id = query.id
                db.execute("INSERT INTO faculty_info (id,name,age,department,gender,position) VALUES (:id,:name,:age,:branch,:gender,:position)",{"name":name,"id":id,"age":age,"branch":branch,"gender":gender,"position":position})
                db.commit()
                message = ("Successfully Registered as faculty")
            else :
                message = ("Username Already exists")

        else:
            if (db.execute("SELECT * FROM others WHERE userid=:username",{"username":username}).fetchone() is None) :
                db.execute("INSERT INTO others (name,userid,password) VALUES (:name,:username,:password)",{"username":username, "name":name, "password":password})
                db.commit()
                message = ("Successfully Registered as others")
            else :
                message = ("Username Already exists")

    else :
        message=(" ")

    return render_template("register.html",message=message)

@app.route("/")
def index():
    return render_template("slide.html")

@app.route("/login")
def login():
    message = ("")
    return render_template("login.html",message=message)

@app.route("/home",methods=["POST","GET"])
def home():
    if request.method == "POST":
        username =request.form.get("v_username")
        password = request.form.get("v_password")
        category = request.form.get("v_category")

        if category == "admin" :
            query=db.execute("SELECT * FROM admin WHERE userid=:username AND password=:password",{"username":username, "password":password}).fetchone()
            if (query is None):
                message = ("Incorrect Username or Password Admin")
                return render_template("login.html",message=message)
            else :
                session["logged_user"]=username
                session["category"]="admin"
                session["id"] = query.id
                id = query.id
                info = db.execute("SELECT * FROM admin_info WHERE id=:id",{"id":id}).fetchone()
                leave = db.execute("SELECT * FROM admin_leave WHERE id=:id",{"id":id}).fetchone()
                if (leave is None) :
                    leaveapplied = 0;
                else :
                    leaveapplied = 1;
                return render_template("home.html",userdetail = query,userinfo=info,leaveapplied=leaveapplied,admin=1)

        elif category == "faculty" :
            query = db.execute("SELECT * FROM faculty WHERE userid=:username AND password=:password",{"username":username, "password":password}).fetchone()
            if (query is None):
                message = ("Incorrect Username or Password faculty")
                return render_template("login.html",message=message)
            else :
                session["logged_user"]=username
                session["category"] = "faculty"
                id = query.id
                session["id"]=id
                info = db.execute("SELECT * FROM faculty_info WHERE id=:id",{"id":id}).fetchone()
                leave = db.execute("SELECT * FROM faculty_leave WHERE id=:id",{"id":id}).fetchone()
                if (leave is None) :
                    leaveapplied = 0;
                else :
                    leaveapplied = 1;
                if db.execute("SELECT * FROM faculty_info WHERE id=:id AND position iLIKE '%hod%'  ",{"id":id}).fetchone() is None:
                    hod = 0;
                else :
                    hod = 1;
                return render_template("home.html",userdetail = query,userinfo=info,leaveapplied=leaveapplied,hod=hod,admin=0)

        elif category == "others" :
            query = db.execute("SELECT * FROM others WHERE userid=:username AND password=:password",{"username":username, "password":password}).fetchone()
            if (query is None):
                message = ("Incorrect Username or Password Others")
                return render_template("login.html",message=message)
            else :
                session["logged_user"]=username
                session["category"]="others"
                session["id"] = query.id
                return render_template("home.html",userdetail = query)
    elif request.method == "GET" :
        username = session["logged_user"]
        category = session["category"]
        id = session["id"]
        if category == "admin" :
            query = db.execute("SELECT * FROM admin WHERE id=:id",{"id":id}).fetchone()
            info = db.execute("SELECT * FROM admin_info WHERE id=:id",{"id":id}).fetchone()
            leave = db.execute("SELECT * FROM admin_leave WHERE id=:id",{"id":id}).fetchone()
            if (leave is None) :
                leaveapplied = 0;
            else :
                leaveapplied = 1;
            return render_template("home.html",userdetail = query,userinfo=info,leaveapplied=leaveapplied,admin=1)
        elif category == "faculty" :
                query = db.execute("SELECT * FROM faculty WHERE id=:id",{"id":id}).fetchone()
                info = db.execute("SELECT * FROM faculty_info WHERE id=:id",{"id":id}).fetchone()
                leave = db.execute("SELECT * FROM faculty_leave WHERE id=:id",{"id":id}).fetchone()
                if (leave is None) :
                    leaveapplied = 0;
                else :
                    leaveapplied = 1;
                return render_template("home.html",userdetail = query,userinfo=info,leaveapplied=leaveapplied,admin=0)

@app.route("/admin")
def admin():
    ctr = 10;

@app.route("/rejoin", methods=["POST","GET"])
def rejoin():
    user_id = session["id"]
    if request.method == "POST" :
        rejoin_date = request.form.get("rejoin_date")
        if session["category"] == "faculty":
            db.execute("INSERT INTO faculty_rejoin (rejoin_date,id) VALUES (:rejoin_date,:user_id)",{"rejoin_date":rejoin_date,"user_id":user_id})
            db.commit()
            db.execute("DELETE FROM faculty_leave WHERE id=:id",{"id":user_id})
            db.commit()
            return redirect(url_for("home"))
        elif session["category"] == "admin" :
            db.execute("INSERT INTO admin_rejoin (rejoin_date,id) VALUES (:rejoin_date,:user_id)",{"rejoin_date":rejoin_date,"user_id":user_id})
            db.commit()
            db.execute("DELETE FROM admin_leave WHERE id=:id",{"id":user_id})
            db.commit()
            return redirect(url_for("home"))
        else :
            db.execute("INSERT INTO others_rejoin (rejoin_date,id) VALUES (:rejoin_date,:user_id)",{"rejoin_date":rejoin_date,"user_id":user_id})
            db.commit()
            db.execute("DELETE FROM others_leave WHERE id=:id",{"id":user_id})
            db.commit()
            return redirect(url_for("home"))
    leave_from = db.execute("SELECT leave_from FROM faculty_leave WHERE id =:id",{"id":user_id}).fetchone()
    leave_upto = db.execute("SELECT leave_upto FROM faculty_leave WHERE id =:id",{"id":user_id}).fetchone()
    query = db.execute("SELECT * FROM faculty_info WHERE id = :user_id",{"user_id":user_id}).fetchone()
    return render_template("rejoining.html",info=query,leave_from=leave_from,leave_upto=leave_upto)

@app.route("/leave", methods=["POST","GET"])
def leave():

    user = session["logged_user"]
    cat = session["category"]
    id = session["id"]
    if request.method == "POST":
        idd = int(id)
        leave_from = request.form.get("leave_from")
        leave_upto = request.form.get("leave_upto")
        nature = request.form.get("nature")
        no_of_days = int(request.form.get("no_of_days"))
        reason = request.form.get("reason")
        if(cat == "faculty"):
            db.execute("INSERT INTO faculty_leave (id,leave_from,leave_upto,approved,no_of_days,reason,nature) VALUES (:idd, :leave_from, :leave_upto, 0,:no_of_days,:reason,:nature)",{"idd":idd,"leave_from":leave_from,"leave_upto":leave_upto,"no_of_days":no_of_days,"nature":nature, "reason":reason})
            db.commit()
            return redirect(url_for('home'))
        elif(cat == "admin"):
            db.execute("INSERT INTO admin_leave (id,leave_from,leave_upto,approved,no_of_days,reason,nature) VALUES (:idd, :leave_from, :leave_upto, 0,:no_of_days,:reason,:nature)",{"idd":idd,"leave_from":leave_from,"leave_upto":leave_upto,"no_of_days":no_of_days,"nature":nature, "reason":reason})
            db.commit()
            return redirect(url_for('home'))

    if(cat=="faculty"):
        query = db.execute("SELECT * FROM faculty_info WHERE id=:id",{"id":id}).fetchone()
    elif(cat=="admin"):
        query = db.execute("SELECT * FROM admin_info WHERE id=:id",{"id":id}).fetchone()
    return render_template("leaveapplication.html",query=query)

@app.route("/stationleave")
def stationleave():
    return render_template("stationleave.html")

@app.route("/list")
def list():
    id = session["id"]
    if session["category"] == "faculty" :
        info = db.execute("SELECT * FROM faculty_info WHERE id=:id",{"id":id}).fetchone()
        leave = db.execute("SELECT * FROM faculty_leave WHERE id=:id",{"id":id}).fetchone()
        if (leave is None) :
            leaveapplied = 0;
        else :
            leaveapplied = 1;
        lists= db.execute("SELECT * FROM faculty_leave WHERE approved = 0").fetchall()
    elif session["category"] == "admin" :
        info = db.execute("SELECT * FROM admin_info WHERE id=:id",{"id":id}).fetchone()
        leave = db.execute("SELECT * FROM admin_leave WHERE id=:id",{"id":id}).fetchone()
        if (leave is None) :
            leaveapplied = 0;
        else :
            leaveapplied = 1;
        lists= db.execute("SELECT * FROM faculty_leave WHERE approved = 0").fetchall()

    return render_template("list.html",leave=leave,info=info,lists=lists)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

def sendmail(id):
    emails = []
    names = []
    queries = db.execute("SELECT * FROM faculty WHERE id=:id",{"id":id}).fetchall()
    for query in queries:
        emails.append(query.userid)
        names.append(query.name)





if __name__ =="__main__":
    app.run(port=5000)
