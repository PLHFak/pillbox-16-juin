from flask import Flask, request, jsonify
import datetime
import json

app = Flask(__name__)
events = []

@app.route('/')
def home():
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    
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
        <p>Derniere mise a jour : """ + current_time + """</p>
    </div>
    <div class="events">
        <h2>Derniers evenements</h2>"""
    
    if not events:
        html += "<p>Aucun evenement enregistre.</p>"
    else:
        for event in reversed(events[-15:]):
            if "opened" in event:
                html += '<div class="event opened">[OUVERT] ' + event + '</div>'
            elif "closed" in event:
                html += '<div class="event closed">[FERME] ' + event + '</div>'
            else:
                html += '<div class="event">' + event + '</div>'
    
    html += """
    </div>
    <p style="text-align:center; color:#666; margin-top:20px;">Page actualisee toutes les 10 secondes</p>
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
        
        print(f"Status detecte: {status}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        status = 'error'
    
    event = f"{datetime.datetime.now().strftime('%H:%M:%S')} - Pilulier {status}"
    events.append(event)
    print(f"Evenement ajoute: {event}")
    
    return jsonify({"success": True})

if __name__ == '__main__':
    print("\nDemarrage du Moniteur de Pilulier")
    print(f"URL publique: http://51.44.12.162:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
