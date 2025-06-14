#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialisation du module routes.
Ce fichier importe tous les blueprints pour les rendre disponibles via app.routes.
"""

from app.routes.old_auth import auth_bp
from app.routes.properties import properties_bp
from app.routes.owners import owners_bp
from app.routes.clients import clients_bp
from app.routes.transactions import transactions_bp
from app.routes.financials import financials_bp
from app.routes.maintenance import maintenance_bp

# Liste des blueprints disponibles
blueprints = [
    auth_bp,
    properties_bp,
    owners_bp,
    clients_bp,
    transactions_bp,
    financials_bp,
    maintenance_bp
]
