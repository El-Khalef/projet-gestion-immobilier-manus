#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Services de gestion des transactions immobilières.
Ce fichier contient les fonctions métier liées aux transactions (ventes et locations).
"""

from datetime import datetime
from app import db
from app.models.__init__1 import Transaction, RentalAgreement

def get_transaction_by_id(transaction_id):
    """
    Récupère une transaction par son ID.
    
    Args:
        transaction_id (int): ID de la transaction à récupérer
        
    Returns:
        Transaction: La transaction trouvée ou None si non trouvée
    """
    return Transaction.query.get(transaction_id)

def get_all_transactions(page=1, per_page=10, filters=None):
    """
    Récupère toutes les transactions avec pagination et filtrage optionnel.
    
    Args:
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        filters (dict, optional): Filtres à appliquer
        
    Returns:
        tuple: (Liste des transactions, nombre total de pages, nombre total d'éléments)
    """
    query = Transaction.query
    
    # Application des filtres
    if filters:
        if 'transaction_type' in filters:
            query = query.filter(Transaction.transaction_type == filters['transaction_type'])
        if 'status' in filters:
            query = query.filter(Transaction.status == filters['status'])
        if 'property_id' in filters:
            query = query.filter(Transaction.property_id == filters['property_id'])
        if 'client_id' in filters:
            query = query.filter(Transaction.client_id == filters['client_id'])
        if 'handled_by' in filters:
            query = query.filter(Transaction.handled_by == filters['handled_by'])
        if 'min_amount' in filters:
            query = query.filter(Transaction.amount >= filters['min_amount'])
        if 'max_amount' in filters:
            query = query.filter(Transaction.amount <= filters['max_amount'])
        if 'start_date' in filters:
            query = query.filter(Transaction.transaction_date >= filters['start_date'])
        if 'end_date' in filters:
            query = query.filter(Transaction.transaction_date <= filters['end_date'])
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total

def create_transaction(data, handled_by):
    """
    Crée une nouvelle transaction.
    
    Args:
        data (dict): Données de la transaction
        handled_by (int): ID de l'utilisateur gérant la transaction
        
    Returns:
        Transaction: La transaction créée
        
    Raises:
        ValueError: Si des données invalides sont fournies
    """
    # Validation des données
    if data['transaction_type'] not in ['sale', 'rental']:
        raise ValueError("Le type de transaction doit être 'sale' ou 'rental'")
    
    if data['status'] not in ['pending', 'completed', 'cancelled']:
        raise ValueError("Le statut doit être 'pending', 'completed' ou 'cancelled'")
    
    # Création de la transaction
    transaction = Transaction(
        transaction_type=data['transaction_type'],
        property_id=data['property_id'],
        client_id=data['client_id'],
        transaction_date=data['transaction_date'],
        amount=data['amount'],
        commission_amount=data.get('commission_amount'),
        commission_percentage=data.get('commission_percentage'),
        status=data['status'],
        payment_method=data.get('payment_method'),
        notes=data.get('notes'),
        handled_by=handled_by
    )
    
    # Sauvegarde dans la base de données
    db.session.add(transaction)
    db.session.commit()
    
    # Si c'est une location et qu'un contrat de location est fourni, créer le contrat
    if data['transaction_type'] == 'rental' and 'rental_agreement' in data:
        create_rental_agreement(transaction.id, data['rental_agreement'])
    
    return transaction

def update_transaction(transaction_id, data):
    """
    Met à jour une transaction existante.
    
    Args:
        transaction_id (int): ID de la transaction à mettre à jour
        data (dict): Données à mettre à jour
        
    Returns:
        Transaction: La transaction mise à jour ou None si non trouvée
        
    Raises:
        ValueError: Si des données invalides sont fournies
    """
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        return None
    
    # Validation des données
    if 'transaction_type' in data and data['transaction_type'] not in ['sale', 'rental']:
        raise ValueError("Le type de transaction doit être 'sale' ou 'rental'")
    
    if 'status' in data and data['status'] not in ['pending', 'completed', 'cancelled']:
        raise ValueError("Le statut doit être 'pending', 'completed' ou 'cancelled'")
    
    # Mise à jour des attributs
    for key, value in data.items():
        if key != 'rental_agreement' and hasattr(transaction, key):
            setattr(transaction, key, value)
    
    # Mise à jour de la date de modification
    transaction.updated_at = datetime.utcnow()
    
    # Si c'est une location et qu'un contrat de location est fourni, mettre à jour le contrat
    if transaction.transaction_type == 'rental' and 'rental_agreement' in data:
        if transaction.rental_agreement:
            update_rental_agreement(transaction.id, data['rental_agreement'])
        else:
            create_rental_agreement(transaction.id, data['rental_agreement'])
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return transaction

def delete_transaction(transaction_id):
    """
    Supprime une transaction.
    
    Args:
        transaction_id (int): ID de la transaction à supprimer
        
    Returns:
        bool: True si la transaction a été supprimée, False sinon
        
    Raises:
        ValueError: Si la transaction est complétée et ne peut pas être supprimée
    """
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        return False
    
    # Vérification si la transaction est complétée
    if transaction.status == 'completed':
        raise ValueError("Impossible de supprimer une transaction complétée")
    
    db.session.delete(transaction)
    db.session.commit()
    
    return True

def get_rental_agreement(transaction_id):
    """
    Récupère le contrat de location associé à une transaction.
    
    Args:
        transaction_id (int): ID de la transaction
        
    Returns:
        RentalAgreement: Le contrat de location ou None si non trouvé
    """
    return RentalAgreement.query.filter_by(transaction_id=transaction_id).first()

def create_rental_agreement(transaction_id, data):
    """
    Crée un contrat de location pour une transaction.
    
    Args:
        transaction_id (int): ID de la transaction
        data (dict): Données du contrat de location
        
    Returns:
        RentalAgreement: Le contrat de location créé
        
    Raises:
        ValueError: Si la transaction n'est pas de type location
    """
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        raise ValueError("Transaction non trouvée")
    
    if transaction.transaction_type != 'rental':
        raise ValueError("Le contrat de location ne peut être créé que pour une transaction de type location")
    
    # Création du contrat de location
    rental_agreement = RentalAgreement(
        transaction_id=transaction_id,
        start_date=data['start_date'],
        end_date=data['end_date'],
        is_renewable=data.get('is_renewable', True),
        rent_amount=data['rent_amount'],
        rent_frequency=data['rent_frequency'],
        deposit_amount=data['deposit_amount'],
        payment_day=data['payment_day'],
        special_conditions=data.get('special_conditions')
    )
    
    # Sauvegarde dans la base de données
    db.session.add(rental_agreement)
    db.session.commit()
    
    return rental_agreement

def update_rental_agreement(transaction_id, data):
    """
    Met à jour un contrat de location existant.
    
    Args:
        transaction_id (int): ID de la transaction
        data (dict): Données à mettre à jour
        
    Returns:
        RentalAgreement: Le contrat de location mis à jour ou None si non trouvé
    """
    rental_agreement = get_rental_agreement(transaction_id)
    if not rental_agreement:
        return None
    
    # Mise à jour des attributs
    for key, value in data.items():
        if hasattr(rental_agreement, key):
            setattr(rental_agreement, key, value)
    
    # Mise à jour de la date de modification
    rental_agreement.updated_at = datetime.utcnow()
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return rental_agreement

def get_property_transactions(property_id, page=1, per_page=10, transaction_type=None):
    """
    Récupère les transactions associées à un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        transaction_type (str, optional): Type de transaction ('sale' ou 'rental')
        
    Returns:
        tuple: (Liste des transactions, nombre total de pages, nombre total d'éléments)
    """
    query = Transaction.query.filter_by(property_id=property_id)
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total

def get_client_transactions(client_id, page=1, per_page=10, transaction_type=None):
    """
    Récupère les transactions associées à un client.
    
    Args:
        client_id (int): ID du client
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        transaction_type (str, optional): Type de transaction ('sale' ou 'rental')
        
    Returns:
        tuple: (Liste des transactions, nombre total de pages, nombre total d'éléments)
    """
    query = Transaction.query.filter_by(client_id=client_id)
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total

def change_transaction_status(transaction_id, status, notes=None):
    """
    Change le statut d'une transaction.
    
    Args:
        transaction_id (int): ID de la transaction
        status (str): Nouveau statut ('pending', 'completed', 'cancelled')
        notes (str, optional): Notes sur le changement de statut
        
    Returns:
        Transaction: La transaction mise à jour ou None si non trouvée
        
    Raises:
        ValueError: Si le statut est invalide
    """
    if status not in ['pending', 'completed', 'cancelled']:
        raise ValueError("Le statut doit être 'pending', 'completed' ou 'cancelled'")
    
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        return None
    
    # Mise à jour du statut
    transaction.status = status
    
    # Ajout des notes si fournies
    if notes:
        if transaction.notes:
            transaction.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Changement de statut à '{status}': {notes}"
        else:
            transaction.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Changement de statut à '{status}': {notes}"
    
    # Mise à jour de la date de modification
    transaction.updated_at = datetime.utcnow()
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return transaction
