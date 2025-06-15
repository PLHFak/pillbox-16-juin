# Script pour mettre à jour la gestion des webhooks
import re

# Lire app.py
with open('app.py', 'r') as f:
    content = f.read()

# Trouver et remplacer la route webhook existante
new_webhook_route = '''@app.route("/webhook/pillbox", methods=["POST"])
def pillbox_webhook():
    """Webhook général qui détecte l'utilisateur par le message"""
    data = request.json
    print(f"Webhook recu: {data}")
    
    # Extraire le status et l'ID utilisateur
    status = "unknown"
    user_id = 1  # Par défaut admin
    
    try:
        if 'description' in data and data['description']:
            # IFTTT envoie dans description
            desc_data = json.loads(data['description'])
            value = desc_data.get('value', 'unknown')
            
            # Chercher un pattern comme "opened_2" ou "closed_3"
            if '_' in value:
                parts = value.split('_')
                status = parts[0]  # opened ou closed
                if len(parts) > 1 and parts[1].isdigit():
                    user_id = int(parts[1])
            else:
                status = value
        elif 'value' in data:
            # Format direct
            value = data['value']
            if '_' in value:
                parts = value.split('_')
                status = parts[0]
                if len(parts) > 1 and parts[1].isdigit():
                    user_id = int(parts[1])
            else:
                status = value
    except Exception as e:
        print(f"Erreur parsing: {e}")
    
    print(f"Status: {status}, User ID: {user_id}")
    
    # Vérifier que l'utilisateur existe
    user = User.query.get(user_id)
    if user:
        event = PillboxEvent(user_id=user_id, status=status)
        db.session.add(event)
        db.session.commit()
        print(f"Event enregistré pour {user.username}")
    else:
        print(f"Utilisateur {user_id} non trouvé")
    
    return jsonify({"success": True, "user_id": user_id, "status": status})'''

# Chercher l'ancienne route webhook
pattern = r'@app\.route\("/webhook/pillbox".*?\n    return jsonify\(.*?\)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content[:match.start()] + new_webhook_route + content[match.end():]
    print("✅ Route webhook mise à jour")
else:
    print("❌ Route webhook non trouvée")

# Ajouter une route d'aide pour les utilisateurs
help_route = '''

@app.route("/webhook-help")
@login_required
def webhook_help():
    """Page d'aide pour configurer IFTTT"""
    return render_template_string(\'\'\'
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
    \'\'\')'''

# Ajouter la route d'aide si elle n'existe pas
if 'webhook-help' not in content:
    # L'ajouter avant le if __name__
    pos = content.find('if __name__ == "__main__":')
    if pos > 0:
        content = content[:pos] + help_route + '\n\n' + content[pos:]
        print("✅ Route d'aide ajoutée")

# Sauvegarder
with open('app.py', 'w') as f:
    f.write(content)

print("\n✅ Mise à jour terminée!")
print("\nMaintenant dans IFTTT, utilisez :")
print("- Pour Marie (ID 2) : opened_2 et closed_2")
print("- Pour Pierre (ID 3) : opened_3 et closed_3")
print("- etc.")
