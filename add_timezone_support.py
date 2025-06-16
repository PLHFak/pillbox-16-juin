import re

with open('app.py', 'r') as f:
    content = f.read()

# Ajouter l'import pytz
if 'import pytz' not in content:
    imports_pos = content.find('import datetime')
    content = content[:imports_pos] + 'import datetime\nimport pytz\n' + content[imports_pos + len('import datetime'):]

# Ajouter le champ timezone au modèle User
user_model_pattern = r'class User\(.*?\):(.*?)(?=\n\s*def\s+set_password|class)'
match = re.search(user_model_pattern, content, re.DOTALL)

if match and 'timezone' not in match.group(0):
    # Ajouter avant la dernière ligne du modèle
    insert_pos = match.end() - 10  # Juste avant la fin
    timezone_field = '\n    timezone = db.Column(db.String(50), default="Europe/Paris")  # Fuseau horaire'
    content = content[:insert_pos] + timezone_field + content[insert_pos:]

# Modifier la fonction dashboard pour utiliser le timezone
dashboard_func = '''@app.route("/dashboard")
@login_required
def dashboard():
    # Timezone de l'utilisateur
    user_tz = pytz.timezone(current_user.timezone or 'Europe/Paris')
    now_user = datetime.datetime.now(user_tz)
    today = now_user.date()
    
    # Événements du jour dans le timezone de l'utilisateur
    events_today = []
    all_events = PillboxEvent.query.filter_by(user_id=current_user.id).all()
    
    for event in all_events:
        # Convertir au timezone de l'utilisateur
        event_time = pytz.utc.localize(event.timestamp).astimezone(user_tz)
        if event_time.date() == today:
            events_today.append(event)
    
    # Compter les ouvertures du jour
    ouvertures_jour = sum(1 for e in events_today if e.status == 'opened')
    
    # Dernier statut
    last_event = PillboxEvent.query.filter_by(
        user_id=current_user.id
    ).order_by(PillboxEvent.timestamp.desc()).first()
    
    current_status = last_event.status if last_event else 'unknown'
    
    # 10 derniers événements
    recent_events = PillboxEvent.query.filter_by(
        user_id=current_user.id
    ).order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    
    # Convertir les timestamps pour l'affichage
    for event in recent_events:
        event.timestamp_local = pytz.utc.localize(event.timestamp).astimezone(user_tz)
    
    return render_template('better_single_bar.html',
        user=current_user,
        etat=current_status,
        ouvertures_jour=ouvertures_jour,
        events=recent_events,
        dernier_event=last_event,
        date_jour=now_user
    )'''

# Remplacer la fonction dashboard
pattern = r'@app\.route\("/dashboard"\).*?(?=@app\.route|if __name__|$)'
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content[:match.start()] + dashboard_func + '\n\n' + content[match.end():]

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Support timezone ajouté!")
