#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle pour les transactions financières.
"""

from datetime import datetime
from app import db

class FinancialTransaction(db.Model):
    """Modèle représentant une transaction financière."""
    
    __tablename__ = 'financial_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    
    transaction_type = db.Column(db.String(50), nullable=False)  # income, expense, deposit, withdrawal
    category = db.Column(db.String(50))  # rent, maintenance, tax, commission, etc.
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    transaction_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50))  # cash, bank_transfer, check, etc.
    reference_number = db.Column(db.String(100))  # Numéro de référence externe
    description = db.Column(db.Text)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))  # monthly, quarterly, yearly
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations - Correction des relations pour éviter les conflits
    property_rel = db.relationship('Property', backref=db.backref('financial_transactions', lazy='dynamic'))
    transaction_rel = db.relationship('Transaction', backref=db.backref('financial_transactions', lazy='dynamic'))
    owner_rel = db.relationship('Owner', backref=db.backref('financial_transactions', lazy='dynamic'))
    client_rel = db.relationship('Client', backref=db.backref('financial_transactions', lazy='dynamic'))
    
    def __repr__(self):
        """Représentation textuelle de l'objet."""
        return f'<FinancialTransaction {self.id}: {self.transaction_type} {self.amount} {self.currency}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'transaction_id': self.transaction_id,
            'owner_id': self.owner_id,
            'client_id': self.client_id,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'amount': self.amount,
            'currency': self.currency,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'description': self.description,
            'is_recurring': self.is_recurring,
            'recurring_frequency': self.recurring_frequency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def formatted_amount(self):
        """Retourne le montant formaté avec la devise."""
        if self.currency == 'EUR':
            return f"{self.amount:,.2f} €"
        elif self.currency == 'USD':
            return f"${self.amount:,.2f}"
        else:
            return f"{self.amount:,.2f} {self.currency}"
    
    @property
    def is_income(self):
        """Vérifie si la transaction est une entrée d'argent."""
        return self.transaction_type in ['income', 'deposit']
    
    @property
    def is_expense(self):
        """Vérifie si la transaction est une sortie d'argent."""
        return self.transaction_type in ['expense', 'withdrawal']
