#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle Client pour la gestion des clients (acheteurs/locataires).
Ce fichier définit la structure de la table des clients et ses méthodes associées.
"""

from datetime import datetime
from app import db

# Table de jointure pour la relation many-to-many entre Client et Property (intérêts)
client_property_interests = db.Table('client_property_interests',
    db.Column('client_id', db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True),
    db.Column('interest_level', db.String(20), nullable=False),
    db.Column('notes', db.Text),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

class Client(db.Model):
    """
    Modèle représentant un client (acheteur ou locataire potentiel).
    
    Attributs:
        id (int): Identifiant unique du client
        first_name (str): Prénom du client
        last_name (str): Nom de famille du client
        email (str): Adresse email du client
        phone (str): Numéro de téléphone du client
        address_line1 (str): Première ligne d'adresse
        address_line2 (str): Seconde ligne d'adresse (optionnelle)
        city (str): Ville
        state_province (str): État ou province
        postal_code (str): Code postal
        country (str): Pays
        client_type (str): Type de client (acheteur, locataire, les deux)
        budget_min (float): Budget minimum
        budget_max (float): Budget maximum
        requirements (str): Exigences et préférences du client
        notes (str): Notes diverses sur le client
        created_at (datetime): Date de création de l'enregistrement
        updated_at (datetime): Date de dernière mise à jour de l'enregistrement
        assigned_agent_id (int): ID de l'agent immobilier assigné au client
    """
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state_province = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    client_type = db.Column(db.String(20), nullable=False)  # 'buyer', 'tenant', 'both'
    budget_min = db.Column(db.Numeric(12, 2))
    budget_max = db.Column(db.Numeric(12, 2))
    requirements = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relations
    interested_properties = db.relationship('Property', secondary=client_property_interests,
                                          lazy='dynamic',
                                          backref=db.backref('interested_clients', lazy='dynamic'))
    transactions = db.relationship('Transaction', backref='client', lazy='dynamic')
    visits = db.relationship('PropertyVisit', backref='client', lazy='dynamic')
    maintenance_requests = db.relationship('MaintenanceRequest', backref='requester', lazy='dynamic',
                                         foreign_keys='MaintenanceRequest.requested_by')
    
    def get_full_name(self):
        """
        Retourne le nom complet du client.
        
        Returns:
            str: Nom complet du client
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_full_address(self):
        """
        Retourne l'adresse complète du client.
        
        Returns:
            str: Adresse complète formatée
        """
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.city and self.postal_code:
            address_parts.append(f"{self.city}, {self.postal_code}")
        elif self.city:
            address_parts.append(self.city)
        if self.state_province:
            address_parts.append(self.state_province)
        if self.country:
            address_parts.append(self.country)
        return "\n".join(address_parts)
    
    def get_budget_range(self):
        """
        Retourne la fourchette de budget du client.
        
        Returns:
            str: Fourchette de budget formatée
        """
        if self.budget_min and self.budget_max:
            return f"{self.budget_min:,.2f} € - {self.budget_max:,.2f} €"
        elif self.budget_min:
            return f"À partir de {self.budget_min:,.2f} €"
        elif self.budget_max:
            return f"Jusqu'à {self.budget_max:,.2f} €"
        return "Budget non spécifié"
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet Client.
        
        Returns:
            str: Représentation du client
        """
        return f'<Client {self.id}: {self.get_full_name()}>'


class PropertyVisit(db.Model):
    """
    Modèle représentant une visite de bien immobilier par un client.
    
    Attributs:
        id (int): Identifiant unique de la visite
        property_id (int): ID du bien immobilier visité
        client_id (int): ID du client effectuant la visite
        visit_date (datetime): Date et heure de la visite
        duration (int): Durée de la visite en minutes
        status (str): Statut de la visite (planifiée, terminée, annulée, absence)
        feedback (str): Retour du client sur la visite
        interest_level (str): Niveau d'intérêt du client (aucun, faible, moyen, élevé)
        accompanied_by (int): ID de l'utilisateur accompagnant la visite
        notes (str): Notes diverses sur la visite
        created_at (datetime): Date de création de l'enregistrement
        updated_at (datetime): Date de dernière mise à jour de l'enregistrement
    """
    __tablename__ = 'property_visits'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # en minutes
    status = db.Column(db.String(20), nullable=False)  # 'scheduled', 'completed', 'cancelled', 'no_show'
    feedback = db.Column(db.Text)
    interest_level = db.Column(db.String(20))  # 'none', 'low', 'medium', 'high'
    accompanied_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec l'utilisateur accompagnant
    accompanier = db.relationship('User', backref='accompanied_visits', foreign_keys=[accompanied_by])
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet PropertyVisit.
        
        Returns:
            str: Représentation de la visite
        """
        return f'<PropertyVisit {self.id}: Property {self.property_id}, Client {self.client_id}, Date {self.visit_date}>'
