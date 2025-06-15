from app import *
import datetime

with app.app_context():
    print("\n=== DERNIERS EVENTS (tous users) ===")
    events = PillboxEvent.query.order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    for e in events:
        print(f"{e.timestamp.strftime('%H:%M:%S')} - User {e.user_id}: {e.status}")
    
    print("\n=== EVENTS DE PLH (user 3) ===")
    plh_events = PillboxEvent.query.filter_by(user_id=3).order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    print(f"Total pour PLH: {len(plh_events)}")
    for e in plh_events:
        print(f"{e.timestamp.strftime('%H:%M:%S')} - {e.status}")
    
    print("\n=== EVENTS D'AUJOURD'HUI ===")
    today = datetime.date.today()
    today_events = []
    for e in events:
        if e.timestamp.date() == today:
            today_events.append(e)
    print(f"Aujourd'hui: {len(today_events)} events")
