import re

with open('app.py', 'r') as f:
    content = f.read()

# Ajouter route API supervision si pas présente
if '/api/supervision' not in content:
    api_route = '''
@app.route("/api/supervision")
def api_supervision():
    """API pour la page de supervision"""
    result = {}
    
    # Récupérer les événements par utilisateur
    users = User.query.all()
    for user in users:
        events = PillboxEvent.query.filter_by(user_id=user.id).order_by(
            PillboxEvent.timestamp.desc()
        ).limit(10).all()
        
        result[user.username] = [
            {
                'status': e.status,
                'time': e.timestamp.strftime('%H:%M')
            } for e in events
        ]
    
    return jsonify(result)
'''
    # Insérer avant if __name__
    pos = content.find('if __name__ == "__main__":')
    content = content[:pos] + api_route + '\n\n' + content[pos:]

# Corriger la route supervision
supervision_pattern = r'@app\.route\("/supervision"\).*?return render_template_string.*?\'\'\', users_data=users_data\)'
match = re.search(supervision_pattern, content, re.DOTALL)

if match:
    # Remplacer par une version simple
    new_supervision = '''@app.route("/supervision")
def supervision():
    """Page de supervision"""
    return render_template("supervision.html")'''
    
    content = content[:match.start()] + new_supervision + content[match.end():]

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Routes corrigées!")
