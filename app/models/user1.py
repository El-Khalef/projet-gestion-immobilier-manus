#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle User pour la gestion des utilisateurs de l'application.
Ce fichier définit la structure de la table des utilisateurs et ses méthodes associées.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(UserMixin, db.Model):
    """
    Modèle représentant un utilisateur de l'application.
    
    Attributs:
        id (int): Identifiant unique de l'utilisateur
        username (str): Nom d'utilisateur unique
        email (str): Adresse email unique
        password_hash (str): Hash du mot de passe
        first_name (str): Prénom de l'utilisateur
        last_name (str): Nom de famille de l'utilisateur
        role (str): Rôle de l'utilisateur (admin, agent, manager, etc.)
        is_active (bool): Indique si le compte est actif
        created_at (datetime): Date de création du compte
        updated_at (datetime): Date de dernière mise à jour du compte
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    properties_created = db.relationship('Property', backref='creator', lazy='dynamic',
                                        foreign_keys='Property.created_by')
    clients_assigned = db.relationship('Client', backref='assigned_agent', lazy='dynamic',
                                      foreign_keys='Client.assigned_agent_id')
    transactions_handled = db.relationship('Transaction', backref='handler', lazy='dynamic',
                                          foreign_keys='Transaction.handled_by')
    maintenance_assigned = db.relationship('MaintenanceRequest', backref='assignee', lazy='dynamic',
                                          foreign_keys='MaintenanceRequest.assigned_to')
    
    @property
    def password(self):
        """
        Empêche l'accès direct au mot de passe.
        
        Raises:
            AttributeError: Si on tente d'accéder au mot de passe
        """
        raise AttributeError('Le mot de passe n\'est pas un attribut lisible')
    
    @password.setter
    def password(self, password):
        """
        Définit le hash du mot de passe.
        
        Args:
            password (str): Mot de passe en clair
        """
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash stocké.
        
        Args:
            password (str): Mot de passe à vérifier
            
        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """
        Retourne le nom complet de l'utilisateur.
        
        Returns:
            str: Nom complet de l'utilisateur
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet User.
        
        Returns:
            str: Représentation de l'utilisateur
        """
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    """
    Fonction requise par Flask-Login pour charger un utilisateur.
    
    Args:
        user_id (str): ID de l'utilisateur à charger
        
    Returns:
        User: L'objet utilisateur correspondant à l'ID, ou None si non trouvé
    """
    return User.query.get(int(user_id))
