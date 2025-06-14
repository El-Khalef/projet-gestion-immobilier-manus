#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Routes d'authentification et de gestion des utilisateurs.
Ce fichier définit les endpoints API pour l'authentification et la gestion des utilisateurs.
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_login import login_user, logout_user, login_required, current_user
import jwt
from functools import wraps

from app import db
# Correction de l'import problématique
from app.models.user import User
from app.services.auth_service import (
    get_user_by_id, get_user_by_username, get_user_by_email, get_all_users,
    create_user, update_user, delete_user, generate_auth_token, verify_auth_token
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def token_required(f):
    """
    Décorateur pour vérifier le token JWT dans les requêtes.
    
    Args:
        f: La fonction à décorer
        
    Returns:
        function: La fonction décorée
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupération du token depuis l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        
        # Vérification du token
        user = verify_auth_token(token)
        if not user:
            return jsonify({'message': 'Token invalide ou expiré'}), 401
        
        # Stockage de l'utilisateur dans le contexte global
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint pour l'inscription d'un nouvel utilisateur.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    data = request.get_json()
    
    # Validation des données requises
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Le champ {field} est requis'}), 400
    
    # Vérification de l'unicité du nom d'utilisateur et de l'email
    if get_user_by_username(data['username']):
        return jsonify({'message': f'Le nom d\'utilisateur {data["username"]} existe déjà'}), 400
    
    if get_user_by_email(data['email']):
        return jsonify({'message': f'L\'email {data["email"]} existe déjà'}), 400
    
    try:
        # Création de l'utilisateur
        user = create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'user')
        )
        
        # Génération du token d'authentification
        token = generate_auth_token(user.id)
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            },
            'token': token
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'inscription: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de l\'inscription'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint pour la connexion d'un utilisateur.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    data = request.get_json()
    
    # Validation des données requises
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Nom d\'utilisateur et mot de passe requis'}), 400
    
    # Récupération de l'utilisateur
    user = get_user_by_username(data['username'])
    if not user:
        return jsonify({'message': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
    
    # Vérification du mot de passe
    if not user.check_password(data['password']):
        return jsonify({'message': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
    
    # Vérification que le compte est actif
    if not user.is_active:
        return jsonify({'message': 'Ce compte est désactivé'}), 403
    
    # Connexion de l'utilisateur avec Flask-Login
    login_user(user)
    
    # Génération du token d'authentification
    token = generate_auth_token(user.id)
    
    return jsonify({
        'message': 'Connexion réussie',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        },
        'token': token
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Endpoint pour la déconnexion d'un utilisateur.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    logout_user()
    return jsonify({'message': 'Déconnexion réussie'}), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Endpoint pour récupérer le profil de l'utilisateur connecté.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """
    Endpoint pour mettre à jour le profil de l'utilisateur connecté.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    data = request.get_json()
    
    # Champs autorisés pour la mise à jour du profil
    allowed_fields = ['username', 'email', 'first_name', 'last_name', 'password']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    try:
        updated_user = update_user(user.id, **update_data)
        
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': {
                'id': updated_user.id,
                'username': updated_user.username,
                'email': updated_user.email,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'role': updated_user.role,
                'is_active': updated_user.is_active,
                'created_at': updated_user.created_at.isoformat(),
                'updated_at': updated_user.updated_at.isoformat()
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour du profil: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour du profil'}), 500

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """
    Endpoint pour récupérer la liste des utilisateurs (réservé aux administrateurs).
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    # Vérification des droits d'administrateur
    if user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    users = get_all_users()
    
    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat(),
            'updated_at': u.updated_at.isoformat()
        } for u in users]
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """
    Endpoint pour récupérer un utilisateur spécifique (réservé aux administrateurs).
    
    Args:
        user_id (int): ID de l'utilisateur à récupérer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    current_user = g.current_user
    
    # Vérification des droits d'administrateur ou accès à son propre profil
    if current_user.role != 'admin' and current_user.id != user_id:
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user_endpoint(user_id):
    """
    Endpoint pour mettre à jour un utilisateur spécifique (réservé aux administrateurs).
    
    Args:
        user_id (int): ID de l'utilisateur à mettre à jour
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    current_user = g.current_user
    
    # Vérification des droits d'administrateur
    if current_user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    
    try:
        updated_user = update_user(user_id, **data)
        if not updated_user:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'message': 'Utilisateur mis à jour avec succès',
            'user': {
                'id': updated_user.id,
                'username': updated_user.username,
                'email': updated_user.email,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'role': updated_user.role,
                'is_active': updated_user.is_active,
                'created_at': updated_user.created_at.isoformat(),
                'updated_at': updated_user.updated_at.isoformat()
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}")
        return jsonify({'message': 'Une erreur est survenue lors de la mise à jour de l\'utilisateur'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user_endpoint(user_id):
    """
    Endpoint pour supprimer un utilisateur spécifique (réservé aux administrateurs).
    
    Args:
        user_id (int): ID de l'utilisateur à supprimer
        
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    current_user = g.current_user
    
    # Vérification des droits d'administrateur
    if current_user.role != 'admin':
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    # Empêcher la suppression de son propre compte
    if current_user.id == user_id:
        return jsonify({'message': 'Vous ne pouvez pas supprimer votre propre compte'}), 400
    
    success = delete_user(user_id)
    if not success:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404
    
    return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200

@auth_bp.route('/token/refresh', methods=['POST'])
@token_required
def refresh_token():
    """
    Endpoint pour rafraîchir le token d'authentification.
    
    Returns:
        tuple: Réponse JSON et code HTTP
    """
    user = g.current_user
    
    # Génération d'un nouveau token
    token = generate_auth_token(user.id)
    
    return jsonify({
        'message': 'Token rafraîchi avec succès',
        'token': token
    }), 200
