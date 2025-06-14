#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les documents des biens immobiliers.
"""

from datetime import datetime
from app import db

class PropertyDocument(db.Model):
    """Modèle représentant un document associé à un bien immobilier."""
    
    __tablename__ = 'property_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # Taille en octets
    file_type = db.Column(db.String(50))  # Type MIME
    document_type = db.Column(db.String(50))  # deed, contract, certificate, etc.
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)  # Visible par les clients
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    property = db.relationship('Property', back_populates='documents')
    
    def __repr__(self):
        """Représentation textuelle de l'objet."""
        return f'<PropertyDocument {self.id}: {self.filename}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'document_type': self.document_type,
            'title': self.title,
            'description': self.description,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def url(self):
        """Retourne l'URL du document."""
        return f"/static/uploads/{self.file_path}"
