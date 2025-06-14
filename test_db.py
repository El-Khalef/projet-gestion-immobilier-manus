#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test de connexion à la base de données.
Ce script vérifie que la connexion à PostgreSQL fonctionne correctement.
"""

from app import create_app, db

def test_database_connection():
    """Teste la connexion à la base de données."""
    app = create_app('development')
    with app.app_context():
        try:
            db.engine.connect()
            print("✅ Connexion à la base de données réussie !")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données : {e}")
            return False

if __name__ == '__main__':
    test_database_connection()
