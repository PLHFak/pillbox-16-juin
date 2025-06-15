import re

with open('app.py', 'r') as f:
    content = f.read()

# Nouvelle route register
new_register = '''@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        nom_complet = request.form.get("nom_complet")
        nb_prises_jour = int(request.form.get("nb_prises_jour", 2))
        refresh_interval = int(request.form.get("refresh_interval", 5))
        device_id = request.form.get("device_id", "")
        
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Utilisateur existe deja!")
        
        user = User(
            username=username, 
            email=email, 
            nom_complet=nom_complet,
            nb_prises_jour=nb_prises_jour,
            refresh_interval=refresh_interval,
            device_id=device_id
        )
        user.set_password(password)
        
        # Gerer upload de photo
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                from werkzeug.utils import secure_filename
                filename = secure_filename(f"{username}_{photo.filename}")
                photo_path = os.path.join('static', 'uploads', filename)
                photo.save(photo_path)
                user.photo_url = f"/static/uploads/{filename}"
        
        db.session.add(user)
        db.session.commit()
        
        # Afficher l'URL webhook personnalisée
        return f"""
        <div style="text-align:center; padding:50px; font-family:Arial;">
            <h2>Inscription réussie!</h2>
            <p>Votre URL webhook personnalisée:</p>
            <code style="background:#f0f0f0; padding:10px; display:block; margin:20px;">
                http://{request.host}/webhook/user/{user.id}
            </code>
            <p>Configurez cette URL dans IFTTT</p>
            <a href="/login" style="display:inline-block; margin-top:20px; padding:10px 20px; background:#007bff; color:white; text-decoration:none; border-radius:5px;">Se connecter</a>
        </div>
        """
    
    return render_template("register.html")'''

# Remplacer la fonction
pattern = r'@app\.route\("/register".*?\n    return render_template\("register.html"\)'
content = re.sub(pattern, new_register, content, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(content)

print("Route register mise à jour!")
