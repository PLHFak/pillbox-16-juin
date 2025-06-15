from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
from collections import defaultdict
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pillbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèles de base de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PillboxEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
    
    return render_template_string('''
        <h2>Connexion</h2>
        <form method="POST">
            <input name="username" placeholder="Nom d'utilisateur" required><br>
            <input type="password" name="password" placeholder="Mot de passe" required><br>
            <button type="submit">Se connecter</button>
        </form>
        <p>Utilisateur par défaut: admin / password: admin123</p>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    events = PillboxEvent.query.filter_by(user_id=current_user.id).order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    
    events_html = ""
    for event in events:
        events_html += f"<li>{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Pilulier {event.status}</li>"
    
    return render_template_string(f'''
        <h1>Moniteur de Pilulier</h1>
        <p>Bonjour {current_user.username}! <a href="/logout">Déconnexion</a></p>
        <h2>Événements récents:</h2>
        <ul>{events_html if events_html else "<li>Aucun événement</li>"}</ul>
    ''')

@app.route('/webhook/pillbox', methods=['POST'])
def pillbox_webhook():
    data = request.json
    status = data.get('value', 'unknown')
    
    # Pour l'instant, on utilise l'utilisateur 1 (admin)
    event = PillboxEvent(user_id=1, status=status)
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"success": True, "message": f"Event recorded: {status}"})

# Initialisation
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Créer un utilisateur admin s'il n'existe pas
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur admin créé!")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
