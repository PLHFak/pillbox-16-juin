import re

with open('app.py', 'r') as f:
    content = f.read()

# Améliorer update_profile
new_update_profile = '''@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    """Mise à jour du profil avec timezone"""
    current_user.nom_complet = request.form.get("nom_complet")
    current_user.nb_prises_jour = int(request.form.get("nb_prises_jour", 2))
    
    # Nouveau : timezone
    timezone = request.form.get("timezone", "Europe/Paris")
    if timezone in pytz.all_timezones:
        current_user.timezone = timezone
    
    db.session.commit()
    return redirect(url_for("dashboard"))'''

# Remplacer
pattern = r'@app\.route\("/update_profile".*?\n    return redirect\(url_for\("dashboard"\)\)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content[:match.start()] + new_update_profile + content[match.end():]

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Route update_profile mise à jour!")
