# Dépendances du Projet de Gestion Immobilière

Ce document détaille les dépendances nécessaires pour notre application de gestion immobilière, en expliquant le rôle de chaque module et pourquoi il est essentiel au projet.

## Dépendances Principales

### Flask et Extensions

**Flask** est le framework web que nous utiliserons comme fondation de notre application. Léger et flexible, il nous permet de construire une application web robuste tout en gardant le contrôle sur l'architecture. Flask suit la philosophie "micro-framework", ce qui signifie qu'il fournit les fonctionnalités de base, mais peut être étendu avec diverses extensions pour répondre à des besoins spécifiques.

**Flask-SQLAlchemy** est une extension qui intègre SQLAlchemy dans Flask. SQLAlchemy est un ORM (Object-Relational Mapper) puissant qui nous permettra d'interagir avec notre base de données PostgreSQL de manière orientée objet. Au lieu d'écrire des requêtes SQL brutes, nous pourrons définir nos modèles de données comme des classes Python et effectuer des opérations de base de données à travers ces objets. Cette abstraction facilite la maintenance du code et réduit les risques d'erreurs liées aux requêtes SQL.

**Flask-Migrate** est basé sur Alembic et nous aidera à gérer les migrations de base de données. Les migrations sont essentielles pour faire évoluer le schéma de notre base de données de manière contrôlée, sans perte de données. Chaque fois que nous modifierons nos modèles, Flask-Migrate générera automatiquement des scripts de migration qui pourront être appliqués ou annulés selon les besoins. Cette approche nous permet de versionner notre schéma de base de données, facilitant ainsi le déploiement et la collaboration entre développeurs.

**Flask-WTF** intègre WTForms dans Flask, nous permettant de créer et valider des formulaires web de manière sécurisée. Cette extension gère automatiquement la protection CSRF (Cross-Site Request Forgery) et offre une API simple pour définir des champs de formulaire et leurs validateurs. Les formulaires sont essentiels pour notre application, car ils seront utilisés pour la saisie et la modification des données immobilières.

**Flask-Login** gère l'authentification des utilisateurs dans notre application. Il fournit des fonctionnalités pour connecter et déconnecter les utilisateurs, protéger les routes qui nécessitent une authentification, et maintenir les sessions utilisateur. Cette extension est cruciale pour sécuriser notre application et offrir une expérience personnalisée aux différents types d'utilisateurs (administrateurs, agents immobiliers, propriétaires, etc.).

**Flask-CORS** (Cross-Origin Resource Sharing) permet de gérer les requêtes cross-origin, ce qui est essentiel si notre API est appelée depuis un domaine différent. Cette extension nous permettra de configurer précisément quels domaines peuvent accéder à notre API et quelles méthodes HTTP sont autorisées, renforçant ainsi la sécurité de notre application.

**Flask-RESTful** simplifie la création d'API RESTful en fournissant des classes et des décorateurs pour définir des ressources et des points d'accès. Cette extension nous aidera à structurer notre API de manière cohérente et à suivre les bonnes pratiques REST, facilitant ainsi l'intégration avec d'autres systèmes ou applications frontales.

### Base de Données et ORM

**psycopg2-binary** est le pilote PostgreSQL pour Python. Il permet à SQLAlchemy de communiquer avec notre base de données PostgreSQL. Ce module est essentiel car il traduit les opérations Python en commandes que PostgreSQL peut comprendre. La version binaire (-binary) est préférée car elle inclut toutes les dépendances nécessaires, simplifiant ainsi l'installation.

**SQLAlchemy** est l'ORM que nous utiliserons pour interagir avec notre base de données. Il offre une abstraction puissante qui nous permet de manipuler les données comme des objets Python, tout en générant automatiquement les requêtes SQL optimisées. SQLAlchemy supporte également des fonctionnalités avancées comme les relations entre tables, les transactions, et les requêtes complexes, ce qui est parfait pour notre application de gestion immobilière qui implique de nombreuses relations entre entités.

**Alembic** est utilisé par Flask-Migrate pour gérer les migrations de base de données. Il permet de créer, appliquer et annuler des scripts de migration, assurant ainsi que notre schéma de base de données évolue de manière contrôlée.

### Sécurité

**Werkzeug** est une bibliothèque WSGI complète qui est utilisée par Flask. Elle fournit des utilitaires pour le hachage de mots de passe, la gestion des sessions, et d'autres fonctionnalités de sécurité. Bien qu'elle soit incluse avec Flask, nous l'utiliserons directement pour certaines fonctionnalités de sécurité comme le hachage des mots de passe.

