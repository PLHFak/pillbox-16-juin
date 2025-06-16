# í ½í³¦ Documentation Pillbox Monitor

## í ½íº€ Ã‰tat actuel du projet

### FonctionnalitÃ©s implÃ©mentÃ©es
- âœ… SystÃ¨me multi-utilisateurs avec login/logout
- âœ… 3 utilisateurs : admin, marie, pierre
- âœ… Webhooks IFTTT avec format `opened_X` et `closed_X` (X = ID utilisateur)
- âœ… Interface moderne avec animations et logos SVG
- âœ… Page de supervision temps rÃ©el
- âœ… Historique des Ã©vÃ©nements par utilisateur
- âœ… Profil utilisateur configurable

### Structure technique
- **Backend** : Flask + SQLAlchemy
- **Base de donnÃ©es** : SQLite (pillbox.db)
- **Frontend** : Bootstrap 5 + Font Awesome
- **Port** : 8000
- **RÃ©pertoire** : `/home/ec2-user/pillbox-app`

### Utilisateurs configurÃ©s

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
| `/logout` | DÃ©connexion | Oui |
| `/dashboard` | Tableau de bord utilisateur | Oui |
| `/profile` | Profil utilisateur | Oui |
| `/supervision` | Vue supervision globale | Non |
| `/webhook/pillbox` | Webhook IFTTT | Non |
| `/api/supervision` | API donnÃ©es supervision | Non |

### Configuration IFTTT

URL webhook : `http://51.44.12.162:8000/webhook/pillbox`

Format du body pour chaque utilisateur :
- Admin : `{"value": "opened_1"}` ou `{"value": "closed_1"}`
- Marie : `{"value": "opened_2"}` ou `{"value": "closed_2"}`
- Pierre : `{"value": "opened_3"}` ou `{"value": "closed_3"}`

## í ½í´§ Installation depuis zÃ©ro

```bash
# 1. Cloner/Copier le projet
cd /home/ec2-user
cp -r backup_*/pillbox-app .

# 2. Activer l'environnement virtuel
cd pillbox-app
source venv/bin/activate

# 3. Installer les dÃ©pendances (si nÃ©cessaire)
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

## í ½í°› ProblÃ¨mes connus

1. **Ã‰vÃ©nements n'apparaissent pas dans le dashboard**
   - Les webhooks fonctionnent (visible en supervision)
   - Mais pas affichÃ©s sur la page personnelle
   - Debug nÃ©cessaire dans la route `/dashboard`

2. **Navigation Ã  amÃ©liorer**
   - Boutons Homepage/Supervision pas cohÃ©rents
   - Manque un menu unifiÃ©

## í ½í³ PrÃ©fÃ©rences pour l'assistant IA

### TOUJOURS utiliser la mÃ©thode EOF pour crÃ©er des fichiers :
```bash
cat > fichier.py << 'EOF'
contenu du fichier
