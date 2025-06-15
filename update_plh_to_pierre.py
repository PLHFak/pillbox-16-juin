from app import app, db, User

with app.app_context():
    # Trouver l'utilisateur Plh
    plh = User.query.filter_by(username="Plh").first()
    
    if plh:
        print(f"Utilisateur trouvé: {plh.username} (ID: {plh.id})")
        print(f"Email: {plh.email}")
        
        # Mettre à jour
        plh.username = "pierre"
        plh.nb_prises_jour = 1  # 1 prise par jour comme demandé
        plh.set_password("pierre123")  # Réinitialiser le mot de passe
        
        db.session.commit()
        
        print("\n✅ Mise à jour effectuée!")
        print(f"Nouveau username: pierre")
        print(f"Mot de passe: pierre123")
        print(f"Prises/jour: 1")
        print(f"ID reste: {plh.id}")
        print(f"Webhooks IFTTT: opened_{plh.id}, closed_{plh.id}")
    else:
        print("❌ Utilisateur Plh non trouvé")
