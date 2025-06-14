# Documentation des API - Gestion Immobilière

Ce document présente les différentes routes API disponibles dans l'application de gestion immobilière, avec des exemples d'utilisation.

## Table des matières

1. [Authentification et Gestion des Utilisateurs](#1-authentification-et-gestion-des-utilisateurs)
2. [Gestion des Biens Immobiliers](#2-gestion-des-biens-immobiliers)
3. [Exemples d'utilisation](#3-exemples-dutilisation)

## 1. Authentification et Gestion des Utilisateurs

### Inscription d'un utilisateur

- **URL** : `/api/auth/register`
- **Méthode** : `POST`
- **Corps de la requête** :
  ```json
  {
    "username": "utilisateur1",
    "email": "utilisateur1@example.com",
    "password": "motdepasse123",
    "first_name": "Prénom",
    "last_name": "Nom"
  }
  ```
- **Réponse** : Token JWT et informations de l'utilisateur

### Connexion

- **URL** : `/api/auth/login`
- **Méthode** : `POST`
- **Corps de la requête** :
  ```json
  {
    "username": "utilisateur1",
    "password": "motdepasse123"
  }
  ```
- **Réponse** : Token JWT et informations de l'utilisateur

### Déconnexion

- **URL** : `/api/auth/logout`
- **Méthode** : `POST`
- **En-têtes** : `Authorization: Bearer <token>`

### Profil utilisateur

- **URL** : `/api/auth/profile`
- **Méthode** : `GET`
- **En-têtes** : `Authorization: Bearer <token>`

### Mise à jour du profil

- **URL** : `/api/auth/profile`
- **Méthode** : `PUT`
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
  ```json
  {
    "first_name": "Nouveau Prénom",
    "last_name": "Nouveau Nom",
    "email": "nouvel.email@example.com"
  }
  ```

### Liste des utilisateurs (admin uniquement)

- **URL** : `/api/auth/users`
- **Méthode** : `GET`
- **En-têtes** : `Authorization: Bearer <token>`

### Détails d'un utilisateur (admin uniquement)

- **URL** : `/api/auth/users/<user_id>`
- **Méthode** : `GET`
- **En-têtes** : `Authorization: Bearer <token>`

### Mise à jour d'un utilisateur (admin uniquement)

- **URL** : `/api/auth/users/<user_id>`
- **Méthode** : `PUT`
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
  ```json
  {
    "role": "admin",
    "is_active": true
  }
  ```

### Suppression d'un utilisateur (admin uniquement)

- **URL** : `/api/auth/users/<user_id>`
- **Méthode** : `DELETE`
- **En-têtes** : `Authorization: Bearer <token>`

### Rafraîchissement du token

- **URL** : `/api/auth/token/refresh`
- **Méthode** : `POST`
- **En-têtes** : `Authorization: Bearer <token>`

## 2. Gestion des Biens Immobiliers

### Liste des biens immobiliers

- **URL** : `/api/properties/`
- **Méthode** : `GET`
- **Paramètres de requête** :
  - `page` : Numéro de page (défaut: 1)
  - `per_page` : Nombre d'éléments par page (défaut: 10)
  - Filtres : `property_type`, `status`, `city`, `min_price`, `max_price`, `min_area`, `max_area`, `bedrooms`, `bathrooms`, `owner_id`, `transaction_type`

### Détails d'un bien immobilier

- **URL** : `/api/properties/<property_id>`
- **Méthode** : `GET`

### Recherche par code de référence

- **URL** : `/api/properties/reference/<reference_code>`
- **Méthode** : `GET`

### Création d'un bien immobilier

- **URL** : `/api/properties/`
- **Méthode** : `POST`
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
  ```json
  {
    "title": "Appartement 3 pièces",
    "property_type": "apartment",
    "status": "for_sale",
    "address_line1": "123 Rue Exemple",
    "city": "Paris",
    "postal_code": "75001",
    "country": "France",
    "total_area": 75.5,
    "num_bedrooms": 2,
    "num_bathrooms": 1,
    "asking_price": 350000,
    "owner_id": 1
  }
  ```

### Mise à jour d'un bien immobilier

- **URL** : `/api/properties/<property_id>`
- **Méthode** : `PUT`
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
  ```json
  {
    "title": "Appartement 3 pièces rénové",
    "description": "Magnifique appartement entièrement rénové",
    "status": "for_sale",
    "asking_price": 375000
  }
  ```

### Suppression d'un bien immobilier

- **URL** : `/api/properties/<property_id>`
- **Méthode** : `DELETE`
- **En-têtes** : `Authorization: Bearer <token>`

### Ajout d'une image

- **URL** : `/api/properties/<property_id>/images`
- **Méthode** : `POST`
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** : `multipart/form-data`
  - `image` : Fichier image
  - `is_primary` : `true` ou `false`
  - `title` : Titre de l'image
  - `description` : Description de l'image

### Ajout d'un document

- **URL** : `/api/properties/<property_id>/documents`
- **Méthode** : `POST`
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** : `multipart/form-data`
  - `document` : Fichier document
  - `document_type` : Type de document (ex: `title_deed`, `energy_certificate`)
  - `title` : Titre du document
  - `description` : Description du document
  - `expiry_date` : Date d'expiration (format YYYY-MM-DD)

### Liste des équipements

- **URL** : `/api/properties/amenities`
- **Méthode** : `GET`

### Création d'un équipement (admin uniquement)

- **URL** : `/api/properties/amenities`
- **Méthode** : `POST`
- **En-têtes** : `Authorization: Bearer <token>`
- **Corps de la requête** :
  ```json
  {
    "name": "Climatisation",
    "category": "comfort",
    "description": "Système de climatisation réversible"
  }
  ```

## 3. Exemples d'utilisation

### Exemple 1: Inscription et connexion

1. Inscription d'un nouvel utilisateur :
   ```bash
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"agent1", "email":"agent1@example.com", "password":"password123", "first_name":"Jean", "last_name":"Dupont"}'
   ```

2. Connexion avec l'utilisateur créé :
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"agent1", "password":"password123"}'
   ```

3. Récupération du profil avec le token obtenu :
   ```bash
   curl -X GET http://localhost:5000/api/auth/profile \
     -H "Authorization: Bearer <token_obtenu>"
   ```

### Exemple 2: Gestion des biens immobiliers

1. Création d'un bien immobilier :
   ```bash
   curl -X POST http://localhost:5000/api/properties/ \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Villa avec piscine",
       "property_type": "house",
       "status": "for_sale",
       "address_line1": "45 Avenue des Fleurs",
       "city": "Nice",
       "postal_code": "06000",
       "country": "France",
       "total_area": 180,
       "num_bedrooms": 4,
       "num_bathrooms": 2,
       "asking_price": 850000,
       "owner_id": 1
     }'
   ```

2. Récupération de la liste des biens immobiliers avec filtres :
   ```bash
   curl -X GET "http://localhost:5000/api/properties/?property_type=house&min_price=500000&city=Nice&page=1&per_page=10"
   ```

3. Ajout d'une image à un bien immobilier :
   ```bash
   curl -X POST http://localhost:5000/api/properties/1/images \
     -H "Authorization: Bearer <token>" \
     -F "image=@/chemin/vers/image.jpg" \
     -F "is_primary=true" \
     -F "title=Façade principale" \
     -F "description=Vue de la façade principale de la villa"
   ```

### Notes importantes

- Remplacez `<token>` par le token JWT obtenu lors de la connexion.
- Pour les requêtes nécessitant des droits d'administrateur, assurez-vous que l'utilisateur connecté a le rôle "admin".
- Les formats d'image acceptés sont : JPG, JPEG, PNG et GIF.
- Les formats de document acceptés sont : PDF, DOC, DOCX, XLS, XLSX et TXT.
