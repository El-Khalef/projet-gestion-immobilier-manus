#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Routes de gestion des biens immobiliers.
Ce fichier définit les endpoints API pour la gestion des biens immobiliers.
"""

from flask import Blueprint, request, jsonify, current_app, g, url_for
from werkzeug.utils import secure_filename
import os

from app.routes.old_auth import token_required
from app.models.__init__1 import Property, PropertyImage, PropertyDocument, Amenity
from app.services.property_service import (
    get_property_by_id, get_property_by_reference, get_all_properties,
    create_property, update_property, delete_property,
    add_property_image, add_property_document,
    get_property_images, get_property_documents,
    get_all_amenities, create_amenity
)

properties_bp = Blueprint('properties', __name__, url_prefix='/api/properties')

@properties_bp.route('/', methods=['GET'])
def get_properties():
    """
    Endpoint pour récupérer la liste des biens immobiliers avec pagination et filtrage.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    # Récupération des paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Récupération des filtres
    filters = {}
    filter_params = [
        'property_type', 'status', 'city', 'min_price', 'max_price',
        'min_area', 'max_area', 'bedrooms', 'bathrooms', 'owner_id',
        'transaction_type'
    ]
    
    for param in filter_params:
        value = request.args.get(param)
        if value:
            # Conversion des valeurs numériques
            if param in ['min_price', 'max_price', 'min_area', 'max_area', 'bedrooms', 'bathrooms', 'owner_id']:
                try:
                    value = float(value) if 'price' in param or 'area' in param else int(value)
                except ValueError:
                    continue
            filters[param] = value
    
    # Récupération des biens immobiliers
    properties, total_pages, total_items = get_all_properties(filters, page, per_page)
    
    # Construction de la réponse
    result = {
        'properties': [],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        }
    }
    
    # Formatage des biens immobiliers
    for prop in properties:
        primary_image = None
        primary_image_obj = prop.images.filter_by(is_primary=True).first() or prop.images.first()
        if primary_image_obj:
            primary_image = url_for('static', filename=primary_image_obj.file_path.replace('app/static/', ''), _external=True)
        
        result['properties'].append({
            'id': prop.id,
            'reference_code': prop.reference_code,
            'title': prop.title,
            'property_type': prop.property_type,
            'status': prop.status,
            'city': prop.city,
            'postal_code': prop.postal_code,
            'country': prop.country,
            'total_area': float(prop.total_area) if prop.total_area else None,
            'num_bedrooms': prop.num_bedrooms,
            'num_bathrooms': prop.num_bathrooms,
            'asking_price': float(prop.asking_price) if prop.asking_price else None,
            'rental_price': float(prop.rental_price) if prop.rental_price else None,
            'primary_image': primary_image,
            'created_at': prop.created_at.isoformat()
        })
    
    return jsonify(result), 200

