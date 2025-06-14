#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les visites de biens immobiliers.
"""

from datetime import datetime
from app import db

class PropertyVisit(db.Model):
    """Modèle représentant une visite de bien immobilier."""
    
    __tablename__ = 'property_visits'
    # Ajout de l'option extend_existing pour éviter l'erreur de double déclaration
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Agent responsable de la visite
    
    visit_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)  # Durée prévue en minutes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    feedback = db.Column(db.Text)  # Retour du client après la visite
    interest_level = db.Column(db.Integer)  # Niveau d'intérêt du client (1-5)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations - Correction des noms pour éviter les conflits
    property_rel = db.relationship('Property', back_populates='visits')
    client_rel = db.relationship('Client', back_populates='visits')
    user_rel = db.relationship('User', back_populates='property_visits')
    
    def __repr__(self):
        """Représentation textuelle de l'objet."""
        return f'<PropertyVisit {self.id}: {self.property_id} - {self.client_id} on {self.visit_date}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'notes': self.notes,
            'feedback': self.feedback,
            'interest_level': self.interest_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def is_past(self):
        """Vérifie si la visite est passée."""
        return self.visit_date < datetime.utcnow()
    
    @property
    def is_today(self):
        """Vérifie si la visite est aujourd'hui."""
        today = datetime.utcnow().date()
        return self.visit_date.date() == today
    
    @property
    def formatted_date(self):
        """Retourne la date formatée."""
        return self.visit_date.strftime('%d/%m/%Y %H:%M') if self.visit_date else ""
    
    @property
    def status_label(self):
        """Retourne le libellé du statut."""
        status_map = {
            'scheduled': 'Planifiée',
            'completed': 'Terminée',
            'cancelled': 'Annulée'
        }
        return status_map.get(self.status, self.status)
