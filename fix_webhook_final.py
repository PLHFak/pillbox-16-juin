import re

with open('app.py', 'r') as f:
    content = f.read()

# Chercher et remplacer toute la fonction webhook
pattern = r'@app\.route\("/webhook/pillbox".*?\n    return jsonify\(.*?\)\n'

new_webhook = '''@app.route("/webhook/pillbox", methods=["POST"])
def pillbox_webhook():
    data = request.json
    print(f"Webhook recu: {data}")
    
    # Extraire le status selon le format IFTTT
    status = "unknown"
    try:
        if 'description' in data and data['description']:
            # IFTTT envoie dans description
            import json
            desc_data = json.loads(data['description'])
            status = desc_data.get('value', 'unknown')
        elif 'value' in data:
            # Format direct
            status = data['value']
    except Exception as e:
        print(f"Erreur parsing: {e}")
    
    print(f"Status final: {status}")
    
    event = PillboxEvent(user_id=3, status=status)
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Event recorded"})
'''

content = re.sub(pattern, new_webhook + '\n', content, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(content)

print("Webhook corrige!")
