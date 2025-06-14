#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module d'initialisation des services.
Ce fichier permet d'importer facilement tous les services de l'application.
"""

from app.services.auth_service import *
from app.services.property_service import *
from app.services.owner_service import *
from app.services.client_service import *
from app.services.transaction_service import *






#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mise à jour du module services pour importer tous les services.
Ce fichier importe tous les services pour les rendre disponibles via app.services.
"""

from app.services.auth_service import (
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    get_all_users,
    create_user,
    update_user,
    delete_user,
    generate_auth_token,
    verify_auth_token
)

from app.services.property_service import (
    get_property_by_id,
    get_property_by_reference,
    get_all_properties,
    create_property,
    update_property,
    delete_property,
    add_property_image,
    add_property_document,
    get_property_images,
    get_property_documents,
    get_all_amenities,
    create_amenity
)

# Définition des services disponibles pour l'importation
__all__ = [
    # Services d'authentification
    'get_user_by_id',
    'get_user_by_username',
    'get_user_by_email',
    'get_all_users',
    'create_user',
    'update_user',
    'delete_user',
    'generate_auth_token',
    'verify_auth_token',
    
    # Services de gestion des biens immobiliers
    'get_property_by_id',
    'get_property_by_reference',
    'get_all_properties',
    'create_property',
    'update_property',
    'delete_property',
    'add_property_image',
    'add_property_document',
    'get_property_images',
    'get_property_documents',
    'get_all_amenities',
    'create_amenity'
]



