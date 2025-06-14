#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialisation du module models.
Ce fichier importe tous les modèles pour les rendre disponibles via app.models.
"""

#from app import db

# Import des modèles
# Ces imports seront décommentés au fur et à mesure de leur implémentation
# from app.models.user import User
# from app.models.property import Property
# from app.models.owner import Owner
# from app.models.client import Client
# from app.models.transaction import Transaction
# from app.models.financial import FinancialTransaction
# from app.models.maintenance import MaintenanceRequest




#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mise à jour du module models pour importer tous les modèles.
Ce fichier importe tous les modèles pour les rendre disponibles via app.models.
"""

from app import db

# Import des modèles
from app.models.user1 import User
from app.models.owner import Owner
from app.models.property import Property, PropertyImage, PropertyDocument, Amenity
from app.models.client import Client, PropertyVisit
from app.models.transaction import Transaction, RentalAgreement
from app.models.old1_financial import FinancialTransaction, MaintenanceRequest

# Définition des modèles disponibles pour l'importation
__all__ = [
    'User',
    'Owner',
    'Property',
    'PropertyImage',
    'PropertyDocument',
    'Amenity',
    'Client',
    'PropertyVisit',
    'Transaction',
    'RentalAgreement',
    'FinancialTransaction',
    'MaintenanceRequest'
]
