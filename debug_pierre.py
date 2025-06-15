from app import app, db, User, PillboxEvent
import datetime

with app.app_context():
    print("=== DEBUG PIERRE ===")
    
    # Vérifier Pierre
    pierre = User.query.filter_by(username="pierre").first()
    if pierre:
        print(f"Pierre existe: ID={pierre.id}")
        
        # Voir ses événements
        events = PillboxEvent.query.filter_by(user_id=pierre.id).order_by(
            PillboxEvent.timestamp.desc()
        ).limit(5).all()
        
        print(f"\nÉvénements de Pierre (ID {pierre.id}):")
        for e in events:
            print(f"  - {e.timestamp}: {e.status}")
        
        if not events:
            print("  Aucun événement trouvé!")
            print("\n�� Vérifiez dans IFTTT:")
            print(f'   Pour ouverture: {{"value": "opened_{pierre.id}"}}')
            print(f'   Pour fermeture: {{"value": "closed_{pierre.id}"}}')
    else:
        print("❌ Pierre n'existe pas!")
