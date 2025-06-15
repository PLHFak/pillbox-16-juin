# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pillbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modeles de base de donnees
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    nom_complet = db.Column(db.String(100))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PillboxEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    
    # Pour l instant, retournons du texte simple
    return "<h1>Login Page</h1><form method=POST><input name=username><input type=password name=password><button>Login</button></form>"

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
    html = "<h1>Dashboard</h1>"
    html += "<p>Bonjour " + current_user.username + "</p>"
    html += "<a href=/logout>Logout</a><br><br>"
    html += "<h2>Events:</h2>"
    for e in events:
        html += "<p>" + e.timestamp.strftime("%H:%M") + " - " + e.status + "</p>"
    return html

@app.route("/webhook/pillbox", methods=["POST"])
def pillbox_webhook():
    data = request.json
    status = data.get("value", "unknown")
    
    event = PillboxEvent(user_id=1, status=status)
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Event recorded"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Creer admin si n existe pas
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@example.com", nom_complet="Administrateur")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
    
    app.run(host="0.0.0.0", port=8000, debug=True)
