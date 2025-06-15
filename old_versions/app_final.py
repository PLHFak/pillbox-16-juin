from flask import Flask, request, jsonify, render_template_string, redirect, url_for
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
                # TODO: Envoyer notification et SMS
        
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
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        .status { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; }
        .online { color: #4CAF50; font-size: 24px; }
        .schedule { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .events { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .event { padding: 10px; margin: 5px 0; border-left: 4px solid #ddd; background: #fafafa; }
        .opened { border-color: #4CAF50; background: #e8f5e9; }
        .closed { border-color: #f44336; background: #ffebee; }
        .config-button { display: inline-block; background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
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
        html += "<p>Aucun evenement enregistre dans la base.</p>"
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
    <center>
        <a href="/config" class="config-button">Configurer les horaires</a>
    </center>
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

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        phone = request.form.get('phone')
        
        # Mettre à jour la base de données
        conn = get_db()
        cursor = conn.cursor()
        
        # Mettre à jour l'utilisateur
        cursor.execute("UPDATE users SET phone = ? WHERE id = 1", (phone,))
        
        # Mettre à jour l'horaire
        cursor.execute("""
            UPDATE medication_schedules 
            SET start_time = ?, end_time = ? 
            WHERE id = 1
        """, (start_time, end_time))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))
    
    # Récupérer les données actuelles
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = 1")
    user = cursor.fetchone()
    
    cursor.execute("SELECT * FROM medication_schedules WHERE id = 1")
    schedule = cursor.fetchone()
    
    conn.close()
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Configuration - Moniteur de Pilulier</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        .form-container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        input[type="time"] { font-size: 16px; }
        .submit-btn { background: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; }
        .submit-btn:hover { background: #45a049; }
        .back-link { text-align: center; margin-top: 20px; }
        a { color: #2196F3; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Configuration du Pilulier</h1>
    
    <div class="form-container">
        <form method="POST">
            <div class="form-group">
                <label for="phone">Numero de telephone (pour SMS):</label>
                <input type="tel" id="phone" name="phone" value='""" + (user['phone'] if user else '') + """' placeholder="+33612345678" required>
            </div>
            
            <div class="form-group">
                <label for="start_time">Heure de debut de prise:</label>
                <input type="time" id="start_time" name="start_time" value='""" + (schedule['start_time'] if schedule else '08:00') + """' required>
            </div>
            
            <div class="form-group">
                <label for="end_time">Heure de fin de prise:</label>
                <input type="time" id="end_time" name="end_time" value='""" + (schedule['end_time'] if schedule else '09:00') + """' required>
            </div>
            
            <button type="submit" class="submit-btn">Enregistrer</button>
        </form>
    </div>
    
    <div class="back-link">
        <a href="/">Retour au moniteur</a>
    </div>
</body>
</html>"""
    
    return html

if __name__ == '__main__':
    # Lancer le thread de vérification
    checker_thread = threading.Thread(target=check_medication_taken)
    checker_thread.daemon = True
    checker_thread.start()
    
    print("\nDemarrage du Moniteur de Pilulier - Version Complete")
    print(f"URL publique: http://51.44.12.162:8000")
    print("Page de configuration: http://51.44.12.162:8000/config")
    app.run(host='0.0.0.0', port=8000, debug=True)
