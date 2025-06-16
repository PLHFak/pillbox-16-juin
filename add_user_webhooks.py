# Ajouter les routes webhook par utilisateur dans app.py

# Chercher la route webhook existante et ajouter après :

@app.route("/webhook/user/<int:user_id>", methods=["POST"])
def user_webhook(user_id):
    """Webhook spécifique par utilisateur"""
    data = request.json
    print(f"Webhook user {user_id} reçu: {data}")
    
    # Extraire le status (opened ou closed)
    status = data.get('value', 'unknown').lower()
    
    # Vérifier que l'utilisateur existe
    user = User.query.get(user_id)
    if user:
        event = PillboxEvent(user_id=user_id, status=status)
        db.session.add(event)
        db.session.commit()
        print(f"Event {status} enregistré pour {user.username}")
        return jsonify({"success": True, "user": user.username, "status": status})
    
    return jsonify({"success": False, "error": "User not found"}), 404
