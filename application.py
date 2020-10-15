import os
from datetime import datetime
from flask import Flask, session, render_template, request, redirect, url_for
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
logged_in = False

current_room = "Main"

chat_log = []
chat_log1 = []
chat_log2 = []

chat_rooms = {}

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
def login():    
    if request.method == "GET":        
        if session.get("user_id") != None:
            if session.get("current_channel") != None:
                url = 'channel/' + session["current_channel"]
                return redirect(url_for('channel_view', room=session["current_channel"]))
            else:
                return redirect(url_for('index'))
        else:
            return render_template("login.html")
    else:
        session["user_id"] = request.form.get("user_id")
        name = session.get("user_id")
        rows = db.execute("SELECT * FROM users where name = :name;", {"name": name})
        result = rows.fetchone()
        if(result == None):
            print("YES!")
            return redirect("/create")
        else:
            print("NO!")
            return redirect("/index")
        
@app.route("/index", methods=["GET", "POST"])
def index():
    if session.get("user_id") != None:
        # todo select all current chat rooms        
     #   rooms = db.execute("SELECT name FROM chatroom;")
    #    for name in rooms:
    #        name = mame.replace("(", "").replace(")", "").replace("'", "")
            
        return render_template("index.html", user_id = session["user_id"], chat_log = chat_log, chat_rooms = chat_rooms)
    else:
        return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    user_name = request.form.get("user_name")
    user_id = request.form.get("user_id")
    password = request.form.get("password")
    
    db.execute("INSERT INTO users values (:user_id, :user_name, :password)", {"user_id": user_id, "user_name": user_name, "password": password})
    db.execute("COMMIT")
    
    return render_template("index.html")
    
@app.route("/channel/<string:room>", methods=["GET", "POST"])
def channel_view(room):
    session["current_channel"] = room
    this_chat_log = chat_rooms[room]
    return render_template("channel.html", user_id = session["user_id"], room=room, chat_log = this_chat_log, chat_rooms = chat_rooms)
  
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
