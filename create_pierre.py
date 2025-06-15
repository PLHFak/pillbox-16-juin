from app import app, db, User

with app.app_context():
    # Vérifier d'abord si Pierre existe
    pierre = User.query.filter_by(username="pierre").first()
    
    if not pierre:
        print("Création de Pierre...")
        pierre = User(
            username="pierre",
            email="p.lhoest@gmail.com",
            nom_complet="Pierre Lhoest",
            nb_prises_jour=1
        )
        pierre.set_password("pierre123")
        db.session.add(pierre)
        db.session.commit()
        print("✅ Pierre créé avec succès!")
    else:
        print("Pierre existe déjà")
    
    print(f"ID de Pierre: {pierre.id}")
    
    # Afficher tous les utilisateurs
    print("\n=== TOUS LES UTILISATEURS ===")
    for u in User.query.all():
        print(f"ID {u.id}: {u.username} ({u.email})")
