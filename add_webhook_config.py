# Script pour ajouter la configuration webhook

with open('app.py', 'r') as f:
    content = f.read()

# Ajouter les colonnes dans la classe User
user_columns = '''    nb_prises_jour = db.Column(db.Integer, default=2)
    refresh_interval = db.Column(db.Integer, default=5)  # Secondes
    device_id = db.Column(db.String(50))  # ID du capteur eWeLink
    webhook_url = db.Column(db.String(200))  # URL personnalisée (optionnel)'''

content = content.replace('nb_prises_jour = db.Column(db.Integer, default=2)', user_columns)

with open('app.py', 'w') as f:
    f.write(content)

print("Colonnes ajoutées!")