**PyJWT** (Python JSON Web Tokens) nous permettra d'implémenter l'authentification basée sur les tokens. Les JWT sont des tokens signés qui peuvent contenir des informations sur l'utilisateur et ses permissions, permettant une authentification stateless. Cette approche est particulièrement utile pour les API RESTful comme la nôtre.

**python-dotenv** charge les variables d'environnement à partir d'un fichier .env, ce qui est essentiel pour gérer les configurations sensibles comme les clés secrètes et les informations de connexion à la base de données. Cette approche nous permet de garder ces informations hors du code source, améliorant ainsi la sécurité et facilitant le déploiement dans différents environnements.

### Utilitaires

**Pillow** (PIL Fork) est une bibliothèque de traitement d'images qui nous permettra de gérer les photos des biens immobiliers. Elle offre des fonctionnalités pour redimensionner, recadrer, et optimiser les images, ce qui est essentiel pour une application immobilière où les photos jouent un rôle crucial.

**pandas** est une bibliothèque d'analyse de données qui nous aidera à manipuler et analyser les données immobilières. Elle sera particulièrement utile pour les fonctionnalités de reporting et d'analyse, permettant de générer des insights sur le marché immobilier et les performances des investissements.

**requests** est une bibliothèque HTTP simple mais puissante qui nous permettra d'interagir avec des API externes. Par exemple, nous pourrions l'utiliser pour récupérer des données géographiques ou des informations de marché à partir de services tiers.

**gunicorn** (Green Unicorn) est un serveur WSGI HTTP pour Python, que nous utiliserons pour déployer notre application en production. Contrairement au serveur de développement intégré de Flask, gunicorn est conçu pour gérer des charges de production et offre des fonctionnalités comme le multi-processing et la gestion des signaux.

**pytest** est un framework de test qui nous permettra d'écrire et d'exécuter des tests unitaires et d'intégration pour notre application. Les tests sont essentiels pour garantir la qualité du code et prévenir les régressions lors des évolutions.

## Fichier requirements.txt

Voici le contenu du fichier `requirements.txt` qui liste toutes les dépendances nécessaires pour notre projet :

```
# Framework web
Flask==2.3.3
Flask-RESTful==0.3.10
Flask-CORS==4.0.0

# ORM et base de données
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
Flask-Migrate==4.0.5
alembic==1.12.1

# Formulaires et validation
Flask-WTF==1.2.1
WTForms==3.1.1
email-validator==2.1.0

# Authentification et sécurité
Flask-Login==0.6.3
PyJWT==2.8.0
Werkzeug==2.3.7
python-dotenv==1.0.0

# Traitement d'images et données
Pillow==10.1.0
pandas==2.1.3
numpy==1.26.2

# Utilitaires
requests==2.31.0
marshmallow==3.20.1
Flask-Marshmallow==0.15.0
marshmallow-sqlalchemy==0.29.0

# Serveur de production
gunicorn==21.2.0

# Tests
pytest==7.4.3
pytest-flask==1.3.0
```

## Installation des Dépendances

Pour installer ces dépendances, nous devrons d'abord créer un environnement virtuel Python, puis installer les packages listés dans le fichier requirements.txt. Voici les commandes à exécuter :

```bash
# Création de l'environnement virtuel
python -m venv venv

# Activation de l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
```

L'utilisation d'un environnement virtuel est une bonne pratique car elle permet d'isoler les dépendances de notre projet des autres projets Python sur le même système. Cela évite les conflits de versions et facilite la reproduction de l'environnement de développement sur différentes machines.

## Gestion des Dépendances

Au fur et à mesure que notre projet évoluera, nous pourrons ajouter de nouvelles dépendances selon les besoins. Il est important de maintenir le fichier requirements.txt à jour en ajoutant les nouvelles dépendances avec leurs versions spécifiques. Cela garantit que tous les développeurs travaillent avec les mêmes versions de bibliothèques, réduisant ainsi les problèmes de compatibilité.

Pour mettre à jour le fichier requirements.txt après avoir installé de nouvelles dépendances, nous pouvons utiliser la commande :

```bash
pip freeze > requirements.txt
```

Cette commande capture l'état exact de toutes les dépendances installées dans l'environnement virtuel, y compris les dépendances transitives (les dépendances des dépendances).

Dans la prochaine étape, nous aborderons la modélisation de la base de données, en détaillant les tables nécessaires et leurs relations pour notre application de gestion immobilière.
