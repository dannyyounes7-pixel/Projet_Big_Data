# Big Data IAR Platform - Indice d'Attractivit Rationnelle

[![GitHub](https://img.shields.io/badge/GitHub-Projet_Big_Data-blue?logo=github)](https://github.com/dannyyounes7-pixel/Projet_Big_Data)

> ** Dpt GitHub** : [https://github.com/dannyyounes7-pixel/Projet_Big_Data](https://github.com/dannyyounes7-pixel/Projet_Big_Data)

Plateforme Big Data pour analyser les communes franaises et identifier celles offrant le meilleur rapport **services de proximit / prix immobilier**.

## Objectif

Construire une plateforme Big Data complte base sur une architecture mdaillon (RAW  SILVER  GOLD) pour :
- Estimer les prix immobiliers au m par commune (donnes DVF 2024)
- Mesurer la densit des services/quipements de proximit (donnes BPE 2024)
- Calculer un indice IAR combinant ces deux dimensions
- Exposer les rsultats via une API REST scurise (JWT)
- Visualiser les donnes avec des graphiques interactifs

## Formule IAR

```
IAR = 0.7  services_normaliss + 0.3  (1 - prix_normaliss)
```

- **IAR proche de 1** : Commune attractive (services levs, prix raisonnables)
- **IAR proche de 0** : Commune moins attractive (services faibles ou prix levs)

## Architecture Mdaillon

```
SOURCE (DVF + BPE + Communes)
   
RAW (donnes brutes partitionnes par date)
   
SILVER (donnes nettoyes, valides, enrichies)
   
GOLD (datamarts PostgreSQL)
   
API REST (JWT + pagination)
   
Visualisation (Streamlit)
```

## Structure du Projet

```
bigdata-iar/
 config/              # Fichiers de configuration
    app.yaml
    spark.yaml
    api.yaml
    logging.yaml
 src/
    common/          # Utilitaires partags
    jobs/            # Jobs Spark (feeder, processor, datamart)
    sql/             # Scripts SQL
 api/                 # API REST FastAPI
    routes/
    schemas.py
 viz/                 # Dashboard Streamlit
 scripts/             # Scripts d'excution
 logs/                # Logs des jobs
 docs/                # Documentation
```

## Installation

### Prrequis

- Python 3.9+
- PostgreSQL 13+
- Java 8+ (pour Spark)

### Installation des dpendances

```bash
pip install -r requirements.txt
```

### Configuration de la base de donnes

```bash
# Crer la base de donnes
createdb iar_db

# Initialiser les tables
./scripts/init_db.sh
```

## Utilisation

### 1. Ingestion des donnes (RAW)

```bash
spark-submit src/jobs/feeder.py --config config/app.yaml --run_date 2024-02-14
```

### 2. Traitement des donnes (SILVER)

```bash
spark-submit src/jobs/processor.py --config config/app.yaml --run_date 2024-02-14
```

### 3. Cration des datamarts (GOLD)

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

### Dpartements

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
2. **Corrlation prix vs services** (scatter plot)
3. **Rankings dpartementaux** (bar chart)

## Documentation

- [Architecture dtaille](docs/architecture.md)
- [Dictionnaire de donnes](docs/data_dictionary.md)
- [Documentation API](docs/api_doc.md)
- [Rapport complet](docs/rapport.md)

## Technologies

- **Big Data**: Apache Spark (PySpark 3.5)
- **Base de donnes**: PostgreSQL
- **API**: FastAPI + JWT
- **Visualisation**: Streamlit + Plotly
- **Format**: Parquet (compression Snappy)

## Sources de Donnes

- **DVF 2024** : Demandes de Valeurs Foncires (transactions immobilires)
- **BPE 2024** : Base Permanente des quipements (INSEE)
- **Rfrentiel communes** : v_commune_2024.csv

## Notes Importantes

- Les fichiers de donnes volumineux (*.xlsx) ne sont pas versionns
- Ils doivent tre placs  la racine du projet
- Le Data Lake est cr automatiquement lors de l'excution

## Auteurs

Projet Big Data Framework - IAR Platform

## Licence

Projet acadmique

