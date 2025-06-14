#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Services de gestion des propriétaires.
Ce fichier contient les fonctions métier liées aux propriétaires de biens immobiliers.
"""

from datetime import datetime
from app import db
from app.models.__init__1 import Owner

def get_owner_by_id(owner_id):
    """
    Récupère un propriétaire par son ID.
    
    Args:
        owner_id (int): ID du propriétaire à récupérer
        
    Returns:
        Owner: Le propriétaire trouvé ou None si non trouvé
    """
    return Owner.query.get(owner_id)

def get_all_owners(page=1, per_page=10, search=None):
    """
    Récupère tous les propriétaires avec pagination et recherche optionnelle.
    
    Args:
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        search (str, optional): Terme de recherche pour filtrer les propriétaires
        
    Returns:
        tuple: (Liste des propriétaires, nombre total de pages, nombre total d'éléments)
    """
    query = Owner.query
    
    # Application du filtre de recherche si fourni
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Owner.first_name.ilike(search_term),
                Owner.last_name.ilike(search_term),
                Owner.email.ilike(search_term),
                Owner.company_name.ilike(search_term)
            )
        )
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total

def create_owner(data, created_by):
    """
    Crée un nouveau propriétaire.
    
    Args:
        data (dict): Données du propriétaire
        created_by (int): ID de l'utilisateur créant le propriétaire
        
    Returns:
        Owner: Le propriétaire créé
        
    Raises:
        ValueError: Si l'email existe déjà
    """
    # Vérification de l'unicité de l'email
    if 'email' in data and data['email']:
        existing_owner = Owner.query.filter_by(email=data['email']).first()
        if existing_owner:
            raise ValueError(f"L'email '{data['email']}' existe déjà")
    
    # Création du propriétaire
    owner = Owner(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state_province=data.get('state_province'),
        postal_code=data.get('postal_code'),
        country=data.get('country'),
        is_company=data.get('is_company', False),
        company_name=data.get('company_name'),
        company_registration_number=data.get('company_registration_number'),
        tax_id=data.get('tax_id'),
        notes=data.get('notes'),
        created_by=created_by
    )
    
    # Sauvegarde dans la base de données
    db.session.add(owner)
    db.session.commit()
    
    return owner

def update_owner(owner_id, data):
    """
    Met à jour un propriétaire existant.
    
    Args:
        owner_id (int): ID du propriétaire à mettre à jour
        data (dict): Données à mettre à jour
        
    Returns:
        Owner: Le propriétaire mis à jour ou None si non trouvé
        
    Raises:
        ValueError: Si l'email existe déjà pour un autre propriétaire
    """
    owner = get_owner_by_id(owner_id)
    if not owner:
        return None
    
    # Vérification de l'unicité de l'email
    if 'email' in data and data['email'] and data['email'] != owner.email:
        existing_owner = Owner.query.filter_by(email=data['email']).first()
        if existing_owner:
            raise ValueError(f"L'email '{data['email']}' existe déjà")
    
    # Mise à jour des attributs
    for key, value in data.items():
        if hasattr(owner, key):
            setattr(owner, key, value)
    
    # Mise à jour de la date de modification
    owner.updated_at = datetime.utcnow()
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return owner

def delete_owner(owner_id):
    """
    Supprime un propriétaire.
    
    Args:
        owner_id (int): ID du propriétaire à supprimer
        
    Returns:
        bool: True si le propriétaire a été supprimé, False sinon
    """
    owner = get_owner_by_id(owner_id)
    if not owner:
        return False
    
    # Vérification si le propriétaire a des biens immobiliers
    if owner.properties.count() > 0:
        raise ValueError("Impossible de supprimer un propriétaire qui possède des biens immobiliers")
    
    db.session.delete(owner)
    db.session.commit()
    
    return True

def get_owner_properties(owner_id, page=1, per_page=10):
    """
    Récupère les biens immobiliers d'un propriétaire.
    
    Args:
        owner_id (int): ID du propriétaire
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        
    Returns:
        tuple: (Liste des biens immobiliers, nombre total de pages, nombre total d'éléments)
    """
    owner = get_owner_by_id(owner_id)
    if not owner:
        return [], 0, 0
    
    # Pagination
    pagination = owner.properties.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total
