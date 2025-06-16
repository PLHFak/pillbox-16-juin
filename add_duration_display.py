#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Ajout de l'affichage de duree...")

# Pour l'instant, affichons juste ce qu'on a
with open('app.py', 'r') as f:
    lines = f.readlines()
    
print(f"Fichier app.py : {len(lines)} lignes")

# Chercher où est le dashboard template
for i, line in enumerate(lines):
    if 'DASHBOARD_TEMPLATE' in line:
        print(f"Dashboard template trouve ligne {i+1}")
        break
        
print("Termine!")
