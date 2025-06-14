#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from app.config import Config

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
cors = CORS()

def create_app(config_class=Config):
    """Fonction factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    cors.init_app(app)

    # Configuration de Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'

    # Enregistrement des blueprints
    from app.routes.old_auth import auth_bp
    from app.routes.properties import properties_bp
    from app.routes.owners import owners_bp
    from app.routes.clients import clients_bp
    from app.routes.transactions import transactions_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(properties_bp, url_prefix='/api/properties')
    app.register_blueprint(owners_bp, url_prefix='/api/owners')
    app.register_blueprint(clients_bp, url_prefix='/api/clients')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(main_bp)  # Routes principales sans préfixe

    # Gestion des erreurs
    @app.errorhandler(404)
    def page_not_found(e):
        return {"error": "Page non trouvée"}, 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return {"error": "Erreur interne du serveur"}, 500

    # Création des tables si elles n'existent pas
    with app.app_context():
        db.create_all()

    return app
