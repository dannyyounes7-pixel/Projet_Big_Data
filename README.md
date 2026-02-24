# Big Data IAR Platform - Indice d'Attractivité Rationnelle

[![GitHub](https://img.shields.io/badge/GitHub-Projet_Big_Data-blue?logo=github)](https://github.com/ybakour09-tech/Projet_Big_Data)

> **Dépôt GitHub** : [https://github.com/ybakour09-tech/Projet_Big_Data](https://github.com/ybakour09-tech/Projet_Big_Data)

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
├─ config/              # Fichiers de configuration
│   ├─ app.yaml
│   ├─ spark.yaml
│   ├─ api.yaml
│   └─ logging.yaml
├─ src/
│   ├─ common/          # Utilitaires partagés
│   └─ jobs/            # Jobs Spark (feeder, processor, datamart)
├─ api/                 # API REST FastAPI
│   └─ routes/
├─ viz/                 # Dashboard Streamlit
├─ scripts/             # Scripts d'exécution
├─ logs/                # Logs des jobs
└─ docs/                # Documentation
```

## Installation

### Prérequis

- Python 3.9+
- PostgreSQL 13+
- Java 8+ (pour Spark)
- Apache Spark 3.x

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration de la base de données

```bash
# Créer la base de données
createdb iar_db

# Initialiser les tables (optionnel, créées automatiquement)
psql -d iar_db -f src/sql/create_tables.sql
```

## Utilisation

### 1. Pipeline Big Data Officiel (Architecture Médaillon avec Spark)

Le projet implémente une architecture médaillon complète avec partitionnement par date (`year=YYYY/month=MM/day=DD`).

#### Exécution via Spark-Submit (Recommandé)

```bash
# Windows PowerShell
$RUN_DATE = (Get-Date -Format "yyyy-MM-dd")

# 1. RAW Layer (FEEDER)
spark-submit --master local[*] --driver-memory 4g `
  src/jobs/feeder.py `
  --config config/app.yaml `
  --run_date $RUN_DATE

# 2. SILVER Layer (PROCESSOR)
spark-submit --master local[*] --driver-memory 4g `
  src/jobs/processor.py `
  --config config/app.yaml `
  --run_date $RUN_DATE

# 3. GOLD Layer (DATAMART)
spark-submit --master local[*] --driver-memory 4g `
  src/jobs/datamart.py `
  --config config/app.yaml `
  --run_date $RUN_DATE
```

#### Utilisation des Scripts Shell (Linux/Mac)

```bash
# RAW Layer
./scripts/run_feeder.sh

# SILVER Layer
./scripts/run_processor.sh

# GOLD Layer
./scripts/run_datamart.sh
```

### 2. Alternative Simplifiée (Tests Rapides)

Pour des tests rapides sans architecture distribuée complète :

```bash
# Windows
$env:PYTHONPATH="."; python scripts\run_pipeline.py

# Linux/Mac
PYTHONPATH=. python scripts/run_pipeline.py
```

> ⚠️ **Note:** Cette version simplifiée n'utilise pas spark-submit et ne crée pas le partitionnement par date. Elle est recommandée uniquement pour des tests rapides.

### 3. Lancement de l'API

```bash
# Windows
scripts\run_api.bat

# Linux/Mac
./scripts/run_api.sh

# Ou directement avec uvicorn
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

L'API sera accessible sur : http://localhost:8000
Documentation Swagger : http://localhost:8000/docs

### 4. Lancement du Dashboard

```bash
streamlit run viz/app_frontend.py
```

Le dashboard sera accessible sur : http://localhost:8501

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
GET /stats/correlation
```

## Visualisations

Le dashboard Streamlit propose :
1. **Vue d'ensemble** : KPIs nationaux et top communes
2. **Exploration communes** : Filtres, rankings, détails
3. **Analyse régionale** : Comparaisons macro
4. **Focus départemental** : Top 10 et statistiques
5. **Corrélations** : Matrice prix vs services

## Documentation

- [Architecture détaillée](docs/architecture.md)
- [Dictionnaire de données](docs/data_dictionary.md)
- [Documentation API](docs/api_doc.md)
- [Rapport complet](docs/rapport.md)
- [Guide de lancement complet](GUIDE_LANCEMENT_COMPLET.md)
- [Problématique business](PROBLEMATIQUE_BUSINESS.md)

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

## Logs

Les jobs Spark génèrent automatiquement des logs dans le dossier `logs/` :
- `logs/feeder_YYYYMMDD.txt`
- `logs/processor_YYYYMMDD.txt`
- `logs/datamart_YYYYMMDD.txt`

## Notes Importantes

- Les fichiers de données volumineux (DVF, BPE) ne sont pas versionnés
- Ils doivent être placés à la racine du projet
- Le Data Lake est créé automatiquement lors de l'exécution
- Structure générée : `data_lake/raw|silver|gold/`

## Auteurs

- **Nawfel Chakib Younes** - [@dannyyounes7-pixel](https://github.com/dannyyounes7-pixel)
- **Yacine Bakour** - [@ybakour09-tech](https://github.com/ybakour09-tech)

Projet Big Data Framework - IAR Platform

## Licence

Projet académique
