import re

with open('app.py', 'r') as f:
    content = f.read()

# Améliorer la fonction webhook
new_webhook = '''@app.route("/webhook/pillbox", methods=["POST"])
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
    
    return jsonify({"success": True, "user_id": user_id, "status": status})'''

# Remplacer la fonction webhook
pattern = r'@app\.route\("/webhook/pillbox".*?\n    return jsonify\(.*?\)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content[:match.start()] + new_webhook + content[match.end():]
    with open('app.py', 'w') as f:
        f.write(content)
    print("✅ Webhook amélioré!")
else:
    print("❌ Webhook non trouvé")
