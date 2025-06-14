#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration de l'application Flask.
Ce fichier définit les différentes configurations pour les environnements
de développement, test et production.
"""

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    """Configuration de base commune à tous les environnements."""
    
    # Clé secrète pour la sécurité de l'application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-difficile-a-deviner'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/gestion_immobilier'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration du serveur de mail (à implémenter si nécessaire)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Configuration des uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    @staticmethod
    def init_app(app):
        """Initialisation de l'application avec cette configuration."""
        # Création du dossier d'uploads s'il n'existe pas
        os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/gestion_immobilier_dev'


class TestingConfig(Config):
    """Configuration pour l'environnement de test."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/gestion_immobilier_test'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/gestion_immobilier'
    
    @classmethod
    def init_app(cls, app):
        """Initialisation spécifique pour la production."""
        Config.init_app(app)
        
        # Gestion des logs en production
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Création du dossier de logs s'il n'existe pas
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        # Configuration du handler de logs
        file_handler = RotatingFileHandler('logs/gestion_immobilier.log',
                                          maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        
        # Ajout du handler à l'application
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Démarrage de l\'application Gestion Immobilière')


# Dictionnaire des configurations disponibles
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
