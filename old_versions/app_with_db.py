from flask import Flask, request, jsonify, render_template_string
import datetime
import json
import sqlite3
import threading
import time

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('pillbox.db')
    conn.row_factory = sqlite3.Row
    return conn

def save_event(status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pillbox_events (timestamp, status) VALUES (?, ?)",
        (datetime.datetime.now(), status)
    )
    conn.commit()
    conn.close()

def get_recent_events(limit=15):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM pillbox_events ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    events = cursor.fetchall()
    conn.close()
    return events

def get_current_schedule():
    conn = get_db()
    cursor = conn.cursor()
    current_time = datetime.datetime.now().strftime('%H:%M')
    cursor.execute(
        "SELECT * FROM medication_schedules WHERE start_time <= ? AND end_time >= ?",
        (current_time, current_time)
    )
    schedule = cursor.fetchone()
    conn.close()
    return schedule

def check_medication_taken():
    """Vérifie si le médicament a été pris dans la plage horaire"""
    while True:
        time.sleep(60)  # Vérifier chaque minute
        
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime('%H:%M')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Chercher les horaires qui viennent de se terminer
        cursor.execute('''
            SELECT ms.*, u.phone, u.name 
            FROM medication_schedules ms 
            JOIN users u ON ms.user_id = u.id 
            WHERE ms.end_time = ?
        ''', (current_time_str,))
        
        schedule = cursor.fetchone()
        
        if schedule:
            # Vérifier si le pilulier a été ouvert pendant cette période
            start_datetime = current_time.replace(
                hour=int(schedule['start_time'].split(':')[0]),
                minute=int(schedule['start_time'].split(':')[1]),
                second=0
            )
            
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM pillbox_events 
                WHERE timestamp >= ? 
                AND timestamp <= ? 
                AND status = 'opened'
            ''', (start_datetime, current_time))
            
            result = cursor.fetchone()
            
            if result['count'] == 0:
                print(f"ALERTE: Médicament non pris pour {schedule['name']}!")
                # Ici on ajoutera les notifications et SMS
        
        conn.close()

@app.route('/')
def home():
    events = get_recent_events()
    schedule = get_current_schedule()
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Moniteur de Pilulier</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        .status { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; }
        .online { color: #4CAF50; font-size: 24px; }
        .schedule { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .events { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .event { padding: 10px; margin: 5px 0; border-left: 4px solid #ddd; background: #fafafa; }
        .opened { border-color: #4CAF50; background: #e8f5e9; }
        .closed { border-color: #f44336; background: #ffebee; }
    </style>
    <meta http-equiv="refresh" content="10">
</head>
<body>
    <h1>Moniteur de Pilulier</h1>
    <div class="status">
        <p class="online">Systeme en ligne</p>
        <p>Derniere mise a jour : """ + datetime.datetime.now().strftime('%H:%M:%S') + """</p>
    """
    
    if schedule:
        html += f"""
        <div class="schedule">
            <strong>Plage horaire actuelle:</strong> {schedule['start_time']} - {schedule['end_time']}
        </div>
        """
    
    html += """
    </div>
    <div class="events">
        <h2>Derniers evenements</h2>"""
    
    if not events:
        html += "<p>Aucun evenement enregistre.</p>"
    else:
        for event in events:
            timestamp = datetime.datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            time_str = timestamp.strftime('%H:%M:%S')
            if event['status'] == 'opened':
                html += f'<div class="event opened">[OUVERT] {time_str}</div>'
            elif event['status'] == 'closed':
                html += f'<div class="event closed">[FERME] {time_str}</div>'
            else:
                html += f'<div class="event">{time_str} - {event["status"]}</div>'
    
    html += """
    </div>
    <p style="text-align:center; margin-top:20px;">
        <a href="/config">Configurer les horaires</a>
    </p>
</body>
</html>"""
    
    return html

@app.route('/webhook/pillbox', methods=['POST'])
def pillbox_webhook():
    print("\n=== WEBHOOK RECU ===")
    
    try:
        data = request.get_json()
        print(f"Donnees recues: {data}")
        
        status = 'unknown'
        
        if 'description' in data:
            try:
                desc_data = json.loads(data['description'])
                status = desc_data.get('value', 'unknown')
            except:
                pass
        
        # Sauvegarder dans la base de données
        save_event(status)
        print(f"Status detecte et sauvegarde: {status}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        status = 'error'
    
    return jsonify({"success": True})

@app.route('/config')
def config():
    return """
    <h1>Configuration</h1>
    <p>Page de configuration en construction...</p>
    <p><a href="/">Retour</a></p>
    """

if __name__ == '__main__':
    # Lancer le thread de vérification
    checker_thread = threading.Thread(target=check_medication_taken)
    checker_thread.daemon = True
    checker_thread.start()
    
    print("\nDemarrage du Moniteur de Pilulier avec Base de Donnees")
    print(f"URL publique: http://51.44.12.162:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
