#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Routes de gestion des clients.
Ce fichier définit les endpoints API pour la gestion des clients (acheteurs/locataires).
"""

from flask import Blueprint, request, jsonify, current_app, g, url_for
from datetime import datetime

from app.routes.old_auth import token_required
from app.models.__init__1 import Client, PropertyVisit
from app.services.client_service import (
    get_client_by_id, get_all_clients, create_client, update_client, delete_client,
    add_property_interest, remove_property_interest, get_client_interested_properties,
    schedule_property_visit, update_property_visit, get_client_visits
)

clients_bp = Blueprint('clients', __name__, url_prefix='/api/clients')

@clients_bp.route('/', methods=['GET'])
def get_clients():
    """
    Endpoint pour récupérer la liste des clients avec pagination et filtrage.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Récupération des paramètres de pagination et filtrage
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search')
    client_type = request.args.get('client_type')
    assigned_agent_id = request.args.get('assigned_agent_id', type=int)
    
    # Récupération des clients
    clients, total_pages, total_items = get_all_clients(page, per_page, search, client_type, assigned_agent_id)
    
    # Construction de la réponse
    result = {
        'clients': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        }
    }
    
    # Formatage des clients
    for client in clients:
        result['clients'].append({
            'id': client.id,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'email': client.email,
            'phone': client.phone,
            'city': client.city,
            'country': client.country,
            'client_type': client.client_type,
            'budget_range': client.get_budget_range(),
            'assigned_agent_id': client.assigned_agent_id,
            'created_at': client.created_at.isoformat()
        })
    
    return jsonify(result), 200

@clients_bp.route('/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """
    Endpoint pour récupérer un client spécifique.
    
    Args:
        client_id (int): ID du client à récupérer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    client = get_client_by_id(client_id)
    if not client:
        return jsonify({'message': 'Client non trouvé'}), 404
    
    # Construction de la réponse détaillée
    result = {
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'email': client.email,
        'phone': client.phone,
        'address': {
            'line1': client.address_line1,
            'line2': client.address_line2,
            'city': client.city,
            'state_province': client.state_province,
            'postal_code': client.postal_code,
            'country': client.country
        },
        'client_type': client.client_type,
        'budget': {
            'min': float(client.budget_min) if client.budget_min else None,
            'max': float(client.budget_max) if client.budget_max else None,
            'formatted': client.get_budget_range()
        },
        'requirements': client.requirements,
        'notes': client.notes,
        'assigned_agent_id': client.assigned_agent_id,
        'created_at': client.created_at.isoformat(),
        'updated_at': client.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@clients_bp.route('/', methods=['POST'])
@token_required
def create_client_endpoint():
    """
    Endpoint pour créer un nouveau client.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Validation des données requises
    required_fields = ['first_name', 'last_name', 'client_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    try:
        # Création du client
        client = create_client(data, user.id)
        
        return jsonify({
            'message': 'Client créé avec succès',
            'client': {
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'client_type': client.client_type
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création du client: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la création du client'}), 500

@clients_bp.route('/<int:client_id>', methods=['PUT'])
@token_required
def update_client_endpoint(client_id):
    """
    Endpoint pour mettre à jour un client existant.
    
    Args:
        client_id (int): ID du client à mettre à jour
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    try:
        # Mise à jour du client
        client = update_client(client_id, data)
        if not client:
            return jsonify({'message': 'Client non trouvé'}), 404
        
        return jsonify({
            'message': 'Client mis à jour avec succès',
            'client': {
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'client_type': client.client_type
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour du client: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour du client'}), 500

@clients_bp.route('/<int:client_id>', methods=['DELETE'])
@token_required
def delete_client_endpoint(client_id):
    """
    Endpoint pour supprimer un client.
    
    Args:
        client_id (int): ID du client à supprimer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    try:
        # Suppression du client
        success = delete_client(client_id)
        if not success:
            return jsonify({'message': 'Client non trouvé'}), 404
        
        return jsonify({'message': 'Client supprimé avec succès'}), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression du client: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la suppression du client'}), 500

@clients_bp.route('/<int:client_id>/interests', methods=['GET'])
def get_client_interests(client_id):
    """
    Endpoint pour récupérer les biens immobiliers qui intéressent un client.
    
    Args:
        client_id (int): ID du client
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Vérification de l'existence du client
    client = get_client_by_id(client_id)
    if not client:
        return jsonify({'message': 'Client non trouvé'}), 404
    
    # Récupération des paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Récupération des biens immobiliers
    properties, total_pages, total_items = get_client_interested_properties(client_id, page, per_page)
    
    # Construction de la réponse
    result = {
        'properties': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        },
        'client': {
            'id': client.id,
            'first_name': client.first_name,
            'last_name': client.last_name
        }
    }
    
    # Formatage des biens immobiliers
    for prop in properties:
        # Récupération du niveau d'intérêt depuis la table de jointure
        interest_level = None
        notes = None
        for interest in client.interested_properties:
            if interest.id == prop.id:
                # Accès aux attributs de la table de jointure
                interest_data = db.session.execute(
                    db.text("SELECT interest_level, notes FROM client_property_interests WHERE client_id = :client_id AND property_id = :property_id"),
                    {"client_id": client.id, "property_id": prop.id}
                ).fetchone()
                if interest_data:
                    interest_level = interest_data[0]
                    notes = interest_data[1]
                break
        
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
            'interest_level': interest_level,
            'notes': notes
        })
    
    return jsonify(result), 200

@clients_bp.route('/<int:client_id>/interests/<int:property_id>', methods=['POST'])
@token_required
def add_client_interest(client_id, property_id):
    """
    Endpoint pour ajouter un intérêt d'un client pour un bien immobilier.
    
    Args:
        client_id (int): ID du client
        property_id (int): ID du bien immobilier
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    data = request.get_json()
    
    # Validation des données requises
    if 'interest_level' not in data:
        return jsonify({'message': 'Le niveau d\'intérêt est requis'}), 400
    
    try:
        # Ajout de l'intérêt
        success = add_property_interest(client_id, property_id, data['interest_level'], data.get('notes'))
        if not success:
            return jsonify({'message': 'Client ou bien immobilier non trouvé'}), 404
        
        return jsonify({'message': 'Intérêt ajouté avec succès'}), 201
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'ajout de l'intérêt: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de l\'ajout de l\'intérêt'}), 500

@clients_bp.route('/<int:client_id>/interests/<int:property_id>', methods=['DELETE'])
@token_required
def remove_client_interest(client_id, property_id):
    """
    Endpoint pour supprimer l'intérêt d'un client pour un bien immobilier.
    
    Args:
        client_id (int): ID du client
        property_id (int): ID du bien immobilier
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    try:
        # Suppression de l'intérêt
        success = remove_property_interest(client_id, property_id)
        if not success:
            return jsonify({'message': 'Client ou bien immobilier non trouvé'}), 404
        
        return jsonify({'message': 'Intérêt supprimé avec succès'}), 200
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression de l'intérêt: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la suppression de l\'intérêt'}), 500

