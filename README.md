# tunisieAnnonceScrapping
Ce projet est une API REST développée avec FastAPI qui permet de scraper et gérer les annonces immobilières du site Tunisie Annonce. L'application automatise la collecte des données immobilières et les rend accessibles via une API structurée.
Ce projet comporte deux parties principales :
-Scraping des données : Extraction des annonces immobilières depuis une source en ligne (par exemple, un site d'annonces).
-Tableau de bord de visualisation : Un tableau de bord interactif construit avec Dash et Plotly pour analyser et visualiser les données d'annonces immobilières.
### Prérequis
Avant d'exécuter cette application, vous devez avoir installé les outils suivants sur votre machine :
- [Python 3.x](https://www.python.org/downloads/) (si vous ne l'avez pas déjà installé)
- [PostgreSQL](https://www.postgresql.org/download/) (si vous prévoyez d'utiliser la fonctionnalité d'enregistrement dans PostgreSQL)
- pip (Gestionnaire de paquets Python)
## Technologies Utilisées

- **Scraping** : BeautifulSoup et Requests
- **Base de Données** : PostgreSQL
- **API** : Flask (REST API)
  -
### Configuration

1. **Base de données PostgreSQL** :
   - Créez une base de données PostgreSQL appelée `tunisie_annonce`.
   - Configurez les paramètres de connexion dans le fichier `scraper.py` pour correspondre à votre installation de PostgreSQL.
   

## Installation et Exécution
1. Clonez ce dépôt sur votre machine locale :
    git clone https://github.com/BennourNour/tunisieAnnonceScrapping.git
    cd projet-tunisie-annonce
2. Installez les dépendances nécessaires :
    pip install -r requirements.txt
### Exécution de l'application

1. Lancez l'application Flask en exécutant le fichier `app.py` :
    python api/app.py

2. L'application sera accessible à l'adresse suivante :
    http://127.0.0.1:5000/

## Fonctionnalités
### . API REST
- Endpoints disponibles :
  - `GET /` : Page d'accueil avec documentation des endpoints
  - `GET /annonces` : Récupération de toutes les annonces
  - `POST /scrape` : Déclenchement d'une nouvelle session de scraping
 - Liste des annonces : `http://localhost:8000/annonces`
- Lancer le scraping : `POST http://localhost:8000/scrape`



# Tableau de Bord Immobilier

Ce projet crée un tableau de bord interactif pour l'analyse des annonces immobilières en Tunisie. Le tableau de bord permet de visualiser des données relatives aux prix des propriétés, aux types de biens, et aux localisations, le tout à travers des graphiques interactifs.

## Fonctionnalités

- **Exploration des données** : Affiche les données des annonces immobilières, y compris le titre, le prix, la localisation et le type de bien.
- **Filtres dynamiques** : Permet aux utilisateurs de filtrer les données par ville, type de bien et plage de prix.
- **Visualisations interactives** :
    - Top 10 des villes avec le plus grand nombre d'annonces.
    - Distribution des prix des propriétés.
    - Répartition des types de biens (appartements, villas, terrains, etc.).

## Prérequis
- Les bibliothèques pour la creation de tableau de bord  :
    - Dash
    - Pandas
    - Plotly
    - NumPy

Vous pouvez installer les dépendances nécessaires en utilisant le fichier `requirements.txt` :
pip install -r requirements.txt

-annonces_nettoyees_nouveau.csv : Fichier CSV contenant les données après nettoyage (utilisé dans l'application).
