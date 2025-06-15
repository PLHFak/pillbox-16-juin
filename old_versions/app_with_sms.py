from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import datetime
import json
import sqlite3
import threading
import time
import boto3
import os

app = Flask(__name__)

# Client AWS SNS pour les SMS
sns_client = boto3.client('sns', region_name='eu-west-3')

def send_sms(phone_number, message):
    """Envoie un SMS via AWS SNS"""
    try:
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'PILLBOX'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        print(f"SMS envoye a {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"Erreur envoi SMS: {e}")
        return False

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

# Dictionnaire pour tracker les alertes envoyées
alerts_sent = {}

def check_medication_taken():
    """Vérifie si le médicament a été pris dans la plage horaire"""
    while True:
        time.sleep(60)  # Vérifier chaque minute
        
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime('%H:%M')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Chercher les horaires actifs
        cursor.execute('''
            SELECT ms.*, u.phone, u.name 
            FROM medication_schedules ms 
            JOIN users u ON ms.user_id = u.id 
            WHERE ms.start_time <= ? AND ms.end_time <= ?
        ''', (current_time_str, current_time_str))
        
        schedules = cursor.fetchall()
        
        for schedule in schedules:
            schedule_id = schedule['id']
            end_time = datetime.datetime.strptime(schedule['end_time'], '%H:%M').time()
            current_time_only = current_time.time()
            
            # Vérifier si on a dépassé l'heure de fin
            if current_time_only > end_time:
                # Calculer depuis combien de temps on a dépassé
                end_datetime = current_time.replace(
                    hour=end_time.hour,
                    minute=end_time.minute,
                    second=0
                )
                minutes_passed = int((current_time - end_datetime).total_seconds() / 60)
                
                # Vérifier si le pilulier a été ouvert pendant la période
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
                ''', (start_datetime, end_datetime))
                
                result = cursor.fetchone()
                
                if result['count'] == 0:
                    # Médicament non pris
                    alert_key = f"{schedule_id}_{current_time.date()}"
                    
                    # Notification après 1 minute
                    if minutes_passed >= schedule['notification_delay'] and not alerts_sent.get(f"{alert_key}_notif"):
                        print(f"ALERTE NOTIFICATION: Medicament non pris depuis {minutes_passed} minutes!")
                        alerts_sent[f"{alert_key}_notif"] = True
                    
                    # SMS après le délai configuré (par défaut 5 minutes)
                    if minutes_passed >= schedule['sms_delay'] and not alerts_sent.get(f"{alert_key}_sms"):
                        message = f"Rappel: Vous n'avez pas pris vos medicaments. (Retard: {minutes_passed} min)"
                        if send_sms(schedule['phone'], message):
                            alerts_sent[f"{alert_key}_sms"] = True
                            print(f"SMS envoye a {schedule['phone']}")
        
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
        .alert { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
    <meta http-equiv="refresh" content="10">
</head>
<body>
    <h1>Moniteur de Pilulier</h1>
    <div class="status">
        <p class="online">Systeme en ligne - SMS actifs</p>
        <p>Derniere mise a jour : """ + datetime.datetime.now().strftime('%H:%M:%S') + """</p>
    """
    
    if schedule:
        html += f"""
        <div class="schedule">
            <strong>Plage horaire actuelle:</strong> {schedule['start_time']} - {schedule['end_time']}
            <br><small>SMS apres {schedule['sms_delay']} minutes de retard</small>
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
        <a href="/test-sms" class="config-button" style="background: #ff9800;">Tester SMS</a>
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
        
        # Si on ouvre le pilulier, réinitialiser les alertes du jour
        if status == 'opened':
            today = datetime.datetime.now().date()
            for key in list(alerts_sent.keys()):
                if str(today) in key:
                    del alerts_sent[key]
        
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
        sms_delay = int(request.form.get('sms_delay', 5))
        
        # Mettre à jour la base de données
        conn = get_db()
        cursor = conn.cursor()
        
        # Mettre à jour l'utilisateur
        cursor.execute("UPDATE users SET phone = ? WHERE id = 1", (phone,))
        
        # Mettre à jour l'horaire
        cursor.execute("""
            UPDATE medication_schedules 
            SET start_time = ?, end_time = ?, sms_delay = ?
            WHERE id = 1
        """, (start_time, end_time, sms_delay))
        
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
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
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
            
            <div class="form-group">
                <label for="sms_delay">Delai avant SMS (minutes apres la fin):</label>
                <select id="sms_delay" name="sms_delay">
                    <option value="1" """ + ('selected' if schedule and schedule['sms_delay'] == 1 else '') + """>1 minute</option>
                    <option value="5" """ + ('selected' if not schedule or schedule['sms_delay'] == 5 else '') + """>5 minutes</option>
                    <option value="10" """ + ('selected' if schedule and schedule['sms_delay'] == 10 else '') + """>10 minutes</option>
                    <option value="15" """ + ('selected' if schedule and schedule['sms_delay'] == 15 else '') + """>15 minutes</option>
                </select>
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

@app.route('/test-sms')
def test_sms():
    """Page pour tester l'envoi de SMS"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users WHERE id = 1")
    user = cursor.fetchone()
    conn.close()
    
    if user and user['phone']:
        success = send_sms(user['phone'], "Test SMS Pillbox: Ceci est un message de test.")
        if success:
            return "<h1>SMS de test envoye!</h1><p>Verifiez votre telephone.</p><p><a href='/'>Retour</a></p>"
        else:
            return "<h1>Erreur envoi SMS</h1><p>Verifiez vos credentials AWS.</p><p><a href='/'>Retour</a></p>"
    else:
        return "<h1>Erreur</h1><p>Configurez d'abord votre numero de telephone.</p><p><a href='/config'>Configurer</a></p>"

if __name__ == '__main__':
    # Lancer le thread de vérification
    checker_thread = threading.Thread(target=check_medication_taken)
    checker_thread.daemon = True
    checker_thread.start()
    
    print("\n" + "="*50)
    print("MONITEUR DE PILULIER - VERSION SMS")
    print("="*50)
    print(f"URL publique: http://51.44.12.162:8000")
    print("Page de configuration: http://51.44.12.162:8000/config")
    print("Test SMS: http://51.44.12.162:8000/test-sms")
    print("SMS actifs avec AWS SNS")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
