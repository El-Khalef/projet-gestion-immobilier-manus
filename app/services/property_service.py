#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Services de gestion des biens immobiliers.
Ce fichier contient les fonctions métier liées aux biens immobiliers.
"""

from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

from app import db
from app.models.__init__1 import Property, PropertyImage, PropertyDocument, Amenity

def get_property_by_id(property_id):
    """
    Récupère un bien immobilier par son ID.
    
    Args:
        property_id (int): ID du bien immobilier à récupérer
        
    Returns:
        Property: Le bien immobilier trouvé ou None si non trouvé
    """
    return Property.query.get(property_id)

def get_property_by_reference(reference_code):
    """
    Récupère un bien immobilier par son code de référence.
    
    Args:
        reference_code (str): Code de référence du bien immobilier
        
    Returns:
        Property: Le bien immobilier trouvé ou None si non trouvé
    """
    return Property.query.filter_by(reference_code=reference_code).first()

def get_all_properties(filters=None, page=1, per_page=10):
    """
    Récupère tous les biens immobiliers avec pagination et filtrage optionnel.
    
    Args:
        filters (dict, optional): Filtres à appliquer
        page (int, optional): Numéro de page
        per_page (int, optional): Nombre d'éléments par page
        
    Returns:
        tuple: (Liste des biens immobiliers, nombre total de pages, nombre total d'éléments)
    """
    query = Property.query
    
    # Application des filtres
    if filters:
        if 'property_type' in filters:
            query = query.filter(Property.property_type == filters['property_type'])
        if 'status' in filters:
            query = query.filter(Property.status == filters['status'])
        if 'city' in filters:
            query = query.filter(Property.city.ilike(f"%{filters['city']}%"))
        if 'min_price' in filters:
            if filters.get('transaction_type') == 'rent':
                query = query.filter(Property.rental_price >= filters['min_price'])
            else:
                query = query.filter(Property.asking_price >= filters['min_price'])
        if 'max_price' in filters:
            if filters.get('transaction_type') == 'rent':
                query = query.filter(Property.rental_price <= filters['max_price'])
            else:
                query = query.filter(Property.asking_price <= filters['max_price'])
        if 'min_area' in filters:
            query = query.filter(Property.total_area >= filters['min_area'])
        if 'max_area' in filters:
            query = query.filter(Property.total_area <= filters['max_area'])
        if 'bedrooms' in filters:
            query = query.filter(Property.num_bedrooms >= filters['bedrooms'])
        if 'bathrooms' in filters:
            query = query.filter(Property.num_bathrooms >= filters['bathrooms'])
        if 'owner_id' in filters:
            query = query.filter(Property.owner_id == filters['owner_id'])
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return pagination.items, pagination.pages, pagination.total

def create_property(data, created_by):
    """
    Crée un nouveau bien immobilier.
    
    Args:
        data (dict): Données du bien immobilier
        created_by (int): ID de l'utilisateur créant le bien
        
    Returns:
        Property: Le bien immobilier créé
        
    Raises:
        ValueError: Si le code de référence existe déjà
    """
    # Vérification de l'unicité du code de référence
    if 'reference_code' in data and get_property_by_reference(data['reference_code']):
        raise ValueError(f"Le code de référence '{data['reference_code']}' existe déjà")
    
    # Génération d'un code de référence si non fourni
    if 'reference_code' not in data or not data['reference_code']:
        data['reference_code'] = generate_reference_code()
    
    # Création du bien immobilier
    property = Property(
        reference_code=data['reference_code'],
        title=data['title'],
        description=data.get('description', ''),
        property_type=data['property_type'],
        status=data['status'],
        address_line1=data['address_line1'],
        address_line2=data.get('address_line2', ''),
        city=data['city'],
        state_province=data.get('state_province', ''),
        postal_code=data['postal_code'],
        country=data['country'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        total_area=data['total_area'],
        living_area=data.get('living_area'),
        land_area=data.get('land_area'),
        num_bedrooms=data.get('num_bedrooms'),
        num_bathrooms=data.get('num_bathrooms'),
        num_floors=data.get('num_floors'),
        year_built=data.get('year_built'),
        energy_rating=data.get('energy_rating'),
        has_garage=data.get('has_garage', False),
        has_garden=data.get('has_garden', False),
        has_terrace=data.get('has_terrace', False),
        has_pool=data.get('has_pool', False),
        is_furnished=data.get('is_furnished', False),
        asking_price=data.get('asking_price'),
        rental_price=data.get('rental_price'),
        created_by=created_by,
        owner_id=data['owner_id']
    )
    
    # Ajout des équipements si fournis
    if 'amenities' in data and data['amenities']:
        for amenity_id in data['amenities']:
            amenity = Amenity.query.get(amenity_id)
            if amenity:
                property.amenities.append(amenity)
    
    # Sauvegarde dans la base de données
    db.session.add(property)
    db.session.commit()
    
    return property

def update_property(property_id, data):
    """
    Met à jour un bien immobilier existant.
    
    Args:
        property_id (int): ID du bien immobilier à mettre à jour
        data (dict): Données à mettre à jour
        
    Returns:
        Property: Le bien immobilier mis à jour ou None si non trouvé
        
    Raises:
        ValueError: Si le code de référence existe déjà pour un autre bien
    """
    property = get_property_by_id(property_id)
    if not property:
        return None
    
    # Vérification de l'unicité du code de référence
    if 'reference_code' in data and data['reference_code'] != property.reference_code:
        existing_property = get_property_by_reference(data['reference_code'])
        if existing_property:
            raise ValueError(f"Le code de référence '{data['reference_code']}' existe déjà")
    
    # Mise à jour des attributs
    for key, value in data.items():
        if key == 'amenities':
            # Gestion spéciale pour les équipements
            if value:
                # Suppression des équipements existants
                property.amenities = []
                # Ajout des nouveaux équipements
                for amenity_id in value:
                    amenity = Amenity.query.get(amenity_id)
                    if amenity:
                        property.amenities.append(amenity)
        elif hasattr(property, key):
            setattr(property, key, value)
    
    # Mise à jour de la date de modification
    property.updated_at = datetime.utcnow()
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return property

def delete_property(property_id):
    """
    Supprime un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier à supprimer
        
    Returns:
        bool: True si le bien a été supprimé, False sinon
    """
    property = get_property_by_id(property_id)
    if not property:
        return False
    
    db.session.delete(property)
    db.session.commit()
    
    return True

def add_property_image(property_id, image_file, is_primary=False, title=None, description=None, uploaded_by=None):
    """
    Ajoute une image à un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        image_file (FileStorage): Fichier image
        is_primary (bool, optional): Indique si c'est l'image principale
        title (str, optional): Titre de l'image
        description (str, optional): Description de l'image
        uploaded_by (int, optional): ID de l'utilisateur ayant uploadé l'image
        
    Returns:
        PropertyImage: L'image ajoutée ou None si le bien n'existe pas
        
    Raises:
        ValueError: Si le fichier n'est pas une image valide
    """
    property = get_property_by_id(property_id)
    if not property:
        return None
    
    # Vérification du type de fichier
    filename = secure_filename(image_file.filename)
    if not allowed_file(filename, ['jpg', 'jpeg', 'png', 'gif']):
        raise ValueError("Type de fichier non autorisé. Seuls les formats JPG, JPEG, PNG et GIF sont acceptés.")
    
    # Génération d'un nom de fichier unique
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Création du dossier de destination s'il n'existe pas
    upload_folder = os.path.join('app', 'static', 'uploads', 'properties', str(property_id))
    os.makedirs(upload_folder, exist_ok=True)
    
    # Chemin complet du fichier
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Sauvegarde du fichier
    image_file.save(file_path)
    
    # Si c'est l'image principale, mettre à jour les autres images
    if is_primary:
        for image in property.images:
            image.is_primary = False
    
    # Création de l'enregistrement dans la base de données
    image = PropertyImage(
        property_id=property_id,
        file_path=file_path,
        file_name=unique_filename,
        file_size=os.path.getsize(file_path),
        file_type=image_file.content_type,
        is_primary=is_primary,
        display_order=get_next_display_order(property_id),
        title=title,
        description=description,
        uploaded_by=uploaded_by
    )
    
    db.session.add(image)
    db.session.commit()
    
    return image

def add_property_document(property_id, document_file, document_type, title=None, description=None, expiry_date=None, uploaded_by=None):
    """
    Ajoute un document à un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        document_file (FileStorage): Fichier document
        document_type (str): Type de document
        title (str, optional): Titre du document
        description (str, optional): Description du document
        expiry_date (date, optional): Date d'expiration du document
        uploaded_by (int, optional): ID de l'utilisateur ayant uploadé le document
        
    Returns:
        PropertyDocument: Le document ajouté ou None si le bien n'existe pas
        
    Raises:
        ValueError: Si le fichier n'est pas un document valide
    """
    property = get_property_by_id(property_id)
    if not property:
        return None
    
    # Vérification du type de fichier
    filename = secure_filename(document_file.filename)
    if not allowed_file(filename, ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt']):
        raise ValueError("Type de fichier non autorisé. Seuls les formats PDF, DOC, DOCX, XLS, XLSX et TXT sont acceptés.")
    
    # Génération d'un nom de fichier unique
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Création du dossier de destination s'il n'existe pas
    upload_folder = os.path.join('app', 'static', 'uploads', 'documents', str(property_id))
    os.makedirs(upload_folder, exist_ok=True)
    
    # Chemin complet du fichier
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Sauvegarde du fichier
    document_file.save(file_path)
    
    # Création de l'enregistrement dans la base de données
    document = PropertyDocument(
        property_id=property_id,
        document_type=document_type,
        file_path=file_path,
        file_name=unique_filename,
        file_size=os.path.getsize(file_path),
        file_type=document_file.content_type,
        title=title,
        description=description,
        expiry_date=expiry_date,
        uploaded_by=uploaded_by
    )
    
    db.session.add(document)
    db.session.commit()
    
    return document

def get_property_images(property_id):
    """
    Récupère toutes les images d'un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        
    Returns:
        list: Liste des images du bien
    """
    property = get_property_by_id(property_id)
    if not property:
        return []
    
    return property.images.order_by(PropertyImage.display_order).all()

def get_property_documents(property_id):
    """
    Récupère tous les documents d'un bien immobilier.
    
    Args:
        property_id (int): ID du bien immobilier
        
    Returns:
        list: Liste des documents du bien
    """
    property = get_property_by_id(property_id)
    if not property:
        return []
    
    return property.documents.all()

def get_all_amenities():
    """
    Récupère tous les équipements disponibles.
    
    Returns:
        list: Liste de tous les équipements
    """
    return Amenity.query.all()

def create_amenity(name, category=None, description=None):
    """
    Crée un nouvel équipement.
    
    Args:
        name (str): Nom de l'équipement
        category (str, optional): Catégorie de l'équipement
        description (str, optional): Description de l'équipement
        
    Returns:
        Amenity: L'équipement créé
    """
    amenity = Amenity(
        name=name,
        category=category,
        description=description
    )
    
    db.session.add(amenity)
    db.session.commit()
    
    return amenity

# Fonctions utilitaires

def generate_reference_code():
    """
    Génère un code de référence unique pour un bien immobilier.
    
    Returns:
        str: Code de référence unique
    """
    # Format: PROP-YYYYMMDD-XXXX où XXXX est un nombre aléatoire
    today = datetime.now().strftime('%Y%m%d')
    random_part = uuid.uuid4().hex[:4].upper()
    
    reference_code = f"PROP-{today}-{random_part}"
    
    # Vérification de l'unicité
    while get_property_by_reference(reference_code):
        random_part = uuid.uuid4().hex[:4].upper()
        reference_code = f"PROP-{today}-{random_part}"
    
    return reference_code

def allowed_file(filename, allowed_extensions):
    """
    Vérifie si le fichier a une extension autorisée.
    
    Args:
        filename (str): Nom du fichier
        allowed_extensions (list): Liste des extensions autorisées
        
    Returns:
        bool: True si l'extension est autorisée, False sinon
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_next_display_order(property_id):
    """
    Récupère le prochain ordre d'affichage pour une image.
    
    Args:
        property_id (int): ID du bien immobilier
        
    Returns:
        int: Prochain ordre d'affichage
    """
    max_order = db.session.query(db.func.max(PropertyImage.display_order)).filter_by(property_id=property_id).scalar()
    return (max_order or 0) + 1
