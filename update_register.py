# Script pour mettre à jour la fonction register

import re

# Lire le fichier
with open('app.py', 'r') as f:
    content = f.read()

# Nouvelle fonction register avec upload
new_register = '''@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        nom_complet = request.form.get("nom_complet")
        
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Utilisateur existe deja!")
        
        user = User(username=username, email=email, nom_complet=nom_complet)
        user.set_password(password)
        
        # Gerer upload de photo
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                # Securiser le nom
                from werkzeug.utils import secure_filename
                filename = secure_filename(f"{username}_{photo.filename}")
                # Sauvegarder
                photo_path = os.path.join('static', 'uploads', filename)
                photo.save(photo_path)
                # Stocker le chemin
                user.photo_url = f"/static/uploads/{filename}"
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for("login"))
    
    return render_template("register.html")'''

# Remplacer la fonction register
pattern = r'@app\.route\("/register".*?\n(?=@app\.route|if __name__|$)'
content = re.sub(pattern, new_register + '\n\n', content, flags=re.DOTALL)

# Ajouter l'import secure_filename si pas déjà présent
if 'from werkzeug.utils import secure_filename' not in content:
    content = content.replace('from werkzeug.security import generate_password_hash, check_password_hash',
                              'from werkzeug.security import generate_password_hash, check_password_hash\nfrom werkzeug.utils import secure_filename')

# Écrire le fichier mis à jour
with open('app.py', 'w') as f:
    f.write(content)

print("Fonction register mise à jour avec support upload photo!")
