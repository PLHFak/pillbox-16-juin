from app import app, db, User

with app.app_context():
    print("=== RECHERCHE PAR EMAIL ===")
    user_with_email = User.query.filter_by(email="p.lhoest@gmail.com").first()
    if user_with_email:
        print(f"L'email p.lhoest@gmail.com est utilisé par: {user_with_email.username} (ID: {user_with_email.id})")
    
    print("\n=== TOUS LES UTILISATEURS ===")
    users = User.query.all()
    for u in users:
        print(f"ID {u.id}: {u.username}")
        print(f"  Email: {u.email}")
        print(f"  Nom: {u.nom_complet}")
        print(f"  Prises/jour: {u.nb_prises_jour}")
        print()
    
    # Chercher pierre
    pierre = User.query.filter_by(username="pierre").first()
    if pierre:
        print(f"✅ L'utilisateur 'pierre' existe avec ID: {pierre.id}")
    else:
        print("❌ L'utilisateur 'pierre' n'existe pas")
