#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèles pour la gestion financière et la maintenance.
Ce fichier définit les structures des tables liées aux transactions financières et aux demandes de maintenance.
"""

from datetime import datetime
from app import db

class FinancialTransaction(db.Model):
    """
    Modèle représentant une transaction financière liée à un bien immobilier.
    
    Attributs:
        id (int): Identifiant unique de la transaction financière
        property_id (int): ID du bien immobilier concerné
        transaction_id (int): ID de la transaction immobilière associée (si applicable)
        transaction_type (str): Type de transaction ('rent_payment', 'expense', 'tax', etc.)
        amount (float): Montant de la transaction
        currency (str): Devise de la transaction
        transaction_date (date): Date de la transaction
        description (str): Description de la transaction
        category (str): Catégorie de la transaction
        payment_method (str): Méthode de paiement
        reference_number (str): Numéro de référence
        is_income (bool): Indique s'il s'agit d'un revenu ou d'une dépense
        created_at (datetime): Date de création de l'enregistrement
        created_by (int): ID de l'utilisateur ayant créé l'enregistrement
    """
    __tablename__ = 'financial_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'))
    transaction_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    reference_number = db.Column(db.String(50))
    is_income = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relations
    property = db.relationship('Property', backref='financial_transactions')
    creator = db.relationship('User', backref='created_financial_transactions', foreign_keys=[created_by])
    
    def get_formatted_amount(self):
        """
        Retourne le montant formaté de la transaction.
        
        Returns:
            str: Montant formaté avec devise et signe
        """
        sign = '+' if self.is_income else '-'
        return f"{sign} {self.amount:,.2f} {self.currency}"
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet FinancialTransaction.
        
        Returns:
            str: Représentation de la transaction financière
        """
        transaction_type = self.transaction_type.replace('_', ' ').capitalize()
        return f'<FinancialTransaction {self.id}: {transaction_type}, {self.get_formatted_amount()}>'


class MaintenanceRequest(db.Model):
    """
    Modèle représentant une demande de maintenance pour un bien immobilier.
    
    Attributs:
        id (int): Identifiant unique de la demande
        property_id (int): ID du bien immobilier concerné
        requested_by (int): ID du client ayant fait la demande (si locataire)
        request_date (datetime): Date de la demande
        issue_description (str): Description du problème
        priority (str): Priorité de la demande ('low', 'medium', 'high', 'emergency')
        status (str): Statut de la demande ('pending', 'assigned', 'in_progress', 'completed', 'cancelled')
        assigned_to (int): ID de l'utilisateur assigné à la demande
        estimated_cost (float): Coût estimé des travaux
        actual_cost (float): Coût réel des travaux
        scheduled_date (date): Date prévue pour les travaux
        completion_date (date): Date de fin des travaux
        notes (str): Notes diverses sur la demande
        updated_at (datetime): Date de dernière mise à jour de l'enregistrement
    """
    __tablename__ = 'maintenance_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('clients.id'))
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    issue_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    estimated_cost = db.Column(db.Numeric(10, 2))
    actual_cost = db.Column(db.Numeric(10, 2))
    scheduled_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_priority_display(self):
        """
        Retourne la priorité formatée pour l'affichage.
        
        Returns:
            str: Priorité formatée
        """
        priority_map = {
            'low': 'Basse',
            'medium': 'Moyenne',
            'high': 'Haute',
            'emergency': 'Urgence'
        }
        return priority_map.get(self.priority, self.priority)
    
    def get_status_display(self):
        """
        Retourne le statut formaté pour l'affichage.
        
        Returns:
            str: Statut formaté
        """
        status_map = {
            'pending': 'En attente',
            'assigned': 'Assignée',
            'in_progress': 'En cours',
            'completed': 'Terminée',
            'cancelled': 'Annulée'
        }
        return status_map.get(self.status, self.status)
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet MaintenanceRequest.
        
        Returns:
            str: Représentation de la demande de maintenance
        """
        return f'<MaintenanceRequest {self.id}: Property {self.property_id}, {self.get_status_display()}>'
