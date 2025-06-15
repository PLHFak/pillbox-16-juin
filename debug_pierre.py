from app import app, db, User, PillboxEvent
import datetime

with app.app_context():
    print("=== DEBUG PIERRE ===")
    
    # V√©rifier Pierre
    pierre = User.query.filter_by(username="pierre").first()
    if pierre:
        print(f"Pierre existe: ID={pierre.id}")
        
        # Voir ses √©v√©nements
        events = PillboxEvent.query.filter_by(user_id=pierre.id).order_by(
            PillboxEvent.timestamp.desc()
        ).limit(5).all()
        
        print(f"\n√âv√©nements de Pierre (ID {pierre.id}):")
        for e in events:
            print(f"  - {e.timestamp}: {e.status}")
        
        if not events:
            print("  Aucun √©v√©nement trouv√©!")
            print("\nÌ†ΩÌ≤° V√©rifiez dans IFTTT:")
            print(f'   Pour ouverture: {{"value": "opened_{pierre.id}"}}')
            print(f'   Pour fermeture: {{"value": "closed_{pierre.id}"}}')
    else:
        print("‚ùå Pierre n'existe pas!")
