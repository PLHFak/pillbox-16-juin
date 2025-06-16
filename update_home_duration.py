#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

with open('app.py', 'r') as f:
    content = f.read()

# Trouver la route home et ajouter duration_info
old_home_end = '''return render_template_string(DASHBOARD_TEMPLATE, 
                                  user=user, 
                                  events=events,
                                  ouvertures_jour=ouvertures_jour,
                                  dernier_event=dernier_event,
                                  etat=etat)'''

new_home_end = '''# Calculer la duree
    duration_info = get_pillbox_duration(user_id)
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                  user=user, 
                                  events=events,
                                  ouvertures_jour=ouvertures_jour,
                                  dernier_event=dernier_event,
                                  etat=etat,
                                  duration_info=duration_info)'''

if old_home_end in content:
    content = content.replace(old_home_end, new_home_end)
    print("✓ Route home modifiee")

with open('app.py', 'w') as f:
    f.write(content)
