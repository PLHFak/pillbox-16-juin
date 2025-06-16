with open('app_to_fix.py', 'r') as f:
    lines = f.readlines()

# Parcourir et corriger la zone problématique
fixed_lines = []
for i, line in enumerate(lines):
    if 'nb_prises_jour = db.Column(db.Integer,' in line and i+1 < len(lines):
        # Si la ligne suivante contient timezone mélangé
        if 'timezone' in lines[i+1] and 'default=2' in lines[i+1]:
            # Corriger ces deux lignes
            fixed_lines.append('    nb_prises_jour = db.Column(db.Integer, default=2)\n')
            fixed_lines.append('    timezone = db.Column(db.String(50), default="Europe/Paris")  # Fuseau horaire\n')
            # Sauter la ligne suivante car on l'a déjà traitée
            continue
    
    # Si c'est la ligne mélangée, on la skip car déjà traitée
    if i > 0 and 'timezone' in line and 'default=2' in line:
        continue
    
    fixed_lines.append(line)

# Écrire le fichier corrigé
with open('app_fixed.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fichier corrigé!")

# Vérifier la correction
print("\nVérification des lignes corrigées:")
with open('app_fixed.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'nb_prises_jour' in line or 'timezone' in line:
            print(f"Ligne {i+1}: {line.strip()}")
