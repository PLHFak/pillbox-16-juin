from app import app, db, User, PillboxEvent
import datetime

with app.app_context():
    print("=== DEBUG ÉVÉNEMENTS ===\n")
    
    # Pour chaque utilisateur
    for user in User.query.all():
        print(f"Utilisateur: {user.username} (ID: {user.id})")
        
        # Ses 5 derniers événements
        events = PillboxEvent.query.filter_by(user_id=user.id).order_by(
            PillboxEvent.timestamp.desc()
        ).limit(5).all()
        
        if events:
            for e in events:
                print(f"  - {e.timestamp.strftime('%d/%m %H:%M')} : {e.status}")
        else:
            print(f"  Aucun événement")
        print()
