# Modélisation de la Base de Données pour le Projet de Gestion Immobilière

Ce document détaille la conception de la base de données PostgreSQL pour notre application de gestion immobilière. Nous allons explorer les différentes tables, leurs attributs, et les relations entre elles, en expliquant les choix de conception et les bonnes pratiques appliquées.

## Vue d'ensemble du Modèle de Données

Notre base de données doit représenter efficacement toutes les entités et relations du domaine immobilier. Voici les principales entités que nous allons modéliser :

1. Biens immobiliers (propriétés)
2. Propriétaires et clients
3. Transactions (ventes et locations)
4. Données financières
5. Maintenance et travaux
6. Utilisateurs du système

Ces entités sont interconnectées par diverses relations, certaines simples (one-to-many) et d'autres plus complexes (many-to-many) nécessitant des tables de jointure.

## Schéma Détaillé des Tables

### Table `users` (Utilisateurs)

Cette table stocke les informations sur les utilisateurs de l'application.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(20) NOT NULL,  -- 'admin', 'agent', 'manager', etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

La table `users` est fondamentale pour la gestion des accès et la sécurité de l'application. Nous stockons le hash du mot de passe plutôt que le mot de passe en clair pour des raisons de sécurité. Le champ `role` permet de définir différents niveaux d'accès dans l'application.

### Table `properties` (Biens Immobiliers)

Cette table centrale stocke les informations sur tous les biens immobiliers gérés par l'application.

```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    reference_code VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    property_type VARCHAR(50) NOT NULL,  -- 'apartment', 'house', 'land', 'commercial', etc.
    status VARCHAR(20) NOT NULL,  -- 'available', 'sold', 'rented', etc.
    address_line1 VARCHAR(100) NOT NULL,
    address_line2 VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    state_province VARCHAR(50),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    total_area DECIMAL(10, 2) NOT NULL,  -- in square meters
    living_area DECIMAL(10, 2),  -- in square meters
    land_area DECIMAL(10, 2),  -- in square meters
    num_bedrooms INTEGER,
    num_bathrooms INTEGER,
    num_floors INTEGER,
    year_built INTEGER,
    energy_rating VARCHAR(10),
    has_garage BOOLEAN DEFAULT FALSE,
    has_garden BOOLEAN DEFAULT FALSE,
    has_terrace BOOLEAN DEFAULT FALSE,
    has_pool BOOLEAN DEFAULT FALSE,
    is_furnished BOOLEAN DEFAULT FALSE,
    asking_price DECIMAL(12, 2),  -- for sale properties
    rental_price DECIMAL(10, 2),  -- for rental properties
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    owner_id INTEGER REFERENCES owners(id)
);
```

La table `properties` est très détaillée car elle doit capturer toutes les caractéristiques importantes d'un bien immobilier. Nous incluons des informations géographiques (adresse, coordonnées), des caractéristiques physiques (superficie, nombre de pièces), des équipements, et des informations financières (prix de vente ou de location).

### Table `owners` (Propriétaires)

Cette table stocke les informations sur les propriétaires des biens immobiliers.

```sql
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state_province VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    tax_id VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

La table `owners` contient les informations de contact et fiscales des propriétaires. Un propriétaire peut posséder plusieurs biens (relation one-to-many avec `properties`).

### Table `clients` (Clients)

Cette table stocke les informations sur les clients potentiels (acheteurs ou locataires).

```sql
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state_province VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    client_type VARCHAR(20) NOT NULL,  -- 'buyer', 'tenant', 'both'
    budget_min DECIMAL(12, 2),
    budget_max DECIMAL(12, 2),
    requirements TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_agent_id INTEGER REFERENCES users(id)
);
```

La table `clients` contient les informations sur les clients, y compris leurs préférences et leur budget. Un client peut être intéressé par plusieurs biens, et un bien peut intéresser plusieurs clients, ce qui nécessitera une table de jointure.

### Table `property_images` (Images des Biens)

Cette table stocke les images associées aux biens immobiliers.

```sql
CREATE TABLE property_images (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER,
    title VARCHAR(100),
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id)
);
```

La table `property_images` permet de stocker plusieurs images pour chaque bien immobilier, avec des métadonnées comme le titre, la description, et l'ordre d'affichage.

### Table `property_documents` (Documents des Biens)

Cette table stocke les documents associés aux biens immobiliers (titres de propriété, diagnostics, etc.).

```sql
CREATE TABLE property_documents (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,  -- 'title_deed', 'energy_certificate', 'floor_plan', etc.
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),
    title VARCHAR(100),
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id),
    expiry_date DATE
);
```

La table `property_documents` permet de gérer tous les documents légaux et techniques associés à un bien immobilier.

### Table `transactions` (Transactions)

Cette table enregistre toutes les transactions (ventes et locations) effectuées.

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL,  -- 'sale', 'rental'
    property_id INTEGER NOT NULL REFERENCES properties(id),
    client_id INTEGER NOT NULL REFERENCES clients(id),
    transaction_date DATE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    commission_amount DECIMAL(10, 2),
    commission_percentage DECIMAL(5, 2),
    status VARCHAR(20) NOT NULL,  -- 'pending', 'completed', 'cancelled'
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    handled_by INTEGER REFERENCES users(id)
);
```

