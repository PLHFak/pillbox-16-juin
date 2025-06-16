#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

with open('app.py', 'r') as f:
    content = f.read()

# Remplacer toute la section de la barre
old_bar_section = '''<div class="prise-bar {% if ouvertures_jour > 0 %}taken{% else %}not-taken{% endif %}">
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

new_bar_section = '''{% if duration_info %}
                {% if duration_info.status == 'opened' %}
                <!-- Pilulier ouvert - Rouge avec timer -->
                <div class="prise-bar opened" style="background: linear-gradient(135deg, #dc3545 0%, #ff6b6b 100%);">
                    <div class="prise-content">
                        <div class="prise-icon">
                            <i class="fas fa-pills"></i>
                        </div>
                        <div style="flex-grow: 1;">
                            <div style="font-size: 22px; font-weight: bold;">PILULIER OUVERT</div>
                            <div style="font-size: 16px;">Depuis {{ duration_info.opened_at }}</div>
                        </div>
                        <div style="font-size: 28px; font-weight: bold;" id="timer">
                            <i class="fas fa-clock"></i> <span id="timer-display">0:00</span>
                        </div>
                    </div>
                </div>
                <script>
                    // Timer en temps reel
                    function updateTimer() {
                        const openTime = new Date('{{ duration_info.opened_timestamp }}');
                        const now = new Date();
                        const diff = Math.floor((now - openTime) / 1000);
                        const minutes = Math.floor(diff / 60);
                        const seconds = diff % 60;
                        document.getElementById('timer-display').textContent = 
                            minutes + ':' + seconds.toString().padStart(2, '0');
                    }
                    updateTimer();
                    setInterval(updateTimer, 1000);
                </script>
                {% else %}
                <!-- Pilulier ferme - Vert avec duree -->
                <div class="prise-bar closed" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                    <div class="prise-content">
                        <div class="prise-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div style="flex-grow: 1;">
                            <div style="font-size: 22px; font-weight: bold;">PRISE TERMINÉE</div>
                            <div style="font-size: 16px;">{{ duration_info.opened_at }} - {{ duration_info.closed_at }}</div>
                        </div>
                        <div style="font-size: 28px; font-weight: bold;">
                            <i class="fas fa-stopwatch"></i> {{ duration_info.duration_str }}
                        </div>
                    </div>
                </div>
                {% endif %}
            {% else %}
                <!-- Pas de prise aujourd'hui - Gris -->
                <div class="prise-bar not-taken" style="background: linear-gradient(135deg, #6c757d 0%, #adb5bd 100%);">
                    <div class="prise-content">
                        <div class="prise-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div>
                            <div style="font-size: 22px; font-weight: bold;">EN ATTENTE</div>
                            <div style="font-size: 16px;">Aucune prise aujourd'hui</div>
                        </div>
                    </div>
                </div>
            {% endif %}'''

if old_bar_section in content:
    content = content.replace(old_bar_section, new_bar_section)
    print("✓ Barre unique avec timer ajoutee")

with open('app.py', 'w') as f:
    f.write(content)
