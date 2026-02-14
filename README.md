# Big Data IAR Platform - Indice d'Attractivité Rationnelle

Plateforme Big Data pour analyser les communes françaises et identifier celles offrant le meilleur rapport **services de proximité / prix immobilier**.

## Objectif

Construire une plateforme Big Data complète basée sur une architecture médaillon (RAW → SILVER → GOLD) pour :
- Estimer les prix immobiliers au m² par commune (données DVF 2024)
- Mesurer la densité des services/équipements de proximité (données BPE 2024)
- Calculer un indice IAR combinant ces deux dimensions
- Exposer les résultats via une API REST sécurisée (JWT)
- Visualiser les données avec des graphiques interactifs

## Formule IAR

```
IAR = 0.7 × services_normalisés + 0.3 × (1 - prix_normalisés)
```

- **IAR proche de 1** : Commune attractive (services élevés, prix raisonnables)
- **IAR proche de 0** : Commune moins attractive (services faibles ou prix élevés)

## Architecture Médaillon

```
SOURCE (DVF + BPE + Communes)
   ↓
RAW (données brutes partitionnées par date)
   ↓
SILVER (données nettoyées, validées, enrichies)
   ↓
GOLD (datamarts PostgreSQL)
   ↓
API REST (JWT + pagination)
   ↓
Visualisation (Streamlit)
```

## Structure du Projet

```
bigdata-iar/
├── config/              # Fichiers de configuration
│   ├── app.yaml
│   ├── spark.yaml
│   ├── api.yaml
│   └── logging.yaml
├── src/
│   ├── common/          # Utilitaires partagés
│   ├── jobs/            # Jobs Spark (feeder, processor, datamart)
│   └── sql/             # Scripts SQL
├── api/                 # API REST FastAPI
│   ├── routes/
│   └── schemas.py
├── viz/                 # Dashboard Streamlit
├── scripts/             # Scripts d'exécution
├── logs/                # Logs des jobs
└── docs/                # Documentation
```

## Installation

### Prérequis

- Python 3.9+
- PostgreSQL 13+
- Java 8+ (pour Spark)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration de la base de données

```bash
# Créer la base de données
createdb iar_db

# Initialiser les tables
./scripts/init_db.sh
```

## Utilisation

### 1. Ingestion des données (RAW)

```bash
spark-submit src/jobs/feeder.py --config config/app.yaml --run_date 2024-02-14
```

### 2. Traitement des données (SILVER)

```bash
spark-submit src/jobs/processor.py --config config/app.yaml --run_date 2024-02-14
```

### 3. Création des datamarts (GOLD)

```bash
spark-submit src/jobs/datamart.py --config config/app.yaml --run_date 2024-02-14
```

### 4. Lancement de l'API

```bash
./scripts/run_api.sh
# ou
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### 5. Lancement du dashboard

```bash
streamlit run viz/dashboard.py
```

## API Endpoints

### Authentification

```bash
POST /auth/login
```

### Communes

```bash
GET /communes?page=1&size=50&sort=iar_desc
GET /communes/{code_commune}
GET /communes?dep=75&page=1&size=50
```

### Départements

```bash
GET /departements/{dep}/top?n=10
GET /departements/{dep}/stats
```

### Statistiques

```bash
GET /stats/summary
GET /stats/regions
```

## Visualisations

Le dashboard Streamlit propose :
1. **Top 10 communes par IAR** (bar chart)
2. **Corrélation prix vs services** (scatter plot)
3. **Rankings départementaux** (bar chart)

## Documentation

- [Architecture détaillée](docs/architecture.md)
- [Dictionnaire de données](docs/data_dictionary.md)
- [Documentation API](docs/api_doc.md)
- [Rapport complet](docs/rapport.md)

## Technologies

- **Big Data**: Apache Spark (PySpark 3.5)
- **Base de données**: PostgreSQL
- **API**: FastAPI + JWT
- **Visualisation**: Streamlit + Plotly
- **Format**: Parquet (compression Snappy)

## Sources de Données

- **DVF 2024** : Demandes de Valeurs Foncières (transactions immobilières)
- **BPE 2024** : Base Permanente des Équipements (INSEE)
- **Référentiel communes** : v_commune_2024.csv

## Notes Importantes

- Les fichiers de données volumineux (*.xlsx) ne sont pas versionnés
- Ils doivent être placés à la racine du projet
- Le Data Lake est créé automatiquement lors de l'exécution

## Auteurs

Projet Big Data Framework - IAR Platform

## Licence

Projet académique
