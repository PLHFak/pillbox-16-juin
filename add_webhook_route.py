# Script pour ajouter la route webhook manquante

with open('app.py', 'r') as f:
    content = f.read()

# La route à ajouter
new_route = '''
# Webhook par utilisateur (URL simple)
@app.route("/webhook/user/<int:user_id>", methods=["POST"])
def user_webhook(user_id):
    """Webhook spécifique par utilisateur"""
    data = request.json
    print(f"Webhook user {user_id} reçu: {data}")
    
    # IFTTT peut envoyer dans 'value' ou 'description'
    value = None
    if data:
        if 'value' in data:
            value = data['value']
        elif 'description' in data:
            # IFTTT met parfois le JSON dans description
            try:
                import json as json_lib
                desc_data = json_lib.loads(data['description'])
                value = desc_data.get('value')
            except:
                value = data['description']
    
    status = value.lower() if value else 'unknown'
    
    # Enregistrer l'événement
    user = User.query.get(user_id)
    if user:
        event = PillboxEvent(user_id=user_id, status=status)
        db.session.add(event)
        db.session.commit()
        print(f"Event {status} enregistré pour {user.username}")
        return jsonify({"success": True, "status": status, "user": user.username})
    
    return jsonify({"error": "User not found"}), 404

'''

# Trouver où insérer (juste avant la dernière ligne)
if "if __name__ == '__main__':" in content:
    parts = content.split("if __name__ == '__main__':")
    new_content = parts[0] + new_route + "\nif __name__ == '__main__':" + parts[1]
    
    with open('app.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Route webhook ajoutée avec succès!")
else:
    print("❌ Impossible de trouver où insérer la route")
