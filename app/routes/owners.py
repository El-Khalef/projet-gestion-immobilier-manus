#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Routes de gestion des propriétaires.
Ce fichier définit les endpoints API pour la gestion des propriétaires de biens immobiliers.
"""

from flask import Blueprint, request, jsonify, current_app, g
from app.routes.old_auth import token_required
from app.models.__init__1 import Owner
from app.services.owner_service import (
    get_owner_by_id, get_all_owners, create_owner, update_owner, delete_owner, get_owner_properties
)

owners_bp = Blueprint('owners', __name__, url_prefix='/api/owners')

@owners_bp.route('/', methods=['GET'])
def get_owners():
    """
    Endpoint pour récupérer la liste des propriétaires avec pagination et recherche.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Récupération des paramètres de pagination et recherche
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search')
    
    # Récupération des propriétaires
    owners, total_pages, total_items = get_all_owners(page, per_page, search)
    
    # Construction de la réponse
    result = {
        'owners': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        }
    }
    
    # Formatage des propriétaires
    for owner in owners:
        result['owners'].append({
            'id': owner.id,
            'first_name': owner.first_name,
            'last_name': owner.last_name,
            'email': owner.email,
            'phone': owner.phone,
            'city': owner.city,
            'country': owner.country,
            'is_company': owner.is_company,
            'company_name': owner.company_name,
            'properties_count': owner.properties.count(),
            'created_at': owner.created_at.isoformat()
        })
    
    return jsonify(result), 200

@owners_bp.route('/<int:owner_id>', methods=['GET'])
def get_owner(owner_id):
    """
    Endpoint pour récupérer un propriétaire spécifique.
    
    Args:
        owner_id (int): ID du propriétaire à récupérer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    owner = get_owner_by_id(owner_id)
    if not owner:
        return jsonify({'message': 'Propriétaire non trouvé'}), 404
    
    # Construction de la réponse détaillée
    result = {
        'id': owner.id,
        'first_name': owner.first_name,
        'last_name': owner.last_name,
        'email': owner.email,
        'phone': owner.phone,
        'address': {
            'line1': owner.address_line1,
            'line2': owner.address_line2,
            'city': owner.city,
            'state_province': owner.state_province,
            'postal_code': owner.postal_code,
            'country': owner.country
        },
        'company_info': {
            'is_company': owner.is_company,
            'company_name': owner.company_name,
            'company_registration_number': owner.company_registration_number,
            'tax_id': owner.tax_id
        },
        'notes': owner.notes,
        'properties_count': owner.properties.count(),
        'created_at': owner.created_at.isoformat(),
        'updated_at': owner.updated_at.isoformat(),
        'created_by': owner.created_by
    }
    
    return jsonify(result), 200

@owners_bp.route('/', methods=['POST'])
@token_required
def create_owner_endpoint():
    """
    Endpoint pour créer un nouveau propriétaire.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Validation des données requises
    required_fields = []
    if data.get('is_company', False):
        required_fields.append('company_name')
    else:
        required_fields.extend(['first_name', 'last_name'])
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    try:
        # Création du propriétaire
        owner = create_owner(data, user.id)
        
        return jsonify({
            'message': 'Propriétaire créé avec succès',
            'owner': {
                'id': owner.id,
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'company_name': owner.company_name,
                'is_company': owner.is_company
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création du propriétaire: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la création du propriétaire'}), 500

@owners_bp.route('/<int:owner_id>', methods=['PUT'])
@token_required
def update_owner_endpoint(owner_id):
    """
    Endpoint pour mettre à jour un propriétaire existant.
    
    Args:
        owner_id (int): ID du propriétaire à mettre à jour
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    try:
        # Mise à jour du propriétaire
        owner = update_owner(owner_id, data)
        if not owner:
            return jsonify({'message': 'Propriétaire non trouvé'}), 404
        
        return jsonify({
            'message': 'Propriétaire mis à jour avec succès',
            'owner': {
                'id': owner.id,
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'company_name': owner.company_name,
                'is_company': owner.is_company
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour du propriétaire: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour du propriétaire'}), 500

@owners_bp.route('/<int:owner_id>', methods=['DELETE'])
@token_required
def delete_owner_endpoint(owner_id):
    """
    Endpoint pour supprimer un propriétaire.
    
    Args:
        owner_id (int): ID du propriétaire à supprimer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    try:
        # Suppression du propriétaire
        success = delete_owner(owner_id)
        if not success:
            return jsonify({'message': 'Propriétaire non trouvé'}), 404
        
        return jsonify({'message': 'Propriétaire supprimé avec succès'}), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression du propriétaire: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la suppression du propriétaire'}), 500

@owners_bp.route('/<int:owner_id>/properties', methods=['GET'])
def get_owner_properties_endpoint(owner_id):
    """
    Endpoint pour récupérer les biens immobiliers d'un propriétaire.
    
    Args:
        owner_id (int): ID du propriétaire
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Vérification de l'existence du propriétaire
    owner = get_owner_by_id(owner_id)
    if not owner:
        return jsonify({'message': 'Propriétaire non trouvé'}), 404
    
    # Récupération des paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Récupération des biens immobiliers
    properties, total_pages, total_items = get_owner_properties(owner_id, page, per_page)
    
    # Construction de la réponse
    result = {
        'properties': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        },
        'owner': {
            'id': owner.id,
            'first_name': owner.first_name,
            'last_name': owner.last_name,
            'company_name': owner.company_name,
            'is_company': owner.is_company
        }
    }
    
    # Formatage des biens immobiliers
    for prop in properties:
        result['properties'].append({
            'id': prop.id,
            'reference_code': prop.reference_code,
            'title': prop.title,
            'property_type': prop.property_type,
            'status': prop.status,
            'city': prop.city,
            'country': prop.country,
            'asking_price': float(prop.asking_price) if prop.asking_price else None,
            'rental_price': float(prop.rental_price) if prop.rental_price else None,
            'created_at': prop.created_at.isoformat()
        })
    
    return jsonify(result), 200