La table `transactions` enregistre les ventes et locations de biens, avec des informations sur les montants, les commissions, et les parties impliquées.

### Table `rental_agreements` (Contrats de Location)

Cette table stocke les détails spécifiques aux contrats de location.

```sql
CREATE TABLE rental_agreements (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_renewable BOOLEAN DEFAULT TRUE,
    rent_amount DECIMAL(10, 2) NOT NULL,
    rent_frequency VARCHAR(20) NOT NULL,  -- 'monthly', 'quarterly', 'yearly'
    deposit_amount DECIMAL(10, 2) NOT NULL,
    payment_day INTEGER NOT NULL,  -- day of month when rent is due
    special_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

La table `rental_agreements` complète la table `transactions` avec des informations spécifiques aux locations, comme les dates de début et de fin, le montant du loyer, et les conditions spéciales.

### Table `financial_transactions` (Transactions Financières)

Cette table enregistre toutes les transactions financières liées aux biens immobiliers.

```sql
CREATE TABLE financial_transactions (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    transaction_id INTEGER REFERENCES transactions(id),
    transaction_type VARCHAR(50) NOT NULL,  -- 'rent_payment', 'expense', 'tax', etc.
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    transaction_date DATE NOT NULL,
    description TEXT,
    category VARCHAR(50),  -- 'maintenance', 'utilities', 'taxes', etc.
    payment_method VARCHAR(50),
    reference_number VARCHAR(50),
    is_income BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);
```

La table `financial_transactions` permet de suivre tous les flux financiers liés aux biens immobiliers, qu'il s'agisse de revenus (loyers) ou de dépenses (charges, travaux, taxes).

### Table `maintenance_requests` (Demandes de Maintenance)

Cette table enregistre les demandes de maintenance et de réparation pour les biens immobiliers.

```sql
CREATE TABLE maintenance_requests (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    requested_by INTEGER REFERENCES clients(id),  -- if tenant
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    issue_description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high', 'emergency'
    status VARCHAR(20) NOT NULL,  -- 'pending', 'assigned', 'in_progress', 'completed', 'cancelled'
    assigned_to INTEGER REFERENCES users(id),
    estimated_cost DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2),
    scheduled_date DATE,
    completion_date DATE,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

La table `maintenance_requests` permet de suivre les problèmes de maintenance signalés par les locataires ou les propriétaires, et de gérer leur résolution.

### Table `property_amenities` (Équipements des Biens)

Cette table de jointure associe des équipements spécifiques aux biens immobiliers.

```sql
CREATE TABLE amenities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    category VARCHAR(50),  -- 'interior', 'exterior', 'security', etc.
    description TEXT
);

CREATE TABLE property_amenities (
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    amenity_id INTEGER NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    PRIMARY KEY (property_id, amenity_id)
);
```

Cette structure permet de gérer une liste flexible d'équipements et de les associer aux biens immobiliers via une relation many-to-many.

### Table `client_property_interests` (Intérêts des Clients)

Cette table de jointure enregistre l'intérêt des clients pour des biens spécifiques.

```sql
CREATE TABLE client_property_interests (
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    interest_level VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (client_id, property_id)
);
```

Cette table permet de suivre quels clients sont intéressés par quels biens, facilitant ainsi le travail des agents immobiliers.

### Table `property_visits` (Visites de Biens)

Cette table enregistre les visites de biens par les clients.

```sql
CREATE TABLE property_visits (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    client_id INTEGER NOT NULL REFERENCES clients(id),
    visit_date TIMESTAMP NOT NULL,
    duration INTEGER,  -- in minutes
    status VARCHAR(20) NOT NULL,  -- 'scheduled', 'completed', 'cancelled', 'no_show'
    feedback TEXT,
    interest_level VARCHAR(20),  -- 'none', 'low', 'medium', 'high'
    accompanied_by INTEGER REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

La table `property_visits` permet de planifier et de suivre les visites de biens par les clients potentiels, et d'enregistrer leurs retours.

## Diagramme des Relations

Voici une représentation simplifiée des relations entre les principales tables :

```
users
  ↑
  |
  +----> properties <----+ property_images
  |      ↑    ↑    ↑     |
  |      |    |    |     + property_documents
  |      |    |    |
