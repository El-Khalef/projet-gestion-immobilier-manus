#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Routes de gestion des transactions immobilières.
Ce fichier définit les endpoints API pour la gestion des transactions (ventes et locations).
"""

from flask import Blueprint, request, jsonify, current_app, g
from datetime import datetime

from app.routes.old_auth import token_required
from app.models.__init__1 import Transaction, RentalAgreement
from app.services.transaction_service import (
    get_transaction_by_id, get_all_transactions, create_transaction, update_transaction, delete_transaction,
    get_rental_agreement, create_rental_agreement, update_rental_agreement,
    get_property_transactions, get_client_transactions, change_transaction_status
)

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    """
    Endpoint pour récupérer la liste des transactions avec pagination et filtrage.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Récupération des paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Récupération des filtres
    filters = {}
    filter_params = [
        'transaction_type', 'status', 'property_id', 'client_id', 'handled_by',
        'min_amount', 'max_amount', 'start_date', 'end_date'
    ]
    
    for param in filter_params:
        value = request.args.get(param)
        if value:
            # Conversion des valeurs numériques
            if param in ['property_id', 'client_id', 'handled_by']:
                try:
                    value = int(value)
                except ValueError:
                    continue
            elif param in ['min_amount', 'max_amount']:
                try:
                    value = float(value)
                except ValueError:
                    continue
            elif param in ['start_date', 'end_date']:
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    continue
            filters[param] = value
    
    # Récupération des transactions
    transactions, total_pages, total_items = get_all_transactions(page, per_page, filters)
    
    # Construction de la réponse
    result = {
        'transactions': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        }
    }
    
    # Formatage des transactions
    for transaction in transactions:
        result['transactions'].append({
            'id': transaction.id,
            'transaction_type': transaction.transaction_type,
            'property_id': transaction.property_id,
            'client_id': transaction.client_id,
            'transaction_date': transaction.transaction_date.isoformat(),
            'amount': float(transaction.amount),
            'status': transaction.status,
            'payment_method': transaction.payment_method,
            'has_rental_agreement': transaction.rental_agreement is not None,
            'created_at': transaction.created_at.isoformat()
        })
    
    return jsonify(result), 200

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    Endpoint pour récupérer une transaction spécifique.
    
    Args:
        transaction_id (int): ID de la transaction à récupérer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        return jsonify({'message': 'Transaction non trouvée'}), 404
    
    # Récupération du contrat de location si c'est une location
    rental_agreement_data = None
    if transaction.transaction_type == 'rental' and transaction.rental_agreement:
        rental_agreement = transaction.rental_agreement
        rental_agreement_data = {
            'start_date': rental_agreement.start_date.isoformat(),
            'end_date': rental_agreement.end_date.isoformat(),
            'is_renewable': rental_agreement.is_renewable,
            'rent_amount': float(rental_agreement.rent_amount),
            'rent_frequency': rental_agreement.rent_frequency,
            'deposit_amount': float(rental_agreement.deposit_amount),
            'payment_day': rental_agreement.payment_day,
            'special_conditions': rental_agreement.special_conditions,
            'duration_months': rental_agreement.get_duration_months()
        }
    
    # Construction de la réponse détaillée
    result = {
        'id': transaction.id,
        'transaction_type': transaction.transaction_type,
        'property_id': transaction.property_id,
        'property_title': transaction.property.title if transaction.property else None,
        'client_id': transaction.client_id,
        'client_name': transaction.client.get_full_name() if transaction.client else None,
        'transaction_date': transaction.transaction_date.isoformat(),
        'amount': float(transaction.amount),
        'formatted_amount': transaction.get_formatted_amount(),
        'commission': {
            'amount': float(transaction.commission_amount) if transaction.commission_amount else None,
            'percentage': float(transaction.commission_percentage) if transaction.commission_percentage else None,
            'formatted': transaction.get_commission_info()
        },
        'status': transaction.status,
        'payment_method': transaction.payment_method,
        'notes': transaction.notes,
        'handled_by': transaction.handled_by,
        'created_at': transaction.created_at.isoformat(),
        'updated_at': transaction.updated_at.isoformat(),
        'rental_agreement': rental_agreement_data
    }
    
    return jsonify(result), 200

