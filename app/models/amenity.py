#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les équipements des biens immobiliers.
"""

from datetime import datetime
from app import db

# Table d'association entre les biens immobiliers et les équipements
property_amenities = db.Table('property_amenities',
    db.Column('property_id', db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id', ondelete='CASCADE'), primary_key=True)
)

class Amenity(db.Model):
    """Modèle représentant un équipement ou une caractéristique d'un bien immobilier."""
    
    __tablename__ = 'amenities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50))  # interior, exterior, security, etc.
    icon = db.Column(db.String(50))  # Classe d'icône (FontAwesome, etc.)
    description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    properties = db.relationship('Property', secondary=property_amenities, back_populates='amenities')
    
    def __repr__(self):
        """Représentation textuelle de l'objet."""
        return f'<Amenity {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'icon': self.icon,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
