from app import app, db, User, PillboxEvent
import datetime

with app.app_context():
    print("=== DEBUG DASHBOARD ===\n")
    
    # Tester pour Pierre (ID 3)
    pierre = User.query.filter_by(username="pierre").first()
    if pierre:
        print(f"Utilisateur: {pierre.username} (ID: {pierre.id})")
        
        # Événements du jour
        today = datetime.date.today()
        events_today = PillboxEvent.query.filter(
            PillboxEvent.user_id == pierre.id,
            db.func.date(PillboxEvent.timestamp) == today
        ).all()
        
        print(f"Événements aujourd'hui: {len(events_today)}")
        for e in events_today:
            print(f"  - {e.timestamp}: {e.status}")
        
        # Tous les événements récents
        all_events = PillboxEvent.query.filter_by(user_id=pierre.id).order_by(
            PillboxEvent.timestamp.desc()
        ).limit(10).all()
        
        print(f"\nTous les événements récents: {len(all_events)}")
        for e in all_events:
            print(f"  - {e.timestamp}: {e.status}")
