import re

with open('app.py', 'r') as f:
    content = f.read()

# Nouvelle route home
new_home_route = '''@app.route('/')
@login_required  
def home():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return redirect(url_for('login'))
    
    # Récupérer les événements
    events = PillboxEvent.query.filter_by(user_id=user_id).order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    
    # Statistiques du jour
    today = datetime.datetime.now().date()
    ouvertures_jour = PillboxEvent.query.filter(
        PillboxEvent.user_id == user_id,
        PillboxEvent.status == 'opened',
        db.func.date(PillboxEvent.timestamp) == today
    ).count()
    
    # Calculer la durée si pilulier ouvert
    duration_info = calculate_duration(user_id)
    
    # Dernière prise complète
    last_take = None
    if not duration_info:
        # Chercher la dernière prise complète aujourd'hui
        opens = PillboxEvent.query.filter(
            PillboxEvent.user_id == user_id,
            PillboxEvent.status == 'opened',
            db.func.date(PillboxEvent.timestamp) == today
        ).order_by(PillboxEvent.timestamp.desc()).all()
        
        for open_event in opens:
            close_event = PillboxEvent.query.filter(
                PillboxEvent.user_id == user_id,
                PillboxEvent.status == 'closed',
                PillboxEvent.timestamp > open_event.timestamp
            ).first()
            
            if close_event:
                duration = close_event.timestamp - open_event.timestamp
                minutes = int(duration.total_seconds() // 60)
                seconds = int(duration.total_seconds() % 60)
                last_take = {
                    'opened_at': open_event.timestamp.strftime('%H:%M'),
                    'duration_str': f"{minutes}min {seconds}s"
                }
                break
    
    # État actuel
    dernier_event = events[0] if events else None
    etat = dernier_event.status if dernier_event else 'closed'
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                  user=user, 
                                  events=events,
                                  ouvertures_jour=ouvertures_jour,
                                  dernier_event=dernier_event,
                                  etat=etat,
                                  duration_info=duration_info,
                                  last_take=last_take)'''

# Remplacer la route home
pattern = r"@app\.route\('\/'\).*?render_template_string\(DASHBOARD_TEMPLATE.*?\)"
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content[:match.start()] + new_home_route + content[match.end():]
    
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Route home mise à jour!")
