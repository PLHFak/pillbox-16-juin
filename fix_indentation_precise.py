with open('app_fix.py', 'r') as f:
    content = f.read()

# Corriger le mélange des lignes nb_prises_jour et timezone
content = content.replace(
    'nb_prises_jour = db.Column(db.Integer, \n    timezone = db.Column(db.String(50), default="Europe/Paris")  # Fuseau horairedefault=2\n)',
    'nb_prises_jour = db.Column(db.Integer, default=2)\n    timezone = db.Column(db.String(50), default="Europe/Paris")  # Fuseau horaire'
)

with open('app_fix.py', 'w') as f:
    f.write(content)

print("✅ Correction appliquée!")
