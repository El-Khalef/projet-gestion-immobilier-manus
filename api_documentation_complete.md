# Documentation des API - Gestion Immobilière

Cette documentation détaille toutes les routes API disponibles dans l'application de gestion immobilière.

## Table des matières

1. [Authentification](#authentification)
2. [Biens Immobiliers](#biens-immobiliers)
3. [Propriétaires](#propriétaires)
4. [Clients](#clients)
5. [Transactions](#transactions)

## Authentification

### Inscription

- **URL** : `/api/auth/register`
- **Méthode** : `POST`
- **Description** : Inscription d'un nouvel utilisateur
- **Corps de la requête** :
```json
{
  "username": "utilisateur",
  "email": "utilisateur@example.com",
  "password": "motdepasse123",
  "first_name": "Prénom",
  "last_name": "Nom"
}
```
- **Réponse** :
```json
{
  "message": "Utilisateur créé avec succès",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "utilisateur",
    "email": "utilisateur@example.com"
  }
}
```

### Connexion

- **URL** : `/api/auth/login`
- **Méthode** : `POST`
- **Description** : Connexion d'un utilisateur existant
- **Corps de la requête** :
```json
{
  "username": "utilisateur",
  "password": "motdepasse123"
}
```
- **Réponse** :
```json
{
  "message": "Connexion réussie",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "utilisateur",
    "email": "utilisateur@example.com",
    "role": "user"
  }
}
```

### Profil utilisateur

- **URL** : `/api/auth/profile`
- **Méthode** : `GET`
- **Description** : Récupération du profil de l'utilisateur connecté
- **En-têtes** : `Authorization: Bearer <token>`
- **Réponse** :
```json
{
  "id": 1,
  "username": "utilisateur",
  "email": "utilisateur@example.com",
  "first_name": "Prénom",
  "last_name": "Nom",
  "role": "user",
  "created_at": "2025-06-01T12:00:00"
}
```

## Biens Immobiliers

### Liste des biens immobiliers

- **URL** : `/api/properties/`
- **Méthode** : `GET`
- **Description** : Récupération de la liste des biens immobiliers avec pagination et filtrage
- **Paramètres de requête** :
  - `page` : Numéro de page (défaut: 1)
  - `per_page` : Nombre d'éléments par page (défaut: 10)
  - `property_type` : Type de bien (apartment, house, land, commercial, etc.)
  - `status` : Statut du bien (for_sale, for_rent, sold, rented)
  - `city` : Ville
  - `min_price` : Prix minimum
  - `max_price` : Prix maximum
  - `min_area` : Surface minimum
  - `max_area` : Surface maximum
  - `bedrooms` : Nombre de chambres
  - `bathrooms` : Nombre de salles de bain
  - `owner_id` : ID du propriétaire
  - `transaction_type` : Type de transaction (sale, rental)
- **Réponse** :
```json
{
  "properties": [
    {
      "id": 1,
      "reference_code": "PROP-001",
      "title": "Appartement spacieux au centre-ville",
      "property_type": "apartment",
      "status": "for_sale",
      "city": "Paris",
      "postal_code": "75001",
      "country": "France",
      "total_area": 75.5,
      "num_bedrooms": 2,
      "num_bathrooms": 1,
      "asking_price": 350000,
      "rental_price": null,
      "primary_image": "http://localhost:5000/static/img/properties/prop-001-main.jpg",
      "created_at": "2025-06-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 5,
    "total_items": 42
  }
}
```

### Détail d'un bien immobilier

- **URL** : `/api/properties/<property_id>`
- **Méthode** : `GET`
- **Description** : Récupération des détails d'un bien immobilier spécifique
- **Réponse** :
```json
{
  "id": 1,
  "reference_code": "PROP-001",
  "title": "Appartement spacieux au centre-ville",
  "description": "Magnifique appartement rénové...",
  "property_type": "apartment",
  "status": "for_sale",
  "address": {
    "line1": "123 Rue de Rivoli",
    "line2": "Étage 3, Porte 302",
    "city": "Paris",
    "state_province": "Île-de-France",
    "postal_code": "75001",
    "country": "France",
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  "features": {
    "total_area": 75.5,
    "living_area": 70.0,
    "land_area": null,
    "num_bedrooms": 2,
    "num_bathrooms": 1,
    "num_floors": 1,
    "year_built": 1985,
    "energy_rating": "C",
    "has_garage": false,
    "has_garden": false,
    "has_terrace": true,
    "has_pool": false,
    "is_furnished": false
  },
  "pricing": {
    "asking_price": 350000,
    "rental_price": null
  },
  "owner_id": 1,
  "created_by": 1,
  "created_at": "2025-06-01T12:00:00",
  "updated_at": "2025-06-01T12:00:00",
  "images": [
    {
      "id": 1,
      "url": "http://localhost:5000/static/img/properties/prop-001-main.jpg",
      "is_primary": true,
      "title": "Vue principale",
      "description": "Salon lumineux"
    }
  ],
  "documents": [
    {
      "id": 1,
      "document_type": "diagnostic",
      "url": "http://localhost:5000/static/documents/properties/prop-001-diagnostic.pdf",
      "title": "Diagnostic énergétique",
      "description": "DPE réalisé le 15/05/2025",
      "expiry_date": "2030-05-15"
    }
  ],
  "amenities": [
    {
      "id": 1,
      "name": "Ascenseur",
      "category": "building"
    },
    {
      "id": 2,
      "name": "Cuisine équipée",
      "category": "interior"
    }
  ]
}
```

### Recherche par code de référence

- **URL** : `/api/properties/reference/<reference_code>`
- **Méthode** : `GET`
- **Description** : Recherche d'un bien immobilier par son code de référence
- **Réponse** : Identique à la réponse de détail d'un bien immobilier

### Création d'un bien immobilier

- **URL** : `/api/properties/`
- **Méthode** : `POST`
- **Description** : Création d'un nouveau bien immobilier
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
```json
{
  "title": "Appartement spacieux au centre-ville",
  "description": "Magnifique appartement rénové...",
  "property_type": "apartment",
  "status": "for_sale",
  "address_line1": "123 Rue de Rivoli",
  "address_line2": "Étage 3, Porte 302",
  "city": "Paris",
  "state_province": "Île-de-France",
  "postal_code": "75001",
  "country": "France",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "total_area": 75.5,
  "living_area": 70.0,
  "num_bedrooms": 2,
  "num_bathrooms": 1,
  "num_floors": 1,
  "year_built": 1985,
  "energy_rating": "C",
  "has_garage": false,
  "has_garden": false,
  "has_terrace": true,
  "has_pool": false,
  "is_furnished": false,
  "asking_price": 350000,
  "owner_id": 1
}
```
- **Réponse** :
```json
{
  "message": "Bien immobilier créé avec succès",
  "property": {
    "id": 1,
    "reference_code": "PROP-001",
    "title": "Appartement spacieux au centre-ville"
  }
}
```

### Mise à jour d'un bien immobilier

- **URL** : `/api/properties/<property_id>`
- **Méthode** : `PUT`
- **Description** : Mise à jour d'un bien immobilier existant
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** : Identique à la création, mais seuls les champs à modifier sont nécessaires
- **Réponse** :
```json
{
  "message": "Bien immobilier mis à jour avec succès",
  "property": {
    "id": 1,
    "reference_code": "PROP-001",
    "title": "Appartement spacieux au centre-ville"
  }
}
```

### Suppression d'un bien immobilier

- **URL** : `/api/properties/<property_id>`
- **Méthode** : `DELETE`
- **Description** : Suppression d'un bien immobilier
- **En-têtes** : `Authorization: Bearer <token>`
- **Réponse** :
```json
{
  "message": "Bien immobilier supprimé avec succès"
}
```

## Propriétaires

### Liste des propriétaires

- **URL** : `/api/owners/`
- **Méthode** : `GET`
- **Description** : Récupération de la liste des propriétaires avec pagination et recherche
- **Paramètres de requête** :
  - `page` : Numéro de page (défaut: 1)
  - `per_page` : Nombre d'éléments par page (défaut: 10)
  - `search` : Terme de recherche (nom, email, etc.)
- **Réponse** :
```json
{
  "owners": [
    {
      "id": 1,
      "first_name": "Jean",
      "last_name": "Dupont",
      "email": "jean.dupont@example.com",
      "phone": "+33123456789",
      "city": "Paris",
      "country": "France",
      "is_company": false,
      "company_name": null,
      "properties_count": 3,
      "created_at": "2025-06-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 2,
    "total_items": 15
  }
}
```

### Détail d'un propriétaire

- **URL** : `/api/owners/<owner_id>`
- **Méthode** : `GET`
- **Description** : Récupération des détails d'un propriétaire spécifique
- **Réponse** :
```json
{
  "id": 1,
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "phone": "+33123456789",
  "address": {
    "line1": "45 Avenue des Champs-Élysées",
    "line2": "Appartement 5B",
    "city": "Paris",
    "state_province": "Île-de-France",
    "postal_code": "75008",
    "country": "France"
  },
  "company_info": {
    "is_company": false,
    "company_name": null,
    "company_registration_number": null,
    "tax_id": null
  },
  "notes": "Propriétaire de plusieurs biens dans le 8ème arrondissement",
  "properties_count": 3,
  "created_at": "2025-06-01T12:00:00",
  "updated_at": "2025-06-01T12:00:00",
  "created_by": 1
}
```

### Création d'un propriétaire

- **URL** : `/api/owners/`
- **Méthode** : `POST`
- **Description** : Création d'un nouveau propriétaire
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "phone": "+33123456789",
  "address_line1": "45 Avenue des Champs-Élysées",
  "address_line2": "Appartement 5B",
  "city": "Paris",
  "state_province": "Île-de-France",
  "postal_code": "75008",
  "country": "France",
  "is_company": false,
  "notes": "Propriétaire de plusieurs biens dans le 8ème arrondissement"
}
```
- **Réponse** :
```json
{
  "message": "Propriétaire créé avec succès",
  "owner": {
    "id": 1,
    "first_name": "Jean",
    "last_name": "Dupont",
    "company_name": null,
    "is_company": false
  }
}
```

### Mise à jour d'un propriétaire

- **URL** : `/api/owners/<owner_id>`
- **Méthode** : `PUT`
- **Description** : Mise à jour d'un propriétaire existant
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** : Identique à la création, mais seuls les champs à modifier sont nécessaires
- **Réponse** :
```json
{
  "message": "Propriétaire mis à jour avec succès",
  "owner": {
    "id": 1,
    "first_name": "Jean",
    "last_name": "Dupont",
    "company_name": null,
    "is_company": false
  }
}
```

### Suppression d'un propriétaire

- **URL** : `/api/owners/<owner_id>`
- **Méthode** : `DELETE`
- **Description** : Suppression d'un propriétaire
- **En-têtes** : `Authorization: Bearer <token>`
- **Réponse** :
```json
{
  "message": "Propriétaire supprimé avec succès"
}
```

### Biens immobiliers d'un propriétaire

- **URL** : `/api/owners/<owner_id>/properties`
- **Méthode** : `GET`
- **Description** : Récupération des biens immobiliers d'un propriétaire
- **Paramètres de requête** :
  - `page` : Numéro de page (défaut: 1)
  - `per_page` : Nombre d'éléments par page (défaut: 10)
- **Réponse** :
```json
{
  "properties": [
    {
      "id": 1,
      "reference_code": "PROP-001",
      "title": "Appartement spacieux au centre-ville",
      "property_type": "apartment",
      "status": "for_sale",
      "city": "Paris",
      "country": "France",
      "asking_price": 350000,
      "rental_price": null,
      "created_at": "2025-06-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_items": 3
  },
  "owner": {
    "id": 1,
    "first_name": "Jean",
    "last_name": "Dupont",
    "company_name": null,
    "is_company": false
  }
}
```

## Clients

### Liste des clients

- **URL** : `/api/clients/`
- **Méthode** : `GET`
- **Description** : Récupération de la liste des clients avec pagination et filtrage
- **Paramètres de requête** :
  - `page` : Numéro de page (défaut: 1)
  - `per_page` : Nombre d'éléments par page (défaut: 10)
  - `search` : Terme de recherche (nom, email, etc.)
  - `client_type` : Type de client (buyer, tenant, both)
  - `assigned_agent_id` : ID de l'agent assigné
- **Réponse** :
```json
{
  "clients": [
    {
      "id": 1,
      "first_name": "Marie",
      "last_name": "Martin",
      "email": "marie.martin@example.com",
      "phone": "+33123456789",
      "city": "Lyon",
      "country": "France",
      "client_type": "buyer",
      "budget_range": "300 000 € - 400 000 €",
      "assigned_agent_id": 2,
      "created_at": "2025-06-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 3,
    "total_items": 25
  }
}
```

### Détail d'un client

- **URL** : `/api/clients/<client_id>`
- **Méthode** : `GET`
- **Description** : Récupération des détails d'un client spécifique
- **Réponse** :
```json
{
  "id": 1,
  "first_name": "Marie",
  "last_name": "Martin",
  "email": "marie.martin@example.com",
  "phone": "+33123456789",
  "address": {
    "line1": "15 Rue de la République",
    "line2": null,
    "city": "Lyon",
    "state_province": "Auvergne-Rhône-Alpes",
    "postal_code": "69002",
    "country": "France"
  },
  "client_type": "buyer",
  "budget": {
    "min": 300000,
    "max": 400000,
    "formatted": "300 000 € - 400 000 €"
  },
  "requirements": "Appartement 3 pièces minimum, proche des transports",
  "notes": "Recherche active depuis 3 mois",
  "assigned_agent_id": 2,
  "created_at": "2025-06-01T12:00:00",
  "updated_at": "2025-06-01T12:00:00"
}
```

### Création d'un client

- **URL** : `/api/clients/`
- **Méthode** : `POST`
- **Description** : Création d'un nouveau client
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
```json
{
  "first_name": "Marie",
  "last_name": "Martin",
  "email": "marie.martin@example.com",
  "phone": "+33123456789",
  "address_line1": "15 Rue de la République",
  "city": "Lyon",
  "state_province": "Auvergne-Rhône-Alpes",
  "postal_code": "69002",
  "country": "France",
  "client_type": "buyer",
  "budget_min": 300000,
  "budget_max": 400000,
  "requirements": "Appartement 3 pièces minimum, proche des transports",
  "notes": "Recherche active depuis 3 mois",
  "assigned_agent_id": 2
}
```
- **Réponse** :
```json
{
  "message": "Client créé avec succès",
  "client": {
    "id": 1,
    "first_name": "Marie",
    "last_name": "Martin",
    "client_type": "buyer"
  }
}
```

### Mise à jour d'un client

- **URL** : `/api/clients/<client_id>`
- **Méthode** : `PUT`
- **Description** : Mise à jour d'un client existant
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** : Identique à la création, mais seuls les champs à modifier sont nécessaires
- **Réponse** :
```json
{
  "message": "Client mis à jour avec succès",
  "client": {
    "id": 1,
    "first_name": "Marie",
    "last_name": "Martin",
    "client_type": "buyer"
  }
}
```

### Suppression d'un client

- **URL** : `/api/clients/<client_id>`
- **Méthode** : `DELETE`
- **Description** : Suppression d'un client
- **En-têtes** : `Authorization: Bearer <token>`
- **Réponse** :
```json
{
  "message": "Client supprimé avec succès"
}
```

### Biens immobiliers qui intéressent un client

- **URL** : `/api/clients/<client_id>/interests`
- **Méthode** : `GET`
- **Description** : Récupération des biens immobiliers qui intéressent un client
- **Paramètres de requête** :
  - `page` : Numéro de page (défaut: 1)
  - `per_page` : Nombre d'éléments par page (défaut: 10)
- **Réponse** :
```json
{
  "properties": [
    {
      "id": 1,
      "reference_code": "PROP-001",
      "title": "Appartement spacieux au centre-ville",
      "property_type": "apartment",
      "status": "for_sale",
      "city": "Paris",
      "country": "France",
      "asking_price": 350000,
      "rental_price": null,
      "interest_level": "high",
      "notes": "Très intéressée, souhaite visiter rapidement"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
 
(Content truncated due to size limit. Use line ranges to read in chunks)