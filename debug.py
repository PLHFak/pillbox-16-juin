from app import *

with app.app_context():
    print("=== EVENTS ===")
    events = PillboxEvent.query.all()
    print(f"Total: {len(events)} events")
    for e in events[-5:]:
        print(f"User {e.user_id}: {e.status}")
    
    print("\n=== USERS ===")
    users = User.query.all()
    for u in users:
        print(f"ID {u.id}: {u.username}")
