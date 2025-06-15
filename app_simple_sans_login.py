from flask import Flask, request, jsonify, render_template_string
import datetime
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle simple pour les événements
class PillboxEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)  # opened ou closed
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"Pillbox: {self.status} at {self.timestamp}"

# Page d'accueil simple
@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Moniteur de Pilulier</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status-box { font-size: 24px; margin: 20px 0; padding: 15px; background-color: #f0f0f0; border-radius: 5px; }
            .event-list { border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
            .event-item { margin: 5px 0; padding: 10px; border-bottom: 1px solid #eee; }
            .opened { color: green; }
            .closed { color: red; }
            h1, h2 { color: #333; }
        </style>
        <script>
            function updateEvents() {
                fetch('/api/events')
                    .then(response => response.json())
                    .then(data => {
                        const eventList = document.getElementById('events');
                        eventList.innerHTML = '';
                        
                        if (data.length > 0) {
                            // Mettre à jour le statut actuel
                            const currentStatus = document.getElementById('current-status');
                            currentStatus.textContent = data[0].status;
                            currentStatus.className = data[0].status.toLowerCase();
                            
                            // Afficher les événements
                            data.forEach(event => {
                                const item = document.createElement('div');
                                item.className = 'event-item';
                                item.textContent = `Pilulier ${event.status} à ${event.timestamp}`;
                                eventList.appendChild(item);
                            });
                        }
                    });
            }
            
            // Mettre à jour toutes les 5 secondes
            setInterval(updateEvents, 5000);
            // Mise à jour initiale
            document.addEventListener('DOMContentLoaded', updateEvents);
        </script>
    </head>
    <body>
        <h1>Moniteur de Pilulier</h1>
        <div class="status-box">
            Statut actuel: <span id="current-status">Inconnu</span>
        </div>
        <h2>Événements récents</h2>
        <div class="event-list" id="events">
            Chargement...
        </div>
        <p><a href="/simulator">Ouvrir le simulateur</a></p>
    </body>
    </html>
    """)

# Simulateur
@app.route('/simulator')
def simulator():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simulateur de Pilulier</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .button { 
                padding: 10px 20px; 
                margin: 10px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .open-button { background-color: #4CAF50; color: white; }
            .close-button { background-color: #f44336; color: white; }
        </style>
    </head>
    <body>
        <h1>Simulateur de Pilulier</h1>
        <button class="button open-button" onclick="sendEvent('opened')">Ouvrir</button>
        <button class="button close-button" onclick="sendEvent('closed')">Fermer</button>
        <p><a href="/">Retour</a></p>
        
        <script>
            function sendEvent(status) {
                fetch('/webhook/pillbox', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({value: status}),
                })
                .then(response => response.json())
                .then(data => alert('Événement envoyé!'));
            }
        </script>
    </body>
    </html>
    """)

# Webhook pour IFTTT
@app.route('/webhook/pillbox', methods=['POST'])
def pillbox_webhook():
    data = request.json
    print(f"Webhook reçu: {data}")
    
    # Extraire le status
    status = data.get('value', 'unknown')
    
    # Enregistrer l'événement
    new_event = PillboxEvent(status=status)
    db.session.add(new_event)
    db.session.commit()
    
    return jsonify({"success": True, "message": f"Pillbox {status} event recorded"})

# API pour obtenir les événements
@app.route('/api/events', methods=['GET'])
def get_events():
    events = PillboxEvent.query.order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    result = []
    
    for event in events:
        result.append({
            'id': event.id,
            'status': event.status,
            'timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)
