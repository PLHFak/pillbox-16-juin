import sqlite3
import datetime

def create_database():
    conn = sqlite3.connect('pillbox.db')
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    
    # Table des horaires de médication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medication_schedules (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            notification_delay INTEGER DEFAULT 1,
            sms_delay INTEGER DEFAULT 5,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Table des événements du pilulier
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pillbox_events (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            schedule_checked INTEGER DEFAULT 0
        )
    ''')
    
    # Insérer un utilisateur de test
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, name, phone) 
        VALUES (1, 'Test User', '+33612345678')
    ''')
    
    # Insérer un horaire de test (8h-9h)
    cursor.execute('''
        INSERT OR IGNORE INTO medication_schedules 
        (id, user_id, start_time, end_time, notification_delay, sms_delay) 
        VALUES (1, 1, '08:00', '09:00', 1, 5)
    ''')
    
    conn.commit()
    conn.close()
    print("Base de données créée avec succès!")

if __name__ == "__main__":
    create_database()
