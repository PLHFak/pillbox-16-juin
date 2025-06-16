import json

# Tester le parsing du webhook
test_data = {"value": "opened_3"}
value = test_data.get('value', 'unknown')

print(f"Value reçu: {value}")

if '_' in value:
    parts = value.split('_')
    status = parts[0]  
    user_id = int(parts[1]) if parts[1].isdigit() else 1
    print(f"Status: {status}, User ID: {user_id}")
else:
    print("Pas d'underscore trouvé!")
