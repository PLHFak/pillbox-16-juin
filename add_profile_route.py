import re

with open('app.py', 'r') as f:
    content = f.read()

# Vérifier si la route profile existe
if '@app.route("/profile")' not in content:
    # Ajouter la route profile
    profile_route = '''
@app.route("/profile")
@login_required
def profile():
    """Page de profil utilisateur"""
    return render_template("profile.html")

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    """Mise à jour du profil"""
    current_user.nom_complet = request.form.get("nom_complet")
    current_user.nb_prises_jour = int(request.form.get("nb_prises_jour", 2))
    db.session.commit()
    return redirect(url_for("dashboard"))
'''
    
    # Insérer avant if __name__
    pos = content.find('if __name__ == "__main__":')
    if pos > 0:
        content = content[:pos] + profile_route + '\n\n' + content[pos:]
        print("✅ Routes profile ajoutées")
    
with open('app.py', 'w') as f:
    f.write(content)
