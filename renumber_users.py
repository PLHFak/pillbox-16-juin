from app import app, db, User, PillboxEvent

with app.app_context():
    # D'abord, voir les utilisateurs actuels
    print("Utilisateurs actuels:")
    for user in User.query.all():
        print(f"ID: {user.id}, Username: {user.username}")
    
    # Renommer temporairement pour éviter les conflits
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.id = 999  # Temporaire
        db.session.commit()
    
    # Décaler tous les utilisateurs
    for i in range(4, 1, -1):  # 4, 3, 2
        user = User.query.get(i)
        if user:
            # Mettre à jour les events d'abord
            PillboxEvent.query.filter_by(user_id=i).update({'user_id': i-1})
            # Puis l'utilisateur
            user.id = i - 1
            db.session.commit()
    
    # Mettre admin à 0
    admin = User.query.get(999)
    if admin:
        PillboxEvent.query.filter_by(user_id=999).update({'user_id': 0})
        admin.id = 0
        db.session.commit()
    
    # Vérifier le résultat
    print("\nNouvelle numérotation:")
    for user in User.query.order_by(User.id).all():
        print(f"ID: {user.id}, Username: {user.username}")

print("Renumérotation terminée!")
