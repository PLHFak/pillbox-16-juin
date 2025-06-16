#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

print("Modification de la barre de prise...")

# Lire app.py
with open('app.py', 'r') as f:
    content = f.read()

# Trouver et modifier la section de la barre de prise dans le DASHBOARD_TEMPLATE
# Chercher la partie avec prise-bar-container
old_bar = r'''<div class="prise-bar {% if ouvertures_jour > 0 %}taken{% else %}not-taken{% endif %}">
                <div class="prise-content">
                    <div class="prise-icon">
                        {% if ouvertures_jour > 0 %}
                            <i class="fas fa-pills"></i>
                        {% else %}
                            <i class="fas fa-box"></i>
                        {% endif %}
                    </div>
                    <div>
                        {% if ouvertures_jour > 0 %}
                            PRISE EFFECTUÉE
                        {% else %}
                            NON PRISE
                        {% endif %}
                    </div>
                </div>
            </div>'''

new_bar = r'''<div class="prise-bar {% if etat == 'opened' %}opened{% elif ouvertures_jour > 0 %}closed{% else %}not-taken{% endif %}">
                <div class="prise-content">
                    <div class="prise-icon">
                        {% if etat == 'opened' %}
                            <i class="fas fa-pills"></i>
                        {% elif ouvertures_jour > 0 %}
                            <i class="fas fa-check-circle"></i>
                        {% else %}
                            <i class="fas fa-clock"></i>
                        {% endif %}
                    </div>
                    <div>
                        {% if etat == 'opened' %}
                            <div style="font-size: 20px; font-weight: bold;">PILULIER OUVERT</div>
                            <div style="font-size: 16px;">Fermez après la prise</div>
                        {% elif ouvertures_jour > 0 %}
                            <div style="font-size: 20px; font-weight: bold;">PRISE EFFECTUÉE</div>
                            <div style="font-size: 16px;">{{ ouvertures_jour }}/{{ user.nb_prises_jour }} aujourd'hui</div>
                        {% else %}
                            <div style="font-size: 20px; font-weight: bold;">EN ATTENTE</div>
                            <div style="font-size: 16px;">Aucune prise aujourd'hui</div>
                        {% endif %}
                    </div>
                </div>
            </div>'''

# Ajouter aussi les styles pour les couleurs
old_styles = r'''.prise-bar.taken {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        
        .prise-bar.not-taken {
            background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
        }'''

new_styles = r'''.prise-bar.opened {
            background: linear-gradient(135deg, #dc3545 0%, #ff6b6b 100%);
            animation: pulse 2s ease-in-out infinite;
        }
        
        .prise-bar.closed {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        
        .prise-bar.not-taken {
            background: linear-gradient(135deg, #6c757d 0%, #adb5bd 100%);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }'''

# Remplacer
if old_bar in content:
    content = content.replace(old_bar, new_bar)
    print("✓ Barre de prise modifiée")
else:
    print("✗ Barre de prise non trouvée")

if old_styles in content:
    content = content.replace(old_styles, new_styles)
    print("✓ Styles modifiés")
else:
    print("✗ Styles non trouvés")

# Sauvegarder
with open('app.py', 'w') as f:
    f.write(content)

print("\nModifications terminées!")
