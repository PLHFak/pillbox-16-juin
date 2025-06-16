# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pytz

import os
import hashlib
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pillbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MODE DEVELOPPEMENT
RESET_DB_ON_START = False

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
    timezone = db.Column(db.String(50), default="Europe/Paris")  # Fuseau horaire
    
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
        
        # Gerer upload de photo
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                from werkzeug.utils import secure_filename
                filename = secure_filename(f"{username}_{photo.filename}")
                photo_path = os.path.join('static', 'uploads', filename)
                photo.save(photo_path)
                user.photo_url = f"/static/uploads/{filename}"
        
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
    # Timezone de l'utilisateur
    user_tz = pytz.timezone(current_user.timezone or 'Europe/Paris')
    now_user = datetime.datetime.now(user_tz)
    today = now_user.date()
    
    # Événements du jour dans le timezone de l'utilisateur
    events_today = []
    all_events = PillboxEvent.query.filter_by(user_id=current_user.id).all()
    
    for event in all_events:
        # Convertir au timezone de l'utilisateur
        event_time = pytz.utc.localize(event.timestamp).astimezone(user_tz)
        if event_time.date() == today:
            events_today.append(event)
    
    # Compter les ouvertures du jour
    ouvertures_jour = sum(1 for e in events_today if e.status == 'opened')
    
    # Dernier statut
    last_event = PillboxEvent.query.filter_by(
        user_id=current_user.id
    ).order_by(PillboxEvent.timestamp.desc()).first()
    
    current_status = last_event.status if last_event else 'unknown'
    
    # 10 derniers événements
    recent_events = PillboxEvent.query.filter_by(
        user_id=current_user.id
    ).order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    
    # Convertir les timestamps pour l'affichage
    for event in recent_events:
        event.timestamp_local = pytz.utc.localize(event.timestamp).astimezone(user_tz)
    
    return render_template('better_single_bar.html',
        user=current_user,
        etat=current_status,
        ouvertures_jour=ouvertures_jour,
        events=recent_events,
        dernier_event=last_event,
        date_jour=now_user
    )

@app.route("/webhook/pillbox", methods=["POST"])
def pillbox_webhook():
    """Webhook général qui détecte l'utilisateur par le message"""
    data = request.json
    print(f"Webhook recu: {data}")
    
    # Extraire le status et l'ID utilisateur
    status = "unknown"
    user_id = 1  # Par défaut admin
    
    try:
        # Chercher dans tous les champs possibles
        value = None
        
        # Essayer différents endroits où IFTTT pourrait mettre la valeur
        if 'value' in data:
            value = data['value']
        elif 'Value' in data:
            value = data['Value']
        elif 'body' in data:
            value = data['body']
        elif 'Body' in data:
            value = data['Body']
        elif 'description' in data:
            try:
                desc_data = json.loads(data['description'])
                value = desc_data.get('value', None)
            except:
                value = data['description']
        
        print(f"Value trouvé: {value}")
        
        # Parser la valeur
        if value and isinstance(value, str):
            if '_' in value:
                parts = value.split('_')
                if len(parts) >= 2:
                    status = parts[0].lower()  # opened ou closed
                    try:
                        user_id = int(parts[1])
                    except:
                        user_id = 1
            else:
                status = value.lower()
                
    except Exception as e:
        print(f"Erreur parsing: {e}")
    
    print(f"Status final: {status}, User ID: {user_id}")
    
    # Vérifier que l'utilisateur existe
    user = User.query.get(user_id)
    if user:
        event = PillboxEvent(user_id=user_id, status=status)
        db.session.add(event)
        db.session.commit()
        print(f"Event enregistré pour {user.username} (ID {user_id})")
    else:
        print(f"Utilisateur {user_id} non trouvé, utilisation admin")
        event = PillboxEvent(user_id=1, status=status)
        db.session.add(event)
        db.session.commit()
    
    return jsonify({"success": True, "user_id": user_id, "status": status})



@app.route("/webhook-help")
@login_required
def webhook_help():
    """Page d'aide pour configurer IFTTT"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Configuration IFTTT</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>Configuration de votre pilulier dans IFTTT</h2>
            
            <div class="alert alert-info">
                <h4>Votre ID utilisateur : {{ current_user.id }}</h4>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Instructions pour IFTTT</h5>
                </div>
                <div class="card-body">
                    <p>Dans IFTTT, configurez vos webhooks avec ces valeurs :</p>
                    
                    <h6>Pour l'ouverture du pilulier :</h6>
                    <pre class="bg-light p-3">{"value": "opened_{{ current_user.id }}"}</pre>
                    
                    <h6>Pour la fermeture du pilulier :</h6>
                    <pre class="bg-light p-3">{"value": "closed_{{ current_user.id }}"}</pre>
                    
                    <hr>
                    
                    <h6>URL du webhook (reste la même pour tous) :</h6>
                    <pre class="bg-light p-3">http://votre-serveur:8000/webhook/pillbox</pre>
                    
                    <div class="alert alert-success mt-3">
                        <strong>C'est tout !</strong> Le système reconnaîtra automatiquement que c'est vous grâce au numéro {{ current_user.id }}.
                    </div>
                </div>
            </div>
            
            <a href="/dashboard" class="btn btn-primary mt-3">Retour au tableau de bord</a>
        </div>
    </body>
    </html>
    ''')


@app.route("/supervision")
def supervision():
    """Page de supervision"""
    return render_template("supervision.html")


@app.route("/api/supervision")
def api_supervision():
    """API pour la page de supervision"""
    result = {}
    
    # Récupérer les événements par utilisateur
    users = User.query.all()
    for user in users:
        events = PillboxEvent.query.filter_by(user_id=user.id).order_by(
            PillboxEvent.timestamp.desc()
        ).limit(10).all()
        
        result[user.username] = [
            {
                'status': e.status,
                'time': e.timestamp.strftime('%H:%M')
            } for e in events
        ]
    
    return jsonify(result)



@app.route("/profile")
@login_required
def profile():
    """Page de profil utilisateur"""
    return render_template("profile.html")

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    """Mise à jour du profil avec timezone"""
    current_user.nom_complet = request.form.get("nom_complet")
    current_user.nb_prises_jour = int(request.form.get("nb_prises_jour", 2))
    
    # Nouveau : timezone
    timezone = request.form.get("timezone", "Europe/Paris")
    if timezone in pytz.all_timezones:
        current_user.timezone = timezone
    
    db.session.commit()
    return redirect(url_for("dashboard"))



@app.route("/webhook/simple/<int:user_id>/<status>", methods=["GET", "POST"])
def simple_webhook(user_id, status):
    """Webhook ultra simple pour éviter les erreurs IFTTT"""
    try:
        # Enregistrer l'événement
        event = PillboxEvent(user_id=user_id, status=status)
        db.session.add(event)
        db.session.commit()
        return "OK", 200
    except:
        return "ERROR", 500


if __name__ == "__main__":
    with app.app_context():
        init_database()
    
    app.run(host="0.0.0.0", port=8000, debug=True)

@app.route("/webhook/pierre", methods=["POST"])
def webhook_pierre():
    """Webhook dédié à Pierre"""
    data = request.json
    print(f"Webhook Pierre: {data}")
    
    # Toujours pour Pierre (ID 3)
    status = "unknown"
    try:
        if 'description' in data and data['description']:
            desc_data = json.loads(data['description'])
            status = desc_data.get('value', 'unknown')
        elif 'value' in data:
            status = data['value']
    except:
        pass
    
    event = PillboxEvent(user_id=3, status=status)
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"success": True, "user": "pierre"})
