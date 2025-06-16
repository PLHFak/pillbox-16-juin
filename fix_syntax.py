# Lire le fichier avec erreur
with open('app.py', 'r') as f:
    lines = f.readlines()

# Trouver et corriger les lignes problématiques
for i, line in enumerate(lines):
    # Corriger la ligne nb_prises_jour mal formatée
    if 'nb_prises_jour = db.Column(db.Integer,' in line and 'timezone' in lines[i+1]:
        # Remplacer les deux lignes mal formatées par les bonnes
        lines[i] = '    nb_prises_jour = db.Column(db.Integer, default=2)\n'
        lines[i+1] = '    timezone = db.Column(db.String(50), default="Europe/Paris")  # Fuseau horaire\n'

# Écrire le fichier corrigé
with open('app.py', 'w') as f:
    f.writelines(lines)

print("✅ Erreur de syntaxe corrigée!")