owners --+    |    +---- property_amenities <---- amenities
               |
               +---- client_property_interests <---- clients
               |                                      ↑
               |                                      |
               +---- property_visits ------------------+
               |
               +---- transactions <---- rental_agreements
                      ↑
                      |
                      +---- financial_transactions
                      |
                      +---- maintenance_requests
```

Ce diagramme montre comment les différentes tables sont interconnectées, formant un modèle de données complet pour notre application de gestion immobilière.

## Considérations de Conception

### Normalisation

Notre schéma suit les principes de normalisation pour éviter la redondance des données et garantir l'intégrité référentielle. Par exemple, nous avons séparé les propriétaires, les clients et les utilisateurs en tables distinctes, même s'ils partagent certains attributs communs comme les informations de contact.

### Clés Étrangères et Contraintes

Nous utilisons des clés étrangères pour maintenir l'intégrité référentielle entre les tables. Par exemple, chaque bien immobilier est lié à un propriétaire via la clé étrangère `owner_id`. Nous avons également défini des contraintes `ON DELETE CASCADE` lorsque cela est approprié, par exemple pour les images et documents des biens.

### Tables de Jointure

Pour les relations many-to-many, nous avons créé des tables de jointure comme `property_amenities` et `client_property_interests`. Ces tables contiennent les clés primaires des deux tables qu'elles relient, formant une clé primaire composite.

### Horodatage et Audit

La plupart des tables incluent des champs `created_at` et `updated_at` pour suivre quand les enregistrements ont été créés et modifiés. Certaines tables incluent également des références à l'utilisateur qui a créé ou modifié l'enregistrement, ce qui est utile pour l'audit et la traçabilité.

### Types de Données

Nous avons choisi des types de données appropriés pour chaque attribut :
- `VARCHAR` pour les chaînes de caractères de longueur variable
- `TEXT` pour les textes longs
- `INTEGER` pour les nombres entiers
- `DECIMAL` pour les valeurs monétaires et les mesures précises
- `BOOLEAN` pour les valeurs vrai/faux
- `DATE` et `TIMESTAMP` pour les dates et heures
- `SERIAL` pour les clés primaires auto-incrémentées

### Indexation

Bien que non montrée dans les définitions de tables ci-dessus, il sera important d'ajouter des index sur les colonnes fréquemment utilisées dans les requêtes, comme les clés étrangères et les colonnes de recherche (ville, type de bien, statut, etc.).

## Implémentation avec SQLAlchemy

Dans notre application Flask, nous implémenterons ce schéma de base de données en utilisant SQLAlchemy. Voici un exemple de la façon dont nous définirons le modèle `Property` :

```python
from app import db
from datetime import datetime

class Property(db.Model):
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    property_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    
    # Adresse
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50), nullable=False)
    state_province = db.Column(db.String(50))
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    
    # Caractéristiques
    total_area = db.Column(db.Numeric(10, 2), nullable=False)
    living_area = db.Column(db.Numeric(10, 2))
    land_area = db.Column(db.Numeric(10, 2))
    num_bedrooms = db.Column(db.Integer)
    num_bathrooms = db.Column(db.Integer)
    num_floors = db.Column(db.Integer)
    year_built = db.Column(db.Integer)
    energy_rating = db.Column(db.String(10))
    
    # Équipements
    has_garage = db.Column(db.Boolean, default=False)
    has_garden = db.Column(db.Boolean, default=False)
    has_terrace = db.Column(db.Boolean, default=False)
    has_pool = db.Column(db.Boolean, default=False)
    is_furnished = db.Column(db.Boolean, default=False)
    
    # Prix
    asking_price = db.Column(db.Numeric(12, 2))
    rental_price = db.Column(db.Numeric(10, 2))
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
    
    # Relations
    owner = db.relationship('Owner', backref=db.backref('properties', lazy=True))
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('PropertyDocument', backref='property', lazy=True, cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary='property_amenities', lazy='subquery',
                               backref=db.backref('properties', lazy=True))
    
    def __repr__(self):
        return f'<Property {self.reference_code}: {self.title}>'
```

Ce modèle SQLAlchemy reflète la structure de la table `properties` définie précédemment, avec des relations vers les autres tables. Les relations sont définies à l'aide de `db.relationship`, qui spécifie comment les objets sont liés entre eux.

## Conclusion

Cette modélisation de base de données fournit une fondation solide pour notre application de gestion immobilière. Elle capture toutes les entités et relations importantes du domaine immobilier, tout en suivant les bonnes pratiques de conception de base de données.

Dans les prochaines étapes, nous implémenterons ces modèles dans notre application Flask et créerons les migrations nécessaires pour initialiser la base de données. Nous développerons également les routes API et les services qui interagiront avec ces modèles pour fournir les fonctionnalités de l'application.
