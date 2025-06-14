#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.property import Property
from app.models.owner import Owner
from app.models.client import Client
from app.models.transaction import Transaction

from app.models.property_visit import PropertyVisit


from app import db
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil"""
    # Récupération des derniers biens ajoutés
    latest_properties = Property.query.order_by(Property.created_at.desc()).limit(6).all()
    
    # Récupération des prochaines visites
    upcoming_visits = PropertyVisit.query.filter(
        PropertyVisit.visit_date >= datetime.datetime.now(),
        PropertyVisit.status == 'scheduled'
    ).order_by(PropertyVisit.visit_date).limit(5).all()
    
    return render_template('index.html', 
                          latest_properties=latest_properties,
                          upcoming_visits=upcoming_visits)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord"""
    # Statistiques générales
    stats = {
        'properties_count': Property.query.count(),
        'owners_count': Owner.query.count(),
        'clients_count': Client.query.count(),
        'transactions_count': Transaction.query.count(),
        
        # Statistiques des biens par statut
        'properties_for_sale': Property.query.filter_by(status='for_sale').count(),
        'properties_for_rent': Property.query.filter_by(status='for_rent').count(),
        'properties_sold': Property.query.filter_by(status='sold').count(),
        'properties_rented': Property.query.filter_by(status='rented').count(),
        
        # Statistiques des biens par type
        'properties_apartment': Property.query.filter_by(property_type='apartment').count(),
        'properties_house': Property.query.filter_by(property_type='house').count(),
        'properties_land': Property.query.filter_by(property_type='land').count(),
        'properties_commercial': Property.query.filter_by(property_type='commercial').count(),
        'properties_other': Property.query.filter_by(property_type='other').count(),
        
        # Statistiques des transactions
        'sales_count': Transaction.query.filter_by(transaction_type='sale').count(),
        'rentals_count': Transaction.query.filter_by(transaction_type='rental').count(),
        
        # Données pour les graphiques
        'months': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
        'sales_by_month': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'rentals_by_month': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    
    # Récupération des activités récentes
    recent_activities = []  # À implémenter avec un modèle Activity
    
    return render_template('dashboard.html', stats=stats, recent_activities=recent_activities)

@main_bp.route('/properties')
def properties_list():
    """Liste des biens immobiliers"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Filtres
    filters = {}
    if request.args.get('property_type'):
        filters['property_type'] = request.args.get('property_type')
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('city'):
        filters['city'] = request.args.get('city')
    if request.args.get('owner_id'):
        filters['owner_id'] = request.args.get('owner_id')
    
    # Requête de base
    query = Property.query.filter_by(**filters)
    
    # Filtres supplémentaires
    if request.args.get('min_price'):
        min_price = float(request.args.get('min_price'))
        query = query.filter((Property.asking_price >= min_price) | (Property.rental_price >= min_price))
    if request.args.get('max_price'):
        max_price = float(request.args.get('max_price'))
        query = query.filter((Property.asking_price <= max_price) | (Property.rental_price <= max_price))
    if request.args.get('min_area'):
        query = query.filter(Property.total_area >= float(request.args.get('min_area')))
    if request.args.get('max_area'):
        query = query.filter(Property.total_area <= float(request.args.get('max_area')))
    if request.args.get('bedrooms'):
        query = query.filter(Property.num_bedrooms >= int(request.args.get('bedrooms')))
    if request.args.get('bathrooms'):
        query = query.filter(Property.num_bathrooms >= int(request.args.get('bathrooms')))
    if request.args.get('transaction_type') == 'sale':
        query = query.filter(Property.status.in_(['for_sale', 'sold']))
    elif request.args.get('transaction_type') == 'rental':
        query = query.filter(Property.status.in_(['for_rent', 'rented']))
    
    # Pagination
    pagination = query.order_by(Property.created_at.desc()).paginate(page=page, per_page=per_page)
    properties = pagination.items
    
    # Liste des propriétaires pour le filtre
    owners = Owner.query.all()
    
    return render_template('properties/list.html', 
                          properties=properties, 
                          pagination=pagination,
                          owners=owners)

@main_bp.route('/properties/<int:property_id>')
def property_detail(property_id):
    """Détail d'un bien immobilier"""
    property = Property.query.get_or_404(property_id)
    
    # Récupération des visites pour ce bien
    property_visits = PropertyVisit.query.filter_by(property_id=property_id).order_by(PropertyVisit.visit_date.desc()).all()
    
    # Récupération des transactions pour ce bien
    property_transactions = Transaction.query.filter_by(property_id=property_id).all()
    
    # Liste des clients pour le modal de planification de visite
    clients = Client.query.all()
    
    return render_template('properties/detail.html', 
                          property=property,
                          property_visits=property_visits,
                          property_transactions=property_transactions,
                          clients=clients)

@main_bp.route('/properties/create', methods=['GET', 'POST'])
@login_required
def property_create():
    """Création d'un bien immobilier"""
    # Liste des propriétaires pour le formulaire
    owners = Owner.query.all()
    
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Bien immobilier créé avec succès.', 'success')
        return redirect(url_for('main.properties_list'))
    
    return render_template('properties/create.html', 
                          owners=owners,
                          current_year=datetime.datetime.now().year)

@main_bp.route('/owners')
def owners_list():
    """Liste des propriétaires"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtres
    filters = {}
    if request.args.get('owner_type') == 'individual':
        filters['is_company'] = False
    elif request.args.get('owner_type') == 'company':
        filters['is_company'] = True
    
    # Requête de base
    query = Owner.query.filter_by(**filters)
    
    # Filtres supplémentaires
    if request.args.get('name'):
        search_term = f"%{request.args.get('name')}%"
        query = query.filter((Owner.first_name.ilike(search_term)) | 
                            (Owner.last_name.ilike(search_term)) | 
                            (Owner.company_name.ilike(search_term)))
    if request.args.get('city'):
        query = query.filter(Owner.city.ilike(f"%{request.args.get('city')}%"))
    
    # Filtre pour les propriétaires avec/sans biens
    if request.args.get('has_properties') == 'yes':
        query = query.filter(Owner.properties.any())
    elif request.args.get('has_properties') == 'no':
        query = query.filter(~Owner.properties.any())
    
    # Pagination
    pagination = query.order_by(Owner.id).paginate(page=page, per_page=per_page)
    owners = pagination.items
    
    return render_template('owners/list.html', 
                          owners=owners, 
                          pagination=pagination)

@main_bp.route('/clients')
def clients_list():
    """Liste des clients"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtres
    query = Client.query
    
    if request.args.get('name'):
        search_term = f"%{request.args.get('name')}%"
        query = query.filter((Client.first_name.ilike(search_term)) | 
                            (Client.last_name.ilike(search_term)))
    if request.args.get('email'):
        query = query.filter(Client.email.ilike(f"%{request.args.get('email')}%"))
    if request.args.get('phone'):
        query = query.filter(Client.phone.ilike(f"%{request.args.get('phone')}%"))
    if request.args.get('client_type'):
        query = query.filter(Client.client_type == request.args.get('client_type'))
    
    # Pagination
    pagination = query.order_by(Client.id).paginate(page=page, per_page=per_page)
    clients = pagination.items
    
    return render_template('clients/list.html', 
                          clients=clients, 
                          pagination=pagination)

@main_bp.route('/transactions')
def transactions_list():
    """Liste des transactions"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtres
    filters = {}
    if request.args.get('transaction_type'):
        filters['transaction_type'] = request.args.get('transaction_type')
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('property_id'):
        filters['property_id'] = request.args.get('property_id')
    if request.args.get('client_id'):
        filters['client_id'] = request.args.get('client_id')
    
    # Requête de base
    query = Transaction.query.filter_by(**filters)
    
    # Filtres supplémentaires
    if request.args.get('date_from'):
        date_from = datetime.datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
        query = query.filter(Transaction.transaction_date >= date_from)
    if request.args.get('date_to'):
        date_to = datetime.datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
        query = query.filter(Transaction.transaction_date <= date_to)
    if request.args.get('min_amount'):
        query = query.filter(Transaction.amount >= float(request.args.get('min_amount')))
    if request.args.get('max_amount'):
        query = query.filter(Transaction.amount <= float(request.args.get('max_amount')))
    
    # Pagination
    pagination = query.order_by(Transaction.transaction_date.desc()).paginate(page=page, per_page=per_page)
    transactions = pagination.items
    
    # Listes pour les filtres
    properties = Property.query.all()
    clients = Client.query.all()
    
    return render_template('transactions/list.html', 
                          transactions=transactions, 
                          pagination=pagination,
                          properties=properties,
                          clients=clients)

# Routes supplémentaires à implémenter
@main_bp.route('/owner/<int:owner_id>')
def owner_detail(owner_id):
    """Détail d'un propriétaire"""
    owner = Owner.query.get_or_404(owner_id)
    return render_template('owners/detail.html', owner=owner)

@main_bp.route('/owner/create', methods=['GET', 'POST'])
@login_required
def owner_create():
    """Création d'un propriétaire"""
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Propriétaire créé avec succès.', 'success')
        return redirect(url_for('main.owners_list'))
    return render_template('owners/create.html')

@main_bp.route('/client/<int:client_id>')
def client_detail(client_id):
    """Détail d'un client"""
    client = Client.query.get_or_404(client_id)
    return render_template('clients/detail.html', client=client)

@main_bp.route('/client/create', methods=['GET', 'POST'])
@login_required
def client_create():
    """Création d'un client"""
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Client créé avec succès.', 'success')
        return redirect(url_for('main.clients_list'))
    return render_template('clients/create.html')

@main_bp.route('/transaction/<int:transaction_id>')
def transaction_detail(transaction_id):
    """Détail d'une transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('transactions/detail.html', transaction=transaction)

@main_bp.route('/transaction/create', methods=['GET', 'POST'])
@login_required
def transaction_create():
    """Création d'une transaction"""
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Transaction créée avec succès.', 'success')
        return redirect(url_for('main.transactions_list'))
    
    # Listes pour le formulaire
    properties = Property.query.all()
    clients = Client.query.all()
    
    return render_template('transactions/create.html', 
                          properties=properties,
                          clients=clients)

@main_bp.route('/visits')
@login_required
def visits_list():
    """Liste des visites"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtres
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    
    # Requête de base
    query = PropertyVisit.query.filter_by(**filters)
    
    # Pagination
    pagination = query.order_by(PropertyVisit.visit_date.desc()).paginate(page=page, per_page=per_page)
    visits = pagination.items
    
    return render_template('visits/list.html', 
                          visits=visits, 
                          pagination=pagination)

@main_bp.route('/visit/<int:visit_id>')
def visit_detail(visit_id):
    """Détail d'une visite"""
    visit = PropertyVisit.query.get_or_404(visit_id)
    return render_template('visits/detail.html', visit=visit)

# Routes pour l'édition
@main_bp.route('/properties/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def property_edit(property_id):
    """Édition d'un bien immobilier"""
    property = Property.query.get_or_404(property_id)
    owners = Owner.query.all()
    
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Bien immobilier mis à jour avec succès.', 'success')
        return redirect(url_for('main.property_detail', property_id=property.id))
    
    return render_template('properties/edit.html', 
                          property=property,
                          owners=owners,
                          current_year=datetime.datetime.now().year)

@main_bp.route('/owners/<int:owner_id>/edit', methods=['GET', 'POST'])
@login_required
def owner_edit(owner_id):
    """Édition d'un propriétaire"""
    owner = Owner.query.get_or_404(owner_id)
    
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Propriétaire mis à jour avec succès.', 'success')
        return redirect(url_for('main.owner_detail', owner_id=owner.id))
    
    return render_template('owners/edit.html', owner=owner)

@main_bp.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def client_edit(client_id):
    """Édition d'un client"""
    client = Client.query.get_or_404(client_id)
    
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Client mis à jour avec succès.', 'success')
        return redirect(url_for('main.client_detail', client_id=client.id))
    
    return render_template('clients/edit.html', client=client)

@main_bp.route('/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def transaction_edit(transaction_id):
    """Édition d'une transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if request.method == 'POST':
        # Traitement du formulaire - à implémenter
        flash('Transaction mise à jour avec succès.', 'success')
        return redirect(url_for('main.transaction_detail', transaction_id=transaction.id))
    
    # Listes pour le formulaire
    properties = Property.query.all()
    clients = Client.query.all()
    
    return render_template('transactions/edit.html', 
                          transaction=transaction,
                          properties=properties,
                          clients=clients)

# Routes pour la suppression
@main_bp.route('/properties/<int:property_id>/delete', methods=['POST'])
@login_required
def property_delete(property_id):
    """Suppression d'un bien immobilier"""
    property = Property.query.get_or_404(property_id)
    db.session.delete(property)
    db.session.commit()
    flash('Bien immobilier supprimé avec succès.', 'success')
    return redirect(url_for('main.properties_list'))

@main_bp.route('/owners/<int:owner_id>/delete', methods=['POST'])
@login_required
def owner_delete(owner_id):
    """Suppression d'un propriétaire"""
    owner = Owner.query.get_or_404(owner_id)
    db.session.delete(owner)
    db.session.commit()
    flash('Propriétaire supprimé avec succès.', 'success')
    return redirect(url_for('main.owners_list'))

@main_bp.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
def client_delete(client_id):
    """Suppression d'un client"""
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash('Client supprimé avec succès.', 'success')
    return redirect(url_for('main.clients_list'))

@main_bp.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
@login_required
def transaction_delete(transaction_id):
    """Suppression d'une transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction supprimée avec succès.', 'success')
    return redirect(url_for('main.transactions_list'))
