from app import app, db, User

print("Test de création de base...")
with app.app_context():
    # Supprimer et recréer
    db.drop_all()
    db.create_all()
    print("Base créée avec succès!")
    
    # Vérifier les colonnes
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = inspector.get_columns('user')
    print("\nColonnes de la table user:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
