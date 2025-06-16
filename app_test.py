from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key-pillbox-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pillbox_test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèles de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nom_complet = db.Column(db.String(100))
    nb_prises_jour = db.Column(db.Integer, default=1)
    avatar = db.Column(db.String(200))
    events = db.relationship('PillboxEvent', backref='user', lazy=True)
    
    def get_avatar_url(self):
        if self.avatar:
            return f'/static/uploads/{self.avatar}'
        return f'https://ui-avatars.com/api/?name={self.username}&background=667eea&color=fff'

class PillboxEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Route principale
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Récupérer les événements du jour
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    events = PillboxEvent.query.filter_by(user_id=user.id).order_by(PillboxEvent.timestamp.desc()).all()
    
    # Événements du jour
    events_today = [e for e in events if e.timestamp >= start_of_day]
    ouvertures_jour = len([e for e in events_today if e.status == 'opened'])
    
    # Dernier événement et état actuel
    dernier_event = events[0] if events else None
    etat = dernier_event.status if dernier_event else 'closed'
    
    return render_template('dashboard.html',
                         user=user,
                         events=events[:10],
                         ouvertures_jour=ouvertures_jour,
                         dernier_event=dernier_event,
                         etat=etat)

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        
        return render_template('login.html', error='Identifiants incorrects')
    
    return render_template('login.html')

# Route de déconnexion
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Webhook simplifié avec paramètres dans l'URL
@app.route("/webhook/simple/<int:user_id>/<status>", methods=["POST", "GET"])
def simple_webhook(user_id, status):
    """Webhook simplifié où les paramètres sont dans l'URL"""
    print(f"Webhook simple reçu - User ID: {user_id}, Status: {status}")
    
    # Normaliser le status
    status = status.lower()
    
    # Vérifier que l'utilisateur existe
    user = User.query.get(user_id)
    if user:
        event = PillboxEvent(user_id=user_id, status=status)
        db.session.add(event)
        db.session.commit()
        print(f"Event enregistré pour {user.username} (ID {user_id})")
        message = f"Event enregistré: {status} pour {user.username}"
    else:
        print(f"Utilisateur {user_id} non trouvé, création de l'événement quand même")
        # On crée l'événement même si l'utilisateur n'existe pas encore
        event = PillboxEvent(user_id=user_id, status=status)
        db.session.add(event)
        db.session.commit()
        message = f"Event enregistré: {status} pour utilisateur ID {user_id}"
    
    # Retourner une réponse simple pour IFTTT
    return jsonify({
        "success": True, 
        "message": message,
        "user_id": user_id, 
        "status": status
    })

# Webhook avec parsing JSON (compatible avec l'ancienne méthode)
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
    
    # Enregistrer l'événement
    event = PillboxEvent(user_id=user_id, status=status)
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"success": True, "user_id": user_id, "status": status})

# Route de test du webhook
@app.route('/test-webhook')
def test_webhook():
    return render_template('test_webhook.html')

# Route API pour obtenir les événements
@app.route('/api/events/<int:user_id>')
def api_events(user_id):
    events = PillboxEvent.query.filter_by(user_id=user_id).order_by(PillboxEvent.timestamp.desc()).limit(20).all()
    return jsonify([{
        'id': e.id,
        'status': e.status,
        'timestamp': e.timestamp.isoformat()
    } for e in events])

# Créer les tables et l'utilisateur admin si nécessaire
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Créer l'utilisateur admin s'il n'existe pas
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            nom_complet='Administrateur',
            nb_prises_jour=1
        )
        db.session.add(admin)
        
        # Créer un utilisateur test pour ID 3
        test_user = User.query.filter_by(username='patient3').first()
        if not test_user:
            test_user = User(
                username='patient3',
                password=generate_password_hash('test123'),
                nom_complet='Patient Test 3',
                nb_prises_jour=2
            )
            db.session.add(test_user)
        
        db.session.commit()
        print("Utilisateurs créés: admin (ID 1) et patient3 (ID 3)")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8001, debug=True)
