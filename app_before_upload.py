# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pillbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MODE DEVELOPPEMENT
RESET_DB_ON_START = True

# Modeles
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    nom_complet = db.Column(db.String(100))
    photo_url = db.Column(db.String(200))
    date_naissance = db.Column(db.Date)
    nb_prises_jour = db.Column(db.Integer, default=2)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_avatar_url(self):
        if self.photo_url:
            return self.photo_url
        email_hash = hashlib.md5(self.email.lower().encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=200"

class PillboxEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    duree_secondes = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_database():
    """Initialise la base avec des donnees de test"""
    if RESET_DB_ON_START:
        print("Suppression ancienne base...")
        db.drop_all()
    
    print("Creation des tables...")
    db.create_all()
    
    # Creer admin
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        print("Creation utilisateur admin...")
        admin = User(
            username="admin", 
            email="admin@example.com", 
            nom_complet="Administrateur",
            nb_prises_jour=2
        )
        admin.set_password("admin123")
        db.session.add(admin)
    
    # Creer marie
    marie = User.query.filter_by(username="marie").first()
    if not marie:
        print("Creation utilisateur marie...")
        marie = User(
            username="marie",
            email="marie.dupont@example.com",
            nom_complet="Marie Dupont",
            date_naissance=datetime.date(1945, 3, 15),
            nb_prises_jour=3
        )
        marie.set_password("marie123")
        db.session.add(marie)
    
    # Events de test
    if RESET_DB_ON_START:
        print("Ajout events de test...")
        now = datetime.datetime.now()
        events = [
            PillboxEvent(user_id=1, status="opened", timestamp=now - datetime.timedelta(hours=6)),
            PillboxEvent(user_id=1, status="closed", timestamp=now - datetime.timedelta(hours=6) + datetime.timedelta(minutes=2)),
            PillboxEvent(user_id=1, status="opened", timestamp=now - datetime.timedelta(hours=2)),
            PillboxEvent(user_id=1, status="closed", timestamp=now - datetime.timedelta(hours=2) + datetime.timedelta(minutes=3)),
        ]
        for event in events:
            db.session.add(event)
    
    db.session.commit()
    print("Base initialisee!")

# Routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        nom_complet = request.form.get("nom_complet")
        
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Utilisateur existe deja!")
        
        user = User(username=username, email=email, nom_complet=nom_complet)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    events = PillboxEvent.query.filter_by(user_id=current_user.id).order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    
    dernier_event = events[0] if events else None
    etat = "closed" if not dernier_event else dernier_event.status
    
    aujourdhui = datetime.date.today()
    nb_ouvertures = 0
    for e in events:
        if e.timestamp.date() == aujourdhui and e.status == "opened":
            nb_ouvertures += 1
    
    date_jour = datetime.datetime.now().strftime("%A %d %B %Y")
    
    return render_template("better.html",
        user=current_user,
        events=events,
        etat=etat,
        nb_ouvertures=nb_ouvertures,
        dernier_event=dernier_event,
        date_jour=date_jour
    )

@app.route("/webhook/pillbox", methods=["POST"])
def pillbox_webhook():
    data = request.json
    status = data.get("value", "unknown")
    
    print(f"Webhook recu: {data}")
    
    event = PillboxEvent(user_id=1, status=status)
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Event recorded"})

if __name__ == "__main__":
    with app.app_context():
        init_database()
    
    app.run(host="0.0.0.0", port=8000, debug=True)
