# �� Documentation Pillbox Monitor

## �� État actuel du projet

### Fonctionnalités implémentées
- ✅ Système multi-utilisateurs avec login/logout
- ✅ 3 utilisateurs : admin, marie, pierre
- ✅ Webhooks IFTTT avec format `opened_X` et `closed_X` (X = ID utilisateur)
- ✅ Interface moderne avec animations et logos SVG
- ✅ Page de supervision temps réel
- ✅ Historique des événements par utilisateur
- ✅ Profil utilisateur configurable

### Structure technique
- **Backend** : Flask + SQLAlchemy
- **Base de données** : SQLite (pillbox.db)
- **Frontend** : Bootstrap 5 + Font Awesome
- **Port** : 8000
- **Répertoire** : `/home/ec2-user/pillbox-app`

### Utilisateurs configurés

| Username | Password | Email | ID | Prises/jour | Webhooks |
|----------|----------|-------|-----|-------------|----------|
| admin | admin123 | admin@example.com | 1 | 2 | opened_1, closed_1 |
| marie | marie123 | marie.dupont@example.com | 2 | 3 | opened_2, closed_2 |
| pierre | pierre123 | p.lhoest@gmail.com | 3 | 1 | opened_3, closed_3 |

### Routes disponibles

| Route | Description | Authentification |
|-------|-------------|------------------|
| `/` | Redirige vers dashboard ou login | Auto |
| `/login` | Page de connexion | Non |
| `/logout` | Déconnexion | Oui |
| `/dashboard` | Tableau de bord utilisateur | Oui |
| `/profile` | Profil utilisateur | Oui |
| `/supervision` | Vue supervision globale | Non |
| `/webhook/pillbox` | Webhook IFTTT | Non |
| `/api/supervision` | API données supervision | Non |

### Configuration IFTTT

URL webhook : `http://51.44.12.162:8000/webhook/pillbox`

Format du body pour chaque utilisateur :
- Admin : `{"value": "opened_1"}` ou `{"value": "closed_1"}`
- Marie : `{"value": "opened_2"}` ou `{"value": "closed_2"}`
- Pierre : `{"value": "opened_3"}` ou `{"value": "closed_3"}`

## �� Installation depuis zéro

```bash
# 1. Cloner/Copier le projet
cd /home/ec2-user
cp -r backup_*/pillbox-app .

# 2. Activer l'environnement virtuel
cd pillbox-app
source venv/bin/activate

# 3. Installer les dépendances (si nécessaire)
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

## �� Problèmes connus

1. **Événements n'apparaissent pas dans le dashboard**
   - Les webhooks fonctionnent (visible en supervision)
   - Mais pas affichés sur la page personnelle
   - Debug nécessaire dans la route `/dashboard`

2. **Navigation à améliorer**
   - Boutons Homepage/Supervision pas cohérents
   - Manque un menu unifié

## �� Préférences pour l'assistant IA

### TOUJOURS utiliser la méthode EOF pour créer des fichiers :
```bash
cat > fichier.py << 'EOF'
contenu du fichier
