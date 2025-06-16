#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

print("Ajout du calcul de duree...")

with open('app.py', 'r') as f:
    content = f.read()

# Ajouter la fonction de calcul après les imports
duration_func = '''
def get_pillbox_duration(user_id):
    """Calcule la duree depuis la derniere ouverture"""
    today = datetime.datetime.now().date()
    
    # Chercher la derniere ouverture
    last_open = PillboxEvent.query.filter(
        PillboxEvent.user_id == user_id,
        PillboxEvent.status == 'opened',
        db.func.date(PillboxEvent.timestamp) == today
    ).order_by(PillboxEvent.timestamp.desc()).first()
    
    if not last_open:
        return None
        
    # Chercher si ferme apres
    last_close = PillboxEvent.query.filter(
        PillboxEvent.user_id == user_id,
        PillboxEvent.status == 'closed',
        PillboxEvent.timestamp > last_open.timestamp
    ).first()
    
    if last_close:
        # Pilulier ferme - calculer la duree
        duration = last_close.timestamp - last_open.timestamp
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        return {
            'status': 'closed',
            'opened_at': last_open.timestamp.strftime('%H:%M'),
            'closed_at': last_close.timestamp.strftime('%H:%M'),
            'duration_min': minutes,
            'duration_sec': seconds,
            'duration_str': f"{minutes}min {seconds}s"
        }
    else:
        # Pilulier encore ouvert
        return {
            'status': 'opened',
            'opened_at': last_open.timestamp.strftime('%H:%M'),
            'opened_timestamp': last_open.timestamp.isoformat()
        }

'''

# Inserer apres les modeles
pos = content.find('# Decorateur pour verifier')
if pos > 0:
    content = content[:pos] + duration_func + '\n' + content[pos:]
    print("✓ Fonction de duree ajoutee")

with open('app.py', 'w') as f:
    f.write(content)
