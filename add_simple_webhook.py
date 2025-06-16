import re

# Lire le fichier app_test.py
with open('app_test.py', 'r') as f:
    content = f.read()

# Nouvelle route à ajouter après la route webhook existante
new_route = '''
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
'''

# Trouver où insérer la nouvelle route (après la route webhook existante)
pattern = r'(return jsonify\(\{"success": True, "user_id": user_id, "status": status\}\))'
match = re.search(pattern, content)

if match:
    insert_pos = match.end()
    # Ajouter la nouvelle route après la route webhook existante
    new_content = content[:insert_pos] + '\n' + new_route + content[insert_pos:]
    
    with open('app_test.py', 'w') as f:
        f.write(new_content)
    print("✅ Route webhook simple ajoutée!")
else:
    print("❌ Position d'insertion non trouvée")
