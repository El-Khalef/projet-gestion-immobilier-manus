#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les contrats de location.
"""

from datetime import datetime
from app import db

class RentalAgreement(db.Model):
    """Modèle représentant un contrat de location."""
    
    __tablename__ = 'rental_agreements'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)  # Montant du loyer
    payment_frequency = db.Column(db.String(20), default='monthly')  # monthly, quarterly, yearly
    deposit_amount = db.Column(db.Float)  # Montant de la caution
    is_furnished = db.Column(db.Boolean, default=False)
    includes_utilities = db.Column(db.Boolean, default=False)
    special_conditions = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, terminated, expired
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    transaction = db.relationship('Transaction', back_populates='rental_agreement')
    
    def __repr__(self):
        """Représentation textuelle de l'objet."""
        return f'<RentalAgreement {self.id}: {self.start_date} to {self.end_date}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'rent_amount': self.rent_amount,
            'payment_frequency': self.payment_frequency,
            'deposit_amount': self.deposit_amount,
            'is_furnished': self.is_furnished,
            'includes_utilities': self.includes_utilities,
            'special_conditions': self.special_conditions,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def is_active(self):
        """Vérifie si le contrat est actif."""
        today = datetime.utcnow().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    @property
    def duration_months(self):
        """Calcule la durée du contrat en mois."""
        if not self.start_date or not self.end_date:
            return 0
        
        # Calcul de la différence en mois
        months = (self.end_date.year - self.start_date.year) * 12
        months += self.end_date.month - self.start_date.month
        
        # Ajustement pour les jours
        if self.end_date.day < self.start_date.day:
            months -= 1
            
        return months