@transactions_bp.route('/', methods=['POST'])
@token_required
def create_transaction_endpoint():
    """
    Endpoint pour créer une nouvelle transaction.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Validation des données requises
    required_fields = ['transaction_type', 'property_id', 'client_id', 'transaction_date', 'amount', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    try:
        # Conversion de la date de transaction
        if isinstance(data['transaction_date'], str):
            data['transaction_date'] = datetime.fromisoformat(data['transaction_date'])
        
        # Création de la transaction
        transaction = create_transaction(data, user.id)
        
        return jsonify({
            'message': 'Transaction créée avec succès',
            'transaction': {
                'id': transaction.id,
                'transaction_type': transaction.transaction_type,
                'property_id': transaction.property_id,
                'client_id': transaction.client_id,
                'amount': float(transaction.amount),
                'status': transaction.status
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création de la transaction: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la création de la transaction'}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction_endpoint(transaction_id):
    """
    Endpoint pour mettre à jour une transaction existante.
    
    Args:
        transaction_id (int): ID de la transaction à mettre à jour
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    try:
        # Conversion de la date de transaction si fournie
        if 'transaction_date' in data and isinstance(data['transaction_date'], str):
            data['transaction_date'] = datetime.fromisoformat(data['transaction_date'])
        
        # Conversion des dates du contrat de location si fournies
        if 'rental_agreement' in data:
            if 'start_date' in data['rental_agreement'] and isinstance(data['rental_agreement']['start_date'], str):
                data['rental_agreement']['start_date'] = datetime.fromisoformat(data['rental_agreement']['start_date']).date()
            if 'end_date' in data['rental_agreement'] and isinstance(data['rental_agreement']['end_date'], str):
                data['rental_agreement']['end_date'] = datetime.fromisoformat(data['rental_agreement']['end_date']).date()
        
        # Mise à jour de la transaction
        transaction = update_transaction(transaction_id, data)
        if not transaction:
            return jsonify({'message': 'Transaction non trouvée'}), 404
        
        return jsonify({
            'message': 'Transaction mise à jour avec succès',
            'transaction': {
                'id': transaction.id,
                'transaction_type': transaction.transaction_type,
                'property_id': transaction.property_id,
                'client_id': transaction.client_id,
                'amount': float(transaction.amount),
                'status': transaction.status
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour de la transaction: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour de la transaction'}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction_endpoint(transaction_id):
    """
    Endpoint pour supprimer une transaction.
    
    Args:
        transaction_id (int): ID de la transaction à supprimer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    try:
        # Suppression de la transaction
        success = delete_transaction(transaction_id)
        if not success:
            return jsonify({'message': 'Transaction non trouvée'}), 404
        
        return jsonify({'message': 'Transaction supprimée avec succès'}), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression de la transaction: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la suppression de la transaction'}), 500

@transactions_bp.route('/<int:transaction_id>/status', methods=['PUT'])
@token_required
def change_status(transaction_id):
    """
    Endpoint pour changer le statut d'une transaction.
    
    Args:
        transaction_id (int): ID de la transaction
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Validation des données requises
    if 'status' not in data:
        return jsonify({'message': 'Le statut est requis'}), 400
    
    try:
        # Changement du statut
        transaction = change_transaction_status(transaction_id, data['status'], data.get('notes'))
        if not transaction:
            return jsonify({'message': 'Transaction non trouvée'}), 404
        
        return jsonify({
            'message': 'Statut de la transaction mis à jour avec succès',
            'transaction': {
                'id': transaction.id,
                'status': transaction.status
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors du changement de statut de la transaction: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors du changement de statut de la transaction'}), 500

@transactions_bp.route('/property/<int:property_id>', methods=['GET'])
def get_property_transactions_endpoint(property_id):
    """
    Endpoint pour récupérer les transactions associées à un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Récupération des paramètres de pagination et filtrage
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    transaction_type = request.args.get('transaction_type')
    
    # Récupération des transactions
    transactions, total_pages, total_items = get_property_transactions(property_id, page, per_page, transaction_type)
    
    # Construction de la réponse
    result = {
        'transactions': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        },
        'property_id': property_id
    }
    
    # Formatage des transactions
    for transaction in transactions:
        result['transactions'].append({
            'id': transaction.id,
            'transaction_type': transaction.transaction_type,
            'client_id': transaction.client_id,
            'client_name': transaction.client.get_full_name() if transaction.client else None,
            'transaction_date': transaction.transaction_date.isoformat(),
            'amount': float(transaction.amount),
            'status': transaction.status,
            'created_at': transaction.created_at.isoformat()
        })
    
    return jsonify(result), 200

@transactions_bp.route('/client/<int:client_id>', methods=['GET'])
def get_client_transactions_endpoint(client_id):
    """
    Endpoint pour récupérer les transactions associées à un client.
    
    Args:
        client_id (int): ID du client
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Récupération des paramètres de pagination et filtrage
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    transaction_type = request.args.get('transaction_type')
    
    # Récupération des transactions
    transactions, total_pages, total_items = get_client_transactions(client_id, page, per_page, transaction_type)
    
    # Construction de la réponse
    result = {
        'transactions': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        },
        'client_id': client_id
    }
    
    # Formatage des transactions
    for transaction in transactions:
        result['transactions'].append({
            'id': transaction.id,
            'transaction_type': transaction.transaction_type,
            'property_id': transaction.property_id,
            'property_title': transaction.property.title if transaction.property else None,
            'transaction_date': transaction.transaction_date.isoformat(),
            'amount': float(transaction.amount),
            'status': transaction.status,
            'created_at': transaction.created_at.isoformat()
        })
    
    return jsonify(result), 200

@transactions_bp.route('/<int:transaction_id>/rental-agreement', methods=['GET'])
def get_rental_agreement_endpoint(transaction_id):
    """
    Endpoint pour récupérer le contrat de location associé à une transaction.
    
    Args:
        transaction_id (int): ID de la transaction
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Vérification que la transaction existe et est de type location
    transaction = get_transaction_by_id(transaction_id)
    if not transaction:
        return jsonify({'message': 'Transaction non trouvée'}), 404
    
    if transaction.transaction_type != 'rental':
        return jsonify({'message': 'Cette transaction n\'est pas une location'}), 400
    
    # Récupération du contrat de location
    rental_agreement = get_rental_agreement(transaction_id)
    if not rental_agreement:
        return jsonify({'message': 'Contrat de location non trouvé'}), 404
    
    # Construction de la réponse
    result = {
        'id': rental_agreement.id,
        'transaction_id': rental_agreement.transaction_id,
        'start_date': rental_agreement.start_date.isoformat(),
        'end_date': rental_agreement.end_date.isoformat(),
        'is_renewable': rental_agreement.is_renewable,
        'rent_amount': float(rental_agreement.rent_amount),
        'formatted_rent': rental_agreement.get_formatted_rent(),
        'rent_frequency': rental_agreement.rent_frequency,
        'deposit_amount': float(rental_agreement.deposit_amount),
        'payment_day': rental_agreement.payment_day,
        'special_conditions': rental_agreement.special_conditions,
        'duration_months': rental_agreement.get_duration_months(),
        'created_at': rental_agreement.created_at.isoformat(),
        'updated_at': rental_agreement.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@transactions_bp.route('/<int:transaction_id>/rental-agreement', methods=['POST'])
@token_required
def create_rental_agreement_endpoint(transaction_id):
    """
    Endpoint pour créer un contrat de location pour une transaction.
    
    Args:
        transaction_id (int): ID de la transaction
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Validation des données requises
    required_fields = ['start_date', 'end_date', 'rent_amount', 'rent_frequency', 'deposit_amount', 'payment_day']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    try:
        # Conversion des dates
        if isinstance(data['start_date'], str):
            data['start_date'] = datetime.fromisoformat(data['start_date']).date()
        if isinstance(data['end_date'], str):
            data['end_date'] = datetime.fromisoformat(data['end_date']).date()
        
        # Création du contrat de location
        rental_agreement = create_rental_agreement(transaction_id, data)
        
        return jsonify({
            'message': 'Contrat de location créé avec succès',
            'rental_agreement': {
                'id': rental_agreement.id,
                'transaction_id': rental_agreement.transaction_id,
                'start_date': rental_agreement.start_date.isoformat(),
                'end_date': rental_agreement.end_date.isoformat(),
                'rent_amount': float(rental_agreement.rent_amount),
                'rent_frequency': rental_agreement.rent_frequency
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création du contrat de location: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la création du contrat de location'}), 500

@transactions_bp.route('/<int:transaction_id>/rental-agreement', methods=['PUT'])
@token_required
def update_rental_agreement_endpoint(transaction_id):
    """
    Endpoint pour mettre à jour un contrat de location existant.
    
    Args:
        transaction_id (int): ID de la transaction
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    try:
        # Conversion des dates si fournies
        if 'start_date' in data and isinstance(data['start_date'], str):
            data['start_date'] = datetime.fromisoformat(data['start_date']).date()
        if 'end_date' in data and isinstance(data['end_date'], str):
            data['end_date'] = datetime.fromisoformat(data['end_date']).date()
        
        # Mise à jour du contrat de location
        rental_agreement = update_rental_agreement(transaction_id, data)
        if not rental_agreement:
            return jsonify({'message': 'Contrat de location non trouvé'}), 404
        
        return jsonify({
            'message': 'Contrat de location mis à jour avec succès',
            'rental_agreement': {
                'id': rental_agreement.id,
                'transaction_id': rental_agreement.transaction_id,
                'start_date': rental_agreement.start_date.isoformat(),
                'end_date': rental_agreement.end_date.isoformat(),
                'rent_amount': float(rental_agreement.rent_amount),
                'rent_frequency': rental_agreement.rent_frequency
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour du contrat de location: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour du contrat de location'}), 500
