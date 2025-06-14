#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les activités du système (journal d'activité).
"""

from datetime import datetime
from app import db

class Activity(db.Model):
    """Modèle représentant une activité ou un événement dans le système."""
    
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    activity_type = db.Column(db.String(50), nullable=False)  # login, property_create, client_update, etc.
    description = db.Column(db.Text, nullable=False)
    entity_type = db.Column(db.String(50), nullable=True)  # property, client, owner, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
    
    def __repr__(self):
        """Représentation textuelle de l'objet."""
        return f'<Activity {self.id}: {self.activity_type} by user {self.user_id}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def log(cls, user_id, activity_type, description, entity_type=None, entity_id=None, 
            ip_address=None, user_agent=None):
        """
        Crée une nouvelle entrée d'activité dans le journal.
        
        Args:
            user_id (int): ID de l'utilisateur qui a effectué l'action
            activity_type (str): Type d'activité (login, property_create, etc.)
            description (str): Description de l'activité
            entity_type (str, optional): Type d'entité concernée
            entity_id (int, optional): ID de l'entité concernée
            ip_address (str, optional): Adresse IP de l'utilisateur
            user_agent (str, optional): User-Agent du navigateur
            
        Returns:
            Activity: L'objet Activity créé
        """
        activity = cls(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(activity)
        db.session.commit()
        return activity
