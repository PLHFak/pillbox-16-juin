# Ajouter la route de supervision
import re

with open('app.py', 'r') as f:
    content = f.read()

# Ajouter la route supervision
supervision_route = '''
@app.route("/supervision")
def supervision():
    """Page de supervision montrant tous les événements"""
    # Récupérer les 30 derniers événements avec info utilisateur
    events = db.session.query(
        PillboxEvent, User
    ).join(
        User, PillboxEvent.user_id == User.id
    ).order_by(
        PillboxEvent.timestamp.desc()
    ).limit(30).all()
    
    # Organiser par utilisateur
    users_data = {}
    for event, user in events:
        if user.username not in users_data:
            users_data[user.username] = {
                'user': user,
                'events': []
            }
        users_data[user.username]['events'].append(event)
    
    return render_template_string(\'\'\'
<!DOCTYPE html>
<html>
<head>
    <title>Supervision - Pillbox Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f8f9fa; }
        .supervision-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            margin-bottom: 30px;
        }
        .user-column {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-height: 600px;
            overflow-y: auto;
        }
        .event-item {
            padding: 8px;
            margin-bottom: 5px;
            border-radius: 5px;
            font-size: 14px;
        }
        .event-opened {
            background-color: #d4edda;
            color: #155724;
        }
        .event-closed {
            background-color: #f8d7da;
            color: #721c24;
        }
        .user-header {
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        .refresh-info {
            text-align: center;
            color: #6c757d;
            margin-top: 20px;
        }
    </style>
    <meta http-equiv="refresh" content="10">
</head>
<body>
    <div class="supervision-header">
        <div class="container">
            <h1><i class="fas fa-chart-line"></i> Supervision des Piluliers</h1>
            <p class="mb-0">Vue en temps réel - 30 derniers événements</p>
        </div>
    </div>

    <div class="container">
        <div class="row">
            {% for username, data in users_data.items() %}
            <div class="col-md-4">
                <div class="user-column">
                    <div class="user-header">
                        <i class="fas fa-user"></i> {{ data.user.nom_complet or username }}
                        <br><small class="text-muted">{{ data.user.nb_prises_jour }} prise(s)/jour</small>
                    </div>
                    
                    {% for event in data.events %}
                    <div class="event-item event-{{ event.status }}">
                        <i class="fas fa-{{ "box-open" if event.status == "opened" else "box" }}"></i>
                        {{ event.timestamp.strftime("%d/%m %H:%M") }}
                        - {{ "Ouvert" if event.status == "opened" else "Fermé" }}
                    </div>
                    {% endfor %}
                    
                    {% if not data.events %}
                    <p class="text-muted text-center">Aucun événement</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="refresh-info">
            <i class="fas fa-sync-alt"></i> Actualisation automatique toutes les 10 secondes
            <br>
            <a href="/login" class="btn btn-sm btn-primary mt-2">
                <i class="fas fa-arrow-left"></i> Retour connexion
            </a>
        </div>
    </div>
</body>
</html>
    \'\'\', users_data=users_data)'''

# Chercher où insérer (avant if __name__)
pos = content.find('if __name__ == "__main__":')
if pos > 0:
    content = content[:pos] + supervision_route + '\n\n' + content[pos:]
    
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Route supervision ajoutée!")
