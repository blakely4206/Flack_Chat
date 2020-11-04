import os
from datetime import datetime
from flask import Flask, session, render_template, request, redirect, url_for, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit
from models import User

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")    

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chat_log = []

chat_rooms = {}

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
def login():  
    #GET  
    if request.method == "GET":       
        #if there is a user_id in session 
        if session.get("user_id") != None:
            #if the user has a channel in session
            if session.get("current_channel") != None:
                #open that channel
                return redirect(url_for('channel_view', room=session["current_channel"]))
            else:
                #else main page
                return redirect(url_for('index'))
        else:
            #send user to login page
            return render_template("login.html")
    #POST
    else:
        #search database for user
        name = request.form.get("user_id")        
        rows = db.execute("SELECT * FROM users where name = :name;", {"name": name})
        result = rows.fetchone()
        #User not found, send to create user page
        if(result == None):
            return redirect("/register")
        #user found, send to index page, set session user data
        else:
            session["user_id"] = name
            return redirect("/index")

@app.route("/index", methods=["GET", "POST"])
def index():
    #if user is logged in
    if session.get("user_id") != None:
        return render_template("index.html", user_id = session["user_id"], chat_log = chat_log, chat_rooms = chat_rooms)
    #user is not logged in redirect 
    else:
        return redirect("/")

#register new user
@app.route("/register",  methods=["GET","POST"])
def register():
    #GET
    if request.method == "GET":
        return render_template("register.html")
    #POST (Create a user)
    else:
        #TODO VALIDATE USER INPUT
        user_name = request.form.get("user_name")
        user_id = request.form.get("user_id")
        password = request.form.get("password")
    
        #insert into database
        db.execute("INSERT INTO users values (:user_id, :user_name, :password)", {"user_id": user_id, "user_name": user_name, "password": password})
        db.execute("COMMIT")
    
        #return index page
        session["user_id"] = user_id
        return render_template("index.html")
    
@app.route("/channel/<string:room>", methods=["GET", "POST"])
def channel_view(room):
    if session.get("user_id") != None:
        session["current_channel"] = room
        this_chat_log = chat_rooms[room]
        return render_template("channel.html", user_id = session["user_id"], room=room, chat_log = this_chat_log, chat_rooms = chat_rooms)
    else:
        redirect("/")

@app.route("/create_channel", methods=["GET", "POST"])
def create_channel():
    if request.method == "GET":
        return render_template("create_channel.html", user_id = session["user_id"])
    else:
        name = request.form.get("channel_name")
        chat_rooms[name] = []
## todo insert new rooms into db        db.execute("INSERT INTO chatroom values (:name, :creator)", {"name": name, "creator": session.get("user_id")})
        return redirect("channel/" + name)
        
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")
    
@socketio.on("submit")
def reply(data, room):
    message = session['user_id'] + " (" + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ")::   " + data
    if len(chat_rooms[room]) >= 100:
        del chat_rooms[room][0]
    chat_rooms[room].append(message) 
    emit("send reply", message, broadcast=True)
