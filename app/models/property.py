#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modèle Property pour la gestion des biens immobiliers.
Ce fichier définit la structure de la table des biens immobiliers et ses méthodes associées.
"""

from datetime import datetime
from app import db

# Table de jointure pour la relation many-to-many entre Property et Amenity
property_amenities = db.Table('property_amenities',
    db.Column('property_id', db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id', ondelete='CASCADE'), primary_key=True)
)

class Property(db.Model):
    """
    Modèle représentant un bien immobilier.
    
    Attributs:
        id (int): Identifiant unique du bien
        reference_code (str): Code de référence unique du bien
        title (str): Titre du bien
        description (str): Description détaillée du bien
        property_type (str): Type de bien (appartement, maison, terrain, commercial, etc.)
        status (str): Statut du bien (disponible, vendu, loué, etc.)
        address_* (str): Informations d'adresse
        latitude/longitude (float): Coordonnées géographiques
        total_area (float): Surface totale en mètres carrés
        living_area (float): Surface habitable en mètres carrés
        land_area (float): Surface du terrain en mètres carrés
        num_bedrooms (int): Nombre de chambres
        num_bathrooms (int): Nombre de salles de bain
        num_floors (int): Nombre d'étages
        year_built (int): Année de construction
        energy_rating (str): Classement énergétique
        has_* (bool): Équipements principaux (garage, jardin, etc.)
        is_furnished (bool): Indique si le bien est meublé
        asking_price (float): Prix de vente demandé
        rental_price (float): Prix de location demandé
        created_at (datetime): Date de création de l'enregistrement
        updated_at (datetime): Date de dernière mise à jour de l'enregistrement
        created_by (int): ID de l'utilisateur ayant créé l'enregistrement
        owner_id (int): ID du propriétaire du bien
    """
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    property_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    
    # Adresse
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50), nullable=False)
    state_province = db.Column(db.String(50))
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    
    # Caractéristiques
    total_area = db.Column(db.Numeric(10, 2), nullable=False)
    living_area = db.Column(db.Numeric(10, 2))
    land_area = db.Column(db.Numeric(10, 2))
    num_bedrooms = db.Column(db.Integer)
    num_bathrooms = db.Column(db.Integer)
    num_floors = db.Column(db.Integer)
    year_built = db.Column(db.Integer)
    energy_rating = db.Column(db.String(10))
    
    # Équipements
    has_garage = db.Column(db.Boolean, default=False)
    has_garden = db.Column(db.Boolean, default=False)
    has_terrace = db.Column(db.Boolean, default=False)
    has_pool = db.Column(db.Boolean, default=False)
    is_furnished = db.Column(db.Boolean, default=False)
    
    # Prix
    asking_price = db.Column(db.Numeric(12, 2))
    rental_price = db.Column(db.Numeric(10, 2))
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
    
    # Relations
    images = db.relationship('PropertyImage', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('PropertyDocument', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary=property_amenities, lazy='subquery',
                               backref=db.backref('properties', lazy=True))
    transactions = db.relationship('Transaction', backref='property', lazy='dynamic')
    maintenance_requests = db.relationship('MaintenanceRequest', backref='property', lazy='dynamic')
    visits = db.relationship('PropertyVisit', backref='property', lazy='dynamic')
    
    def get_full_address(self):
        """
        Retourne l'adresse complète du bien.
        
        Returns:
            str: Adresse complète formatée
        """
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.append(f"{self.city}, {self.postal_code}")
        if self.state_province:
            address_parts.append(self.state_province)
        address_parts.append(self.country)
        return ", ".join(address_parts)
    
    def get_primary_image_url(self):
        """
        Retourne l'URL de l'image principale du bien.
        
        Returns:
            str: URL de l'image principale ou None si aucune image
        """
        primary_image = self.images.filter_by(is_primary=True).first()
        if primary_image:
            return primary_image.file_path
        # Si aucune image n'est marquée comme principale, retourne la première image
        first_image = self.images.first()
        return first_image.file_path if first_image else None
    
    def get_price_display(self):
        """
        Retourne le prix formaté selon le type de bien (vente ou location).
        
        Returns:
            str: Prix formaté avec devise
        """
        if self.status in ['for_sale', 'sold'] and self.asking_price:
            return f"{self.asking_price:,.2f} €"
        elif self.status in ['for_rent', 'rented'] and self.rental_price:
            return f"{self.rental_price:,.2f} € / mois"
        return "Prix sur demande"
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet Property.
        
        Returns:
            str: Représentation du bien immobilier
        """
        return f'<Property {self.reference_code}: {self.title}>'


class PropertyImage(db.Model):
    """
    Modèle représentant une image associée à un bien immobilier.
    
    Attributs:
        id (int): Identifiant unique de l'image
        property_id (int): ID du bien immobilier associé
        file_path (str): Chemin du fichier image
        file_name (str): Nom du fichier
        file_size (int): Taille du fichier en octets
        file_type (str): Type MIME du fichier
        is_primary (bool): Indique si c'est l'image principale du bien
        display_order (int): Ordre d'affichage
        title (str): Titre de l'image
        description (str): Description de l'image
        uploaded_at (datetime): Date d'upload de l'image
        uploaded_by (int): ID de l'utilisateur ayant uploadé l'image
    """
    __tablename__ = 'property_images'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet PropertyImage.
        
        Returns:
            str: Représentation de l'image
        """
        return f'<PropertyImage {self.id}: {self.file_name}>'


class PropertyDocument(db.Model):
    """
    Modèle représentant un document associé à un bien immobilier.
    
    Attributs:
        id (int): Identifiant unique du document
        property_id (int): ID du bien immobilier associé
        document_type (str): Type de document
        file_path (str): Chemin du fichier
        file_name (str): Nom du fichier
        file_size (int): Taille du fichier en octets
        file_type (str): Type MIME du fichier
        title (str): Titre du document
        description (str): Description du document
        uploaded_at (datetime): Date d'upload du document
        uploaded_by (int): ID de l'utilisateur ayant uploadé le document
        expiry_date (date): Date d'expiration du document (si applicable)
    """
    __tablename__ = 'property_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    expiry_date = db.Column(db.Date)
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet PropertyDocument.
        
        Returns:
            str: Représentation du document
        """
        return f'<PropertyDocument {self.id}: {self.document_type} - {self.file_name}>'


class Amenity(db.Model):
    """
    Modèle représentant un équipement ou une caractéristique pouvant être associé à un bien.
    
    Attributs:
        id (int): Identifiant unique de l'équipement
        name (str): Nom de l'équipement
        category (str): Catégorie de l'équipement
        description (str): Description de l'équipement
    """
    __tablename__ = 'amenities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet Amenity.
        
        Returns:
            str: Représentation de l'équipement
        """
        return f'<Amenity {self.id}: {self.name}>'
