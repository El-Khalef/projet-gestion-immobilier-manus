#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Services d'authentification et de gestion des utilisateurs.
Ce fichier contient les fonctions métier liées à l'authentification et aux utilisateurs.
"""

from datetime import datetime, timedelta
import jwt
from flask import current_app
from werkzeug.security import generate_password_hash

from app import db
from app.models.__init__1 import User

def get_user_by_id(user_id):
    """
    Récupère un utilisateur par son ID.
    
    Args:
        user_id (int): ID de l'utilisateur à récupérer
        
    Returns:
        User: L'utilisateur trouvé ou None si non trouvé
    """
    return User.query.get(user_id)

def get_user_by_username(username):
    """
    Récupère un utilisateur par son nom d'utilisateur.
    
    Args:
        username (str): Nom d'utilisateur à rechercher
        
    Returns:
        User: L'utilisateur trouvé ou None si non trouvé
    """
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """
    Récupère un utilisateur par son email.
    
    Args:
        email (str): Email à rechercher
        
    Returns:
        User: L'utilisateur trouvé ou None si non trouvé
    """
    return User.query.filter_by(email=email).first()

def get_all_users():
    """
    Récupère tous les utilisateurs.
    
    Returns:
        list: Liste de tous les utilisateurs
    """
    return User.query.all()

def create_user(username, email, password, first_name=None, last_name=None, role='user'):
    """
    Crée un nouvel utilisateur.
    
    Args:
        username (str): Nom d'utilisateur
        email (str): Email
        password (str): Mot de passe
        first_name (str, optional): Prénom
        last_name (str, optional): Nom de famille
        role (str, optional): Rôle de l'utilisateur
        
    Returns:
        User: L'utilisateur créé
        
    Raises:
        ValueError: Si le nom d'utilisateur ou l'email existe déjà
    """
    # Vérification de l'unicité du nom d'utilisateur et de l'email
    if get_user_by_username(username):
        raise ValueError(f"Le nom d'utilisateur '{username}' existe déjà")
    
    if get_user_by_email(email):
        raise ValueError(f"L'email '{email}' existe déjà")
    
    # Création de l'utilisateur
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role
    )
    user.password = password  # Utilise le setter qui hash le mot de passe
    
    # Sauvegarde dans la base de données
    db.session.add(user)
    db.session.commit()
    
    return user

def update_user(user_id, **kwargs):
    """
    Met à jour un utilisateur existant.
    
    Args:
        user_id (int): ID de l'utilisateur à mettre à jour
        **kwargs: Attributs à mettre à jour (username, email, first_name, last_name, role, is_active)
        
    Returns:
        User: L'utilisateur mis à jour ou None si non trouvé
        
    Raises:
        ValueError: Si le nom d'utilisateur ou l'email existe déjà pour un autre utilisateur
    """
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    # Vérification de l'unicité du nom d'utilisateur et de l'email
    if 'username' in kwargs and kwargs['username'] != user.username:
        existing_user = get_user_by_username(kwargs['username'])
        if existing_user:
            raise ValueError(f"Le nom d'utilisateur '{kwargs['username']}' existe déjà")
    
    if 'email' in kwargs and kwargs['email'] != user.email:
        existing_user = get_user_by_email(kwargs['email'])
        if existing_user:
            raise ValueError(f"L'email '{kwargs['email']}' existe déjà")
    
    # Mise à jour du mot de passe si fourni
    if 'password' in kwargs:
        user.password = kwargs.pop('password')
    
    # Mise à jour des autres attributs
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    # Mise à jour de la date de modification
    user.updated_at = datetime.utcnow()
    
    # Sauvegarde dans la base de données
    db.session.commit()
    
    return user

def delete_user(user_id):
    """
    Supprime un utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur à supprimer
        
    Returns:
        bool: True si l'utilisateur a été supprimé, False sinon
    """
    user = get_user_by_id(user_id)
    if not user:
        return False
    
    db.session.delete(user)
    db.session.commit()
    
    return True

def generate_auth_token(user_id, expiration=3600):
    """
    Génère un token JWT pour l'authentification.
    
    Args:
        user_id (int): ID de l'utilisateur
        expiration (int, optional): Durée de validité du token en secondes
        
    Returns:
        str: Token JWT encodé
    """
    payload = {
        'exp': datetime.utcnow() + timedelta(seconds=expiration),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )

def verify_auth_token(token):
    """
    Vérifie un token JWT et retourne l'utilisateur correspondant.
    
    Args:
        token (str): Token JWT à vérifier
        
    Returns:
        User: L'utilisateur correspondant au token ou None si invalide
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=['HS256']
        )
        return User.query.get(payload['sub'])
    except jwt.ExpiredSignatureError:
        # Token expiré
        return None
    except jwt.InvalidTokenError:
        # Token invalide
        return None