@clients_bp.route('/<int:client_id>/visits', methods=['GET'])
def get_client_visits_endpoint(client_id):
    """
    Endpoint pour récupérer les visites d'un client.
    
    Args:
        client_id (int): ID du client
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Vérification de l'existence du client
    client = get_client_by_id(client_id)
    if not client:
        return jsonify({'message': 'Client non trouvé'}), 404
    
    # Récupération des paramètres de pagination et filtrage
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    # Récupération des visites
    visits, total_pages, total_items = get_client_visits(client_id, page, per_page, status)
    
    # Construction de la réponse
    result = {
        'visits': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        },
        'client': {
            'id': client.id,
            'first_name': client.first_name,
            'last_name': client.last_name
        }
    }
    
    # Formatage des visites
    for visit in visits:
        result['visits'].append({
            'id': visit.id,
            'property_id': visit.property_id,
            'property_title': visit.property.title if visit.property else None,
            'visit_date': visit.visit_date.isoformat(),
            'duration': visit.duration,
            'status': visit.status,
            'feedback': visit.feedback,
            'interest_level': visit.interest_level,
            'accompanied_by': visit.accompanied_by,
            'notes': visit.notes,
            'created_at': visit.created_at.isoformat()
        })
    
    return jsonify(result), 200

@clients_bp.route('/<int:client_id>/visits', methods=['POST'])
@token_required
def schedule_visit(client_id):
    """
    Endpoint pour planifier une visite de bien immobilier pour un client.
    
    Args:
        client_id (int): ID du client
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Validation des données requises
    required_fields = ['property_id', 'visit_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    try:
        # Conversion de la date de visite
        visit_date = datetime.fromisoformat(data['visit_date'])
        
        # Planification de la visite
        visit = schedule_property_visit(
            client_id,
            data['property_id'],
            visit_date,
            data.get('duration', 60),
            data.get('accompanied_by', user.id),
            data.get('notes')
        )
        
        if not visit:
            return jsonify({'message': 'Client ou bien immobilier non trouvé'}), 404
        
        return jsonify({
            'message': 'Visite planifiée avec succès',
            'visit': {
                'id': visit.id,
                'property_id': visit.property_id,
                'visit_date': visit.visit_date.isoformat(),
                'status': visit.status
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la planification de la visite: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la planification de la visite'}), 500

@clients_bp.route('/<int:client_id>/visits/<int:visit_id>', methods=['PUT'])
@token_required
def update_visit(client_id, visit_id):
    """
    Endpoint pour mettre à jour une visite de bien immobilier.
    
    Args:
        client_id (int): ID du client
        visit_id (int): ID de la visite
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    data = request.get_json()
    
    # Vérification que la visite appartient au client
    visit = PropertyVisit.query.get(visit_id)
    if not visit or visit.client_id != client_id:
        return jsonify({'message': 'Visite non trouvée ou n\'appartient pas au client'}), 404
    
    try:
        # Conversion de la date de visite si fournie
        if 'visit_date' in data:
            data['visit_date'] = datetime.fromisoformat(data['visit_date'])
        
        # Mise à jour de la visite
        updated_visit = update_property_visit(visit_id, data)
        
        return jsonify({
            'message': 'Visite mise à jour avec succès',
            'visit': {
                'id': updated_visit.id,
                'property_id': updated_visit.property_id,
                'visit_date': updated_visit.visit_date.isoformat(),
                'status': updated_visit.status,
                'feedback': updated_visit.feedback,
                'interest_level': updated_visit.interest_level
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour de la visite: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour de la visite'}), 500
