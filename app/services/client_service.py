#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Services de gestion des clients.
Ce fichier contient les fonctions métier liées aux clients (acheteurs/locataires).
"""

from datetime import datetime
from app import db
from app.models.__init__1 import Client, PropertyVisit

def get_client_by_id(client_id):
    """
    Récupère un client par son ID.
    
    Args:
        client_id (int): ID du client à récupérer
        
    Returns:
        Client: Le client trouvé ou None si non trouvé
    """
    return Client.query.get(client_id)

def get_all_clients(page=1, per_page=10, search=None, client_type=None, assigned_agent_id=None):
    """
    Récupère tous les clients avec pagination et filtrage optionnel.
    
    Args:
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        search (str, optional): Terme de recherche pour filtrer les clients
        client_type (str, optional): Type de client ('buyer', 'tenant', 'both')
        assigned_agent_id (int, optional): ID de l'agent assigné
        
    Returns:
        tuple: (Liste des clients, nombre total de pages, nombre total d'éléments)
    """
    query = Client.query
    
    # Application des filtres
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Client.first_name.ilike(search_term),
                Client.last_name.ilike(search_term),
                Client.email.ilike(search_term),
                Client.phone.ilike(search_term),
                Client.city.ilike(search_term)
            )
        )
    
    if client_type:
        query = query.filter(Client.client_type == client_type)
    
    if assigned_agent_id:
        query = query.filter(Client.assigned_agent_id == assigned_agent_id)
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total

def create_client(data, created_by):
    """
    Crée un nouveau client.
    
    Args:
        data (dict): Données du client
        created_by (int): ID de l'utilisateur créant le client
        
    Returns:
        Client: Le client créé
        
    Raises:
        ValueError: Si l'email existe déjà
    """
    # Vérification de l'unicité de l'email
    if 'email' in data and data['email']:
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client:
            raise ValueError(f"L'email '{data['email']}' existe déjà")
    
    # Création du client
    client = Client(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data.get('email'),
        phone=data.get('phone'),
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state_province=data.get('state_province'),
        postal_code=data.get('postal_code'),
        country=data.get('country'),
        client_type=data['client_type'],  # 'buyer', 'tenant', 'both'
        budget_min=data.get('budget_min'),
        budget_max=data.get('budget_max'),
        requirements=data.get('requirements'),
        notes=data.get('notes'),
        assigned_agent_id=data.get('assigned_agent_id')
    )
    
    # Sauvegarde dans la base de données
    db.session.add(client)
    db.session.commit()
    
    return client

def update_client(client_id, data):
    """
    Met à jour un client existant.
    
    Args:
        client_id (int): ID du client à mettre à jour
        data (dict): Données à mettre à jour
        
    Returns:
        Client: Le client mis à jour ou None si non trouvé
        
    Raises:
        ValueError: Si l'email existe déjà pour un autre client
    """
    client = get_client_by_id(client_id)
    if not client:
        return None
    
    # Vérification de l'unicité de l'email
    if 'email' in data and data['email'] and data['email'] != client.email:
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client:
            raise ValueError(f"L'email '{data['email']}' existe déjà")
    
    # Mise à jour des attributs
    for key, value in data.items():
        if hasattr(client, key):
            setattr(client, key, value)
    
    # Mise à jour de la date de modification
    client.updated_at = datetime.utcnow()
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return client

def delete_client(client_id):
    """
    Supprime un client.
    
    Args:
        client_id (int): ID du client à supprimer
        
    Returns:
        bool: True si le client a été supprimé, False sinon
        
    Raises:
        ValueError: Si le client a des transactions actives
    """
    client = get_client_by_id(client_id)
    if not client:
        return False
    
    # Vérification si le client a des transactions actives
    if client.transactions.filter_by(status='pending').count() > 0:
        raise ValueError("Impossible de supprimer un client qui a des transactions en cours")
    
    db.session.delete(client)
    db.session.commit()
    
    return True

def add_property_interest(client_id, property_id, interest_level, notes=None):
    """
    Ajoute un intérêt d'un client pour un bien immobilier.
    
    Args:
        client_id (int): ID du client
        property_id (int): ID du bien immobilier
        interest_level (str): Niveau d'intérêt ('none', 'low', 'medium', 'high')
        notes (str, optional): Notes sur l'intérêt
        
    Returns:
        bool: True si l'intérêt a été ajouté, False sinon
    """
    client = get_client_by_id(client_id)
    if not client:
        return False
    
    # Vérification si le bien immobilier existe
    from app.services.property_service import get_property_by_id
    property = get_property_by_id(property_id)
    if not property:
        return False
    
    # Ajout de l'intérêt
    client.interested_properties.append(property)
    
    # Mise à jour de la table de jointure
    stmt = db.text(
        "UPDATE client_property_interests "
        "SET interest_level = :interest_level, notes = :notes, updated_at = :updated_at "
        "WHERE client_id = :client_id AND property_id = :property_id"
    )
    db.session.execute(
        stmt,
        {
            'interest_level': interest_level,
            'notes': notes,
            'updated_at': datetime.utcnow(),
            'client_id': client_id,
            'property_id': property_id
        }
    )
    
    db.session.commit()
    
    return True

def remove_property_interest(client_id, property_id):
    """
    Supprime l'intérêt d'un client pour un bien immobilier.
    
    Args:
        client_id (int): ID du client
        property_id (int): ID du bien immobilier
        
    Returns:
        bool: True si l'intérêt a été supprimé, False sinon
    """
    client = get_client_by_id(client_id)
    if not client:
        return False
    
    # Vérification si le bien immobilier existe
    from app.services.property_service import get_property_by_id
    property = get_property_by_id(property_id)
    if not property:
        return False
    
    # Suppression de l'intérêt
    client.interested_properties.remove(property)
    db.session.commit()
    
    return True

def get_client_interested_properties(client_id, page=1, per_page=10):
    """
    Récupère les biens immobiliers qui intéressent un client.
    
    Args:
        client_id (int): ID du client
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        
    Returns:
        tuple: (Liste des biens immobiliers, nombre total de pages, nombre total d'éléments)
    """
    client = get_client_by_id(client_id)
    if not client:
        return [], 0, 0
    
    # Pagination
    pagination = client.interested_properties.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total

def schedule_property_visit(client_id, property_id, visit_date, duration=60, accompanied_by=None, notes=None):
    """
    Planifie une visite de bien immobilier pour un client.
    
    Args:
        client_id (int): ID du client
        property_id (int): ID du bien immobilier
        visit_date (datetime): Date et heure de la visite
        duration (int, optional): Durée de la visite en minutes
        accompanied_by (int, optional): ID de l'utilisateur accompagnant la visite
        notes (str, optional): Notes sur la visite
        
    Returns:
        PropertyVisit: La visite créée ou None si erreur
    """
    # Vérification si le client existe
    client = get_client_by_id(client_id)
    if not client:
        return None
    
    # Vérification si le bien immobilier existe
    from app.services.property_service import get_property_by_id
    property = get_property_by_id(property_id)
    if not property:
        return None
    
    # Création de la visite
    visit = PropertyVisit(
        property_id=property_id,
        client_id=client_id,
        visit_date=visit_date,
        duration=duration,
        status='scheduled',
        accompanied_by=accompanied_by,
        notes=notes
    )
    
    # Sauvegarde dans la base de données
    db.session.add(visit)
    db.session.commit()
    
    return visit

def update_property_visit(visit_id, data):
    """
    Met à jour une visite de bien immobilier.
    
    Args:
        visit_id (int): ID de la visite à mettre à jour
        data (dict): Données à mettre à jour
        
    Returns:
        PropertyVisit: La visite mise à jour ou None si non trouvée
    """
    visit = PropertyVisit.query.get(visit_id)
    if not visit:
        return None
    
    # Mise à jour des attributs
    for key, value in data.items():
        if hasattr(visit, key):
            setattr(visit, key, value)
    
    # Mise à jour de la date de modification
    visit.updated_at = datetime.utcnow()
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return visit

def get_client_visits(client_id, page=1, per_page=10, status=None):
    """
    Récupère les visites d'un client.
    
    Args:
        client_id (int): ID du client
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        status (str, optional): Statut des visites à récupérer
        
    Returns:
        tuple: (Liste des visites, nombre total de pages, nombre total d'éléments)
    """
    query = PropertyVisit.query.filter_by(client_id=client_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total
