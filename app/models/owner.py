#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle Owner pour la gestion des propriétaires de biens immobiliers.
Ce fichier définit la structure de la table des propriétaires et ses méthodes associées.
"""

from datetime import datetime
from app import db

class Owner(db.Model):
    """
    Modèle représentant un propriétaire de biens immobiliers.
    
    Attributs:
        id (int): Identifiant unique du propriétaire
        first_name (str): Prénom du propriétaire
        last_name (str): Nom de famille du propriétaire
        email (str): Adresse email du propriétaire
        phone (str): Numéro de téléphone du propriétaire
        address_line1 (str): Première ligne d'adresse
        address_line2 (str): Seconde ligne d'adresse (optionnelle)
        city (str): Ville
        state_province (str): État ou province
        postal_code (str): Code postal
        country (str): Pays
        tax_id (str): Identifiant fiscal
        notes (str): Notes diverses sur le propriétaire
        created_at (datetime): Date de création de l'enregistrement
        updated_at (datetime): Date de dernière mise à jour de l'enregistrement
    """
    __tablename__ = 'owners'
    
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
    tax_id = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    properties = db.relationship('Property', backref='owner', lazy='dynamic')
    
    def get_full_name(self):
        """
        Retourne le nom complet du propriétaire.
        
        Returns:
            str: Nom complet du propriétaire
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_full_address(self):
        """
        Retourne l'adresse complète du propriétaire.
        
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
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet Owner.
        
        Returns:
            str: Représentation du propriétaire
        """
        return f'<Owner {self.id}: {self.get_full_name()}>'
