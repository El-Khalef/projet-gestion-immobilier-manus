#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle Transaction pour la gestion des transactions immobilières.
Ce fichier définit la structure des tables liées aux transactions (ventes et locations).
"""

from datetime import datetime
from app import db

class Transaction(db.Model):
    """
    Modèle représentant une transaction immobilière (vente ou location).
    
    Attributs:
        id (int): Identifiant unique de la transaction
        transaction_type (str): Type de transaction ('sale', 'rental')
        property_id (int): ID du bien immobilier concerné
        client_id (int): ID du client impliqué
        transaction_date (date): Date de la transaction
        amount (float): Montant de la transaction
        commission_amount (float): Montant de la commission
        commission_percentage (float): Pourcentage de la commission
        status (str): Statut de la transaction ('pending', 'completed', 'cancelled')
        payment_method (str): Méthode de paiement
        notes (str): Notes diverses sur la transaction
        created_at (datetime): Date de création de l'enregistrement
        updated_at (datetime): Date de dernière mise à jour de l'enregistrement
        handled_by (int): ID de l'utilisateur ayant géré la transaction
    """
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'sale', 'rental'
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    commission_amount = db.Column(db.Numeric(10, 2))
    commission_percentage = db.Column(db.Numeric(5, 2))
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'completed', 'cancelled'
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    handled_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relations
    rental_agreement = db.relationship('RentalAgreement', backref='transaction', lazy=True, uselist=False, cascade='all, delete-orphan')
    financial_transactions = db.relationship('FinancialTransaction', backref='transaction', lazy='dynamic')
    
    def get_formatted_amount(self):
        """
        Retourne le montant formaté de la transaction.
        
        Returns:
            str: Montant formaté avec devise
        """
        return f"{self.amount:,.2f} €"
    
    def get_commission_info(self):
        """
        Retourne les informations sur la commission.
        
        Returns:
            str: Informations sur la commission
        """
        if self.commission_amount and self.commission_percentage:
            return f"{self.commission_amount:,.2f} € ({self.commission_percentage}%)"
        elif self.commission_amount:
            return f"{self.commission_amount:,.2f} €"
        elif self.commission_percentage:
            return f"{self.commission_percentage}%"
        return "Aucune commission"
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet Transaction.
        
        Returns:
            str: Représentation de la transaction
        """
        return f'<Transaction {self.id}: {self.transaction_type.capitalize()} of Property {self.property_id}>'


class RentalAgreement(db.Model):
    """
    Modèle représentant un contrat de location.
    
    Attributs:
        id (int): Identifiant unique du contrat
        transaction_id (int): ID de la transaction associée
        start_date (date): Date de début du contrat
        end_date (date): Date de fin du contrat
        is_renewable (bool): Indique si le contrat est renouvelable
        rent_amount (float): Montant du loyer
        rent_frequency (str): Fréquence de paiement du loyer ('monthly', 'quarterly', 'yearly')
        deposit_amount (float): Montant du dépôt de garantie
        payment_day (int): Jour du mois où le loyer est dû
        special_conditions (str): Conditions spéciales du contrat
        created_at (datetime): Date de création de l'enregistrement
        updated_at (datetime): Date de dernière mise à jour de l'enregistrement
    """
    __tablename__ = 'rental_agreements'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_renewable = db.Column(db.Boolean, default=True)
    rent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    rent_frequency = db.Column(db.String(20), nullable=False)  # 'monthly', 'quarterly', 'yearly'
    deposit_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_day = db.Column(db.Integer, nullable=False)  # jour du mois
    special_conditions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_duration_months(self):
        """
        Calcule la durée du contrat en mois.
        
        Returns:
            int: Durée du contrat en mois
        """
        delta = self.end_date - self.start_date
        return round(delta.days / 30)
    
    def get_formatted_rent(self):
        """
        Retourne le loyer formaté avec sa fréquence.
        
        Returns:
            str: Loyer formaté
        """
        frequency_map = {
            'monthly': 'par mois',
            'quarterly': 'par trimestre',
            'yearly': 'par an'
        }
        frequency_str = frequency_map.get(self.rent_frequency, self.rent_frequency)
        return f"{self.rent_amount:,.2f} € {frequency_str}"
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet RentalAgreement.
        
        Returns:
            str: Représentation du contrat de location
        """
        return f'<RentalAgreement {self.id}: Transaction {self.transaction_id}, {self.start_date} to {self.end_date}>'
