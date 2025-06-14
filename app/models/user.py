#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les utilisateurs de l'application.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """Modèle représentant un utilisateur de l'application."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(20), default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    property_visits = db.relationship('PropertyVisit', back_populates='user')
    
    def __repr__(self):
        """Représentation textuelle de l'objet."""
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Définit le mot de passe hashé de l'utilisateur."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def is_admin(self):
        """Vérifie si l'utilisateur est un administrateur."""
        return self.role == 'admin'
    
    @property
    def full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


@login_manager.user_loader
def load_user(user_id):
    """Fonction requise par Flask-Login pour charger un utilisateur."""
    return User.query.get(int(user_id))
