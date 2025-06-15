# Script pour remplacer la fonction dashboard

# Lire le fichier
with open('app.py', 'r') as f:
    lines = f.readlines()

# Nouvelle fonction dashboard
new_dashboard = '''def dashboard():
    events = PillboxEvent.query.filter_by(user_id=current_user.id).order_by(PillboxEvent.timestamp.desc()).limit(10).all()
    
    # Calculer les statistiques
    dernier_event = events[0] if events else None
    etat = 'closed' if not dernier_event else dernier_event.status
    
    # Compter les ouvertures du jour
    aujourdhui = datetime.date.today()
    nb_ouvertures = 0
    for e in events:
        if e.timestamp.date() == aujourdhui and e.status == 'opened':
            nb_ouvertures += 1
    
    # Date du jour
    date_jour = datetime.datetime.now().strftime('%A %d %B %Y')
    
    return render_template('dashboard.html',
        user=current_user,
        events=events,
        etat=etat,
        nb_ouvertures=nb_ouvertures,
        dernier_event=dernier_event,
        date_jour=date_jour
    )
'''

# Remplacer les lignes 65 à 74 (index 64 à 73)
new_lines = lines[:65] + [new_dashboard + '\n'] + lines[74:]

# Écrire le nouveau fichier
with open('app.py', 'w') as f:
    f.writelines(new_lines)

print("Dashboard remplacé avec succès!")
