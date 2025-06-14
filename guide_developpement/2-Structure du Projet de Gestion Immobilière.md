# Structure du Projet de Gestion Immobilière

Ce document détaille la structure des dossiers et fichiers pour notre application de gestion immobilière. Cette organisation suit les bonnes pratiques de développement Flask et permet une maintenance et une évolution faciles du projet.

## Structure Générale

Voici la structure générale que nous allons mettre en place pour notre projet :

```
gestion_immobilier/
│
├── app/                        # Dossier principal de l'application
│   ├── __init__.py             # Initialisation de l'application Flask
│   ├── config.py               # Configuration de l'application
│   ├── models/                 # Modèles de données (ORM)
│   │   ├── __init__.py
│   │   ├── property.py         # Modèle pour les biens immobiliers
│   │   ├── owner.py            # Modèle pour les propriétaires
│   │   ├── client.py           # Modèle pour les clients
│   │   ├── transaction.py      # Modèle pour les transactions
│   │   ├── financial.py        # Modèle pour les données financières
│   │   └── maintenance.py      # Modèle pour la maintenance
│   │
│   ├── routes/                 # Routes et contrôleurs de l'API
│   │   ├── __init__.py
│   │   ├── auth.py             # Routes d'authentification
│   │   ├── properties.py       # Routes pour les biens immobiliers
│   │   ├── owners.py           # Routes pour les propriétaires
│   │   ├── clients.py          # Routes pour les clients
│   │   ├── transactions.py     # Routes pour les transactions
│   │   ├── financials.py       # Routes pour les données financières
│   │   └── maintenance.py      # Routes pour la maintenance
│   │
│   ├── services/               # Services métier
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Service d'authentification
│   │   ├── property_service.py # Service pour les biens immobiliers
│   │   └── ...
│   │
│   ├── static/                 # Fichiers statiques (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── templates/              # Templates HTML (Jinja2)
│       ├── base.html           # Template de base
│       ├── auth/               # Templates d'authentification
│       ├── properties/         # Templates pour les biens immobiliers
│       └── ...
│
├── migrations/                 # Migrations de base de données (Alembic)
│
├── tests/                      # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_routes.py
│   └── ...
│
├── venv/                       # Environnement virtuel Python (à créer)
│
├── .env                        # Variables d'environnement (à créer)
├── .gitignore                  # Fichiers à ignorer par Git
├── requirements.txt            # Dépendances du projet
├── run.py                      # Point d'entrée de l'application
└── README.md                   # Documentation du projet
```

## Explication Détaillée des Composants

### Dossier `app/`

Ce dossier contient le cœur de notre application Flask. Il est organisé selon le principe de la séparation des préoccupations, où chaque composant a une responsabilité spécifique.

#### Fichier `__init__.py`

Ce fichier est crucial car il initialise l'application Flask et configure les différentes extensions. Il sert de point d'entrée pour l'application et relie tous les composants ensemble. Il contient généralement la création de l'instance Flask, l'initialisation des extensions (comme SQLAlchemy pour la base de données, Flask-Login pour l'authentification), et l'enregistrement des blueprints pour les routes.

#### Fichier `config.py`

Ce fichier contient les configurations de l'application pour différents environnements (développement, test, production). Il gère les paramètres comme les connexions à la base de données, les clés secrètes, et d'autres variables d'environnement. L'utilisation d'un fichier de configuration séparé facilite la gestion des différents environnements et améliore la sécurité en centralisant les paramètres sensibles.

#### Dossier `models/`

Ce dossier contient les modèles de données qui représentent les tables de notre base de données PostgreSQL. Chaque fichier correspond à une entité métier spécifique et définit sa structure, ses relations et ses méthodes. Nous utiliserons SQLAlchemy comme ORM (Object-Relational Mapping) pour interagir avec la base de données de manière orientée objet.

#### Dossier `routes/`

Ce dossier contient les contrôleurs de notre application, organisés en blueprints Flask. Chaque fichier gère un ensemble spécifique de routes liées à une fonctionnalité particulière. Les routes définissent les points d'entrée de l'API et gèrent les requêtes HTTP, en déléguant la logique métier aux services.

#### Dossier `services/`

Ce dossier contient la logique métier de notre application, séparée des routes pour une meilleure maintenabilité. Les services encapsulent les opérations complexes et interagissent avec les modèles pour effectuer des opérations sur les données. Cette séparation permet de réutiliser la logique métier à travers différentes routes et facilite les tests unitaires.

#### Dossiers `static/` et `templates/`

Ces dossiers contiennent respectivement les fichiers statiques (CSS, JavaScript, images) et les templates HTML utilisés pour le rendu des pages web. Nous utiliserons Jinja2 comme moteur de templates pour générer dynamiquement le HTML en fonction des données.

### Dossier `migrations/`

Ce dossier contiendra les scripts de migration de base de données générés par Alembic (via Flask-Migrate). Les migrations permettent de versionner le schéma de la base de données et de le faire évoluer de manière contrôlée, sans perte de données.

### Dossier `tests/`

Ce dossier contient les tests unitaires et d'intégration pour notre application. Les tests sont essentiels pour garantir la qualité du code et prévenir les régressions lors des évolutions. Nous utiliserons pytest comme framework de test.

### Fichiers à la racine

- `run.py` : Point d'entrée pour démarrer l'application en mode développement.
- `requirements.txt` : Liste des dépendances Python nécessaires au projet.
- `.env` : Fichier pour stocker les variables d'environnement sensibles (à ne pas committer dans Git).
- `.gitignore` : Liste des fichiers et dossiers à ignorer par Git.
- `README.md` : Documentation principale du projet.

## Avantages de cette Structure

Cette structure présente plusieurs avantages :

1. **Modularité** : Chaque composant a une responsabilité unique et bien définie, ce qui facilite la maintenance et l'évolution du code.

2. **Scalabilité** : L'organisation en modules permet d'ajouter facilement de nouvelles fonctionnalités sans perturber l'existant.

3. **Testabilité** : La séparation des préoccupations facilite l'écriture de tests unitaires et d'intégration.

4. **Lisibilité** : La structure claire du projet permet aux nouveaux développeurs de comprendre rapidement l'organisation du code.

5. **Bonnes pratiques** : Cette structure suit les recommandations et bonnes pratiques de la communauté Flask et Python.

Dans la prochaine étape, nous détaillerons les dépendances à installer et leur rôle dans le projet.