@properties_bp.route('/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """
    Endpoint pour récupérer un bien immobilier spécifique.
    
    Args:
        property_id (int): ID du bien immobilier à récupérer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    prop = get_property_by_id(property_id)
    if not prop:
        return jsonify({'message': 'Bien immobilier non trouvé'}), 404
    
    # Récupération des images
    images = []
    for img in get_property_images(property_id):
        images.append({
            'id': img.id,
            'url': url_for('static', filename=img.file_path.replace('app/static/', ''), _external=True),
            'is_primary': img.is_primary,
            'title': img.title,
            'description': img.description
        })
    
    # Récupération des documents
    documents = []
    for doc in get_property_documents(property_id):
        documents.append({
            'id': doc.id,
            'document_type': doc.document_type,
            'url': url_for('static', filename=doc.file_path.replace('app/static/', ''), _external=True),
            'title': doc.title,
            'description': doc.description,
            'expiry_date': doc.expiry_date.isoformat() if doc.expiry_date else None
        })
    
    # Récupération des équipements
    amenities = [{
        'id': amenity.id,
        'name': amenity.name,
        'category': amenity.category
    } for amenity in prop.amenities]
    
    # Construction de la réponse détaillée
    result = {
        'id': prop.id,
        'reference_code': prop.reference_code,
        'title': prop.title,
        'description': prop.description,
        'property_type': prop.property_type,
        'status': prop.status,
        'address': {
            'line1': prop.address_line1,
            'line2': prop.address_line2,
            'city': prop.city,
            'state_province': prop.state_province,
            'postal_code': prop.postal_code,
            'country': prop.country,
            'latitude': float(prop.latitude) if prop.latitude else None,
            'longitude': float(prop.longitude) if prop.longitude else None
        },
        'features': {
            'total_area': float(prop.total_area) if prop.total_area else None,
            'living_area': float(prop.living_area) if prop.living_area else None,
            'land_area': float(prop.land_area) if prop.land_area else None,
            'num_bedrooms': prop.num_bedrooms,
            'num_bathrooms': prop.num_bathrooms,
            'num_floors': prop.num_floors,
            'year_built': prop.year_built,
            'energy_rating': prop.energy_rating,
            'has_garage': prop.has_garage,
            'has_garden': prop.has_garden,
            'has_terrace': prop.has_terrace,
            'has_pool': prop.has_pool,
            'is_furnished': prop.is_furnished
        },
        'pricing': {
            'asking_price': float(prop.asking_price) if prop.asking_price else None,
            'rental_price': float(prop.rental_price) if prop.rental_price else None
        },
        'owner_id': prop.owner_id,
        'created_by': prop.created_by,
        'created_at': prop.created_at.isoformat(),
        'updated_at': prop.updated_at.isoformat(),
        'images': images,
        'documents': documents,
        'amenities': amenities
    }
    
    return jsonify(result), 200

@properties_bp.route('/', methods=['POST'])
@token_required
def create_property_endpoint():
    """
    Endpoint pour créer un nouveau bien immobilier.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Validation des données requises
    required_fields = ['title', 'property_type', 'status', 'address_line1', 'city', 'postal_code', 'country', 'total_area', 'owner_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    try:
        # Création du bien immobilier
        property = create_property(data, user.id)
        
        return jsonify({
            'message': 'Bien immobilier créé avec succès',
            'property': {
                'id': property.id,
                'reference_code': property.reference_code,
                'title': property.title
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création du bien immobilier: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la création du bien immobilier'}), 500

@properties_bp.route('/<int:property_id>', methods=['PUT'])
@token_required
def update_property_endpoint(property_id):
    """
    Endpoint pour mettre à jour un bien immobilier existant.
    
    Args:
        property_id (int): ID du bien immobilier à mettre à jour
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    try:
        # Mise à jour du bien immobilier
        property = update_property(property_id, data)
        if not property:
            return jsonify({'message': 'Bien immobilier non trouvé'}), 404
        
        return jsonify({
            'message': 'Bien immobilier mis à jour avec succès',
            'property': {
                'id': property.id,
                'reference_code': property.reference_code,
                'title': property.title
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour du bien immobilier: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour du bien immobilier'}), 500

@properties_bp.route('/<int:property_id>', methods=['DELETE'])
@token_required
def delete_property_endpoint(property_id):
    """
    Endpoint pour supprimer un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier à supprimer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    # Vérification des droits (admin ou créateur)
    property = get_property_by_id(property_id)
    if not property:
        return jsonify({'message': 'Bien immobilier non trouvé'}), 404
    
    if user.role != 'admin' and property.created_by != user.id:
        return jsonify({'message': 'Vous n\'êtes pas autorisé à supprimer ce bien immobilier'}), 403
    
    success = delete_property(property_id)
    if not success:
        return jsonify({'message': 'Bien immobilier non trouvé'}), 404
    
    return jsonify({'message': 'Bien immobilier supprimé avec succès'}), 200

@properties_bp.route('/<int:property_id>/images', methods=['POST'])
@token_required
def add_property_image_endpoint(property_id):
    """
    Endpoint pour ajouter une image à un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    # Vérification de la présence du fichier
    if 'image' not in request.files:
        return jsonify({'message': 'Aucun fichier image fourni'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'message': 'Aucun fichier image sélectionné'}), 400
    
    # Récupération des paramètres
    is_primary = request.form.get('is_primary', 'false').lower() == 'true'
    title = request.form.get('title')
    description = request.form.get('description')
    
    try:
        # Ajout de l'image
        image = add_property_image(property_id, image_file, is_primary, title, description, user.id)
        if not image:
            return jsonify({'message': 'Bien immobilier non trouvé'}), 404
        
        return jsonify({
            'message': 'Image ajoutée avec succès',
            'image': {
                'id': image.id,
                'url': url_for('static', filename=image.file_path.replace('app/static/', ''), _external=True),
                'is_primary': image.is_primary,
                'title': image.title
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'ajout de l'image: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de l\'ajout de l\'image'}), 500

@properties_bp.route('/<int:property_id>/documents', methods=['POST'])
@token_required
def add_property_document_endpoint(property_id):
    """
    Endpoint pour ajouter un document à un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    # Vérification de la présence du fichier
    if 'document' not in request.files:
        return jsonify({'message': 'Aucun fichier document fourni'}), 400
    
    document_file = request.files['document']
    if document_file.filename == '':
        return jsonify({'message': 'Aucun fichier document sélectionné'}), 400
    
    # Vérification de la présence du type de document
    if 'document_type' not in request.form:
        return jsonify({'message': 'Le type de document est requis'}), 400
    
    # Récupération des paramètres
    document_type = request.form['document_type']
    title = request.form.get('title')
    description = request.form.get('description')
    expiry_date = request.form.get('expiry_date')
    
    try:
        # Ajout du document
        document = add_property_document(property_id, document_file, document_type, title, description, expiry_date, user.id)
        if not document:
            return jsonify({'message': 'Bien immobilier non trouvé'}), 404
        
        return jsonify({
            'message': 'Document ajouté avec succès',
            'document': {
                'id': document.id,
                'url': url_for('static', filename=document.file_path.replace('app/static/', ''), _external=True),
                'document_type': document.document_type,
                'title': document.title
            }
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'ajout du document: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de l\'ajout du document'}), 500

@properties_bp.route('/amenities', methods=['GET'])
def get_amenities():
    """
    Endpoint pour récupérer la liste des équipements disponibles.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    amenities = get_all_amenities()
    
    result = [{
        'id': amenity.id,
        'name': amenity.name,
        'category': amenity.category,
        'description': amenity.description
    } for amenity in amenities]
    
    return jsonify({'amenities': result}), 200

@properties_bp.route('/amenities', methods=['POST'])
@token_required
def create_amenity_endpoint():
    """
    Endpoint pour créer un nouvel équipement.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    # Vérification des droits d'administrateur
    if user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    
    # Validation des données requises
    if 'name' not in data:
        return jsonify({'message': 'Le nom de l\'équipement est requis'}), 400
    
    try:
        # Création de l'équipement
        amenity = create_amenity(data['name'], data.get('category'), data.get('description'))
        
        return jsonify({
            'message': 'Équipement créé avec succès',
            'amenity': {
                'id': amenity.id,
                'name': amenity.name,
                'category': amenity.category,
                'description': amenity.description
            }
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création de l'équipement: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la création de l\'équipement'}), 500

@properties_bp.route('/reference/<reference_code>', methods=['GET'])
def get_property_by_reference_endpoint(reference_code):
    """
    Endpoint pour récupérer un bien immobilier par son code de référence.
    
    Args:
        reference_code (str): Code de référence du bien immobilier
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    prop = get_property_by_reference(reference_code)
    if not prop:
        return jsonify({'message': 'Bien immobilier non trouvé'}), 404
    
    # Redirection vers l'endpoint détaillé
    return get_property(prop.id)
