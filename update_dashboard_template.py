# Mettre à jour le template dashboard avec la nouvelle interface

import re

with open('app.py', 'r') as f:
    content = f.read()

# Nouveau template dashboard amélioré
new_dashboard = '''DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ user.nom_complet or user.username }} - Pillbox Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            color: white;
        }
        
        .main-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Barre de prise unique avec timing */
        .prise-bar-container {
            background: white;
            border-radius: 25px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        }
        
        .prise-bar {
            background: #e9ecef;
            border-radius: 30px;
            height: 100px;
            position: relative;
            overflow: hidden;
            transition: all 0.5s ease;
            cursor: pointer;
        }
        
        .prise-bar.opened {
            background: linear-gradient(135deg, #dc3545 0%, #ff6b6b 100%);
        }
        
        .prise-bar.closed {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        
        .prise-bar.not-taken {
            background: linear-gradient(135deg, #6c757d 0%, #adb5bd 100%);
        }
        
        .prise-content {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
            color: white;
        }
        
        .prise-left {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .prise-icon {
            font-size: 50px;
        }
        
        .prise-info {
            display: flex;
            flex-direction: column;
        }
        
        .prise-status {
            font-size: 22px;
            font-weight: bold;
        }
        
        .prise-time {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .prise-duration {
            font-size: 28px;
            font-weight: bold;
        }
        
        /* Multi-prises sur une ligne */
        .multi-prises {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .prise-card {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .prise-card.done {
            background: rgba(40, 167, 69, 0.3);
        }
        
        .prise-card.pending {
            background: rgba(255, 193, 7, 0.3);
        }
        
        .prise-card.missed {
            background: rgba(220, 53, 69, 0.3);
        }
        
        .reminder-icon {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 20px;
            color: #ffc107;
        }
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="main-container">
        <h3 class="text-center mb-4">
            <i class="fas fa-pills"></i> Moniteur de Pilulier
        </h3>
        
        <!-- Info utilisateur -->
        <div class="text-center mb-4">
            <h4>{{ user.nom_complet or user.username }}</h4>
            <small>{{ user.nb_prises_jour }} prise{{ 's' if user.nb_prises_jour > 1 else '' }}/jour</small>
        </div>

        <!-- Barre de prise unique avec timing -->
        {% if duration_info %}
        <div class="prise-bar-container">
            <h5 class="text-center text-dark mb-3">Prise en cours</h5>
            <div class="prise-bar opened">
                <div class="prise-content">
                    <div class="prise-left">
                        <div class="prise-icon">
                            <i class="fas fa-pills"></i>
                        </div>
                        <div class="prise-info">
                            <div class="prise-status">OUVERT</div>
                            <div class="prise-time">Depuis {{ duration_info.opened_at }}</div>
                        </div>
                    </div>
                    <div class="prise-duration">
                        {{ duration_info.duration_str }}
                    </div>
                </div>
            </div>
        </div>
        {% elif last_take %}
        <div class="prise-bar-container">
            <h5 class="text-center text-dark mb-3">Dernière prise</h5>
            <div class="prise-bar closed">
                <div class="prise-content">
                    <div class="prise-left">
                        <div class="prise-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="prise-info">
                            <div class="prise-status">TERMINÉ</div>
                            <div class="prise-time">{{ last_take.opened_at }} - Durée: {{ last_take.duration_str }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% else %}
        <div class="prise-bar-container">
            <h5 class="text-center text-dark mb-3">État actuel</h5>
            <div class="prise-bar not-taken">
                <div class="prise-content">
                    <div class="prise-left">
                        <div class="prise-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="prise-info">
                            <div class="prise-status">EN ATTENTE</div>
                            <div class="prise-time">Aucune prise aujourd'hui</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Multi-prises si > 1 prise/jour -->
        {% if user.nb_prises_jour > 1 %}
        <div class="multi-prises">
            {% for i in range(user.nb_prises_jour) %}
            <div class="prise-card {% if i < ouvertures_jour %}done{% elif i == ouvertures_jour %}pending{% else %}missed{% endif %}">
                <i class="fas fa-pills fa-2x mb-2"></i>
                <div>Prise {{ i + 1 }}</div>
                {% if i < ouvertures_jour %}
                    <small><i class="fas fa-check"></i> Fait</small>
                {% endif %}
                {% if false %}  <!-- À implémenter : si rappel envoyé -->
                    <i class="fas fa-bell reminder-icon"></i>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Historique -->
        <div class="history-container" style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px;">
            <h5 class="mb-3"><i class="fas fa-history"></i> Historique</h5>
            {% if events %}
                {% for event in events[:5] %}
                    <div class="history-item" style="display: flex; align-items: center; gap: 15px; padding: 12px; margin-bottom: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 12px;">
                        <i class="fas fa-{{ 'box-open' if event.status == 'opened' else 'check-circle' }} fa-lg"></i>
                        <div class="flex-grow-1">
                            <strong>{{ 'Ouvert' if event.status == 'opened' else 'Fermé' }}</strong><br>
                            <small>{{ event.timestamp.strftime('%d/%m à %H:%M') }}</small>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p class="text-center opacity-50">Aucun événement</p>
            {% endif %}
        </div>
    </div>

    <!-- Boutons flottants -->
    <div class="floating-buttons" style="position: fixed; bottom: 20px; right: 20px; display: flex; flex-direction: column; gap: 10px;">
        <a href="/profile" class="btn-float" style="width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); color: white; text-decoration: none;">
            <i class="fas fa-user"></i>
        </a>
        {% if session.get('is_admin') %}
        <a href="/supervision" class="btn-float" style="width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); color: white; text-decoration: none;">
            <i class="fas fa-chart-line"></i>
        </a>
        {% endif %}
        <a href="/logout" class="btn-float" style="width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); color: white; text-decoration: none;">
            <i class="fas fa-sign-out-alt"></i>
        </a>
    </div>
</body>
</html>
"""'''

# Remplacer le template dashboard
pattern = r'DASHBOARD_TEMPLATE = """.*?"""'
content = re.sub(pattern, new_dashboard, content, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Template dashboard mis à jour!")
