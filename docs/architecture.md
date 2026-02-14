# Architecture IAR Platform

## Vue d'ensemble

La plateforme IAR (Indice d'Attractivité Rationnelle) suit une architecture médaillon (Medallion Architecture) avec trois couches de traitement des données.

## Architecture Médaillon

```
┌─────────────────────────────────────────────────────────────┐
│                      SOURCES DE DONNÉES                      │
├─────────────────────────────────────────────────────────────┤
│  DVF 2024 (full.xlsx)  │  BPE 2024  │  Communes (CSV)       │
│  43 MB                 │  378 MB    │  3.5 MB               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE RAW (Bronze)                       │
├─────────────────────────────────────────────────────────────┤
│  • Données brutes ingérées sans transformation               │
│  • Format: Parquet (compression Snappy)                      │
│  • Partitionnement: year=YYYY/month=MM/day=DD               │
│  • Job: feeder.py                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  COUCHE SILVER (Silver)                      │
├─────────────────────────────────────────────────────────────┤
│  • Données nettoyées et validées                            │
│  • 7+ règles de validation appliquées                       │
│  • Calculs: prix_m2, scores services                        │
│  • Jointures: DVF × BPE × Communes                          │
│  • Window functions: rankings                                │
│  • Cache/Persist pour performance                           │
│  • Job: processor.py                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   COUCHE GOLD (Gold)                         │
├─────────────────────────────────────────────────────────────┤
│  • Datamarts optimisés pour analyse                         │
│  • Calcul IAR normalisé                                     │
│  • Tables PostgreSQL:                                       │
│    - dm_commune_iar (table principale)                      │
│    - dm_dep_stats (statistiques départementales)            │
│    - dm_time_kpis (séries temporelles)                      │
│  • Job: datamart.py                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      COUCHE API                              │
├─────────────────────────────────────────────────────────────┤
│  • FastAPI avec JWT authentication                          │
│  • Pagination automatique                                   │
│  • Endpoints:                                               │
│    - POST /auth/login                                       │
│    - GET /communes (avec filtres)                           │
│    - GET /communes/{code}                                   │
│    - GET /departements/{dep}/top                            │
│    - GET /stats/summary                                     │
│  • Documentation Swagger auto-générée                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   COUCHE VISUALISATION                       │
├─────────────────────────────────────────────────────────────┤
│  • Dashboard Streamlit interactif                           │
│  • 4 onglets d'analyse                                      │
│  • 6+ graphiques Plotly                                     │
│  • Filtres dynamiques                                       │
└─────────────────────────────────────────────────────────────┘
```

## Flux de Données

### 1. Ingestion (RAW)
- **Input**: Fichiers sources (XLSX, CSV)
- **Process**: Lecture et écriture en Parquet
- **Output**: `data_lake/raw/{dataset}/year=YYYY/month=MM/day=DD/`

### 2. Transformation (SILVER)
- **Input**: Données RAW
- **Process**:
  - Validation (7 règles)
  - Nettoyage
  - Calculs (prix_m2, scores)
  - Jointures
  - Window functions
- **Output**: `data_lake/silver/{dataset}/year=YYYY/month=MM/day=DD/`

### 3. Agrégation (GOLD)
- **Input**: Données SILVER
- **Process**:
  - Normalisation min-max
  - Calcul IAR
  - Rankings
  - Agrégations
- **Output**: Tables PostgreSQL + Parquet backup

## Technologies

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Big Data Processing | Apache Spark (PySpark) | 3.5.0 |
| Base de données | PostgreSQL | 13+ |
| API Framework | FastAPI | 0.109.0 |
| Authentication | JWT (PyJWT) | 2.8.0 |
| Visualisation | Streamlit + Plotly | 1.30.0 |
| Format stockage | Parquet (Snappy) | - |
| Orchestration | Bash/Batch scripts | - |

## Formule IAR

```
IAR = 0.7 × services_norm + 0.3 × (1 - prix_norm)

Où:
- services_norm = (score_services - min) / (max - min)
- prix_norm = (prix_m2 - min) / (max - min)
```

**Interprétation**:
- IAR → 1 : Commune très attractive (services élevés, prix bas)
- IAR → 0 : Commune peu attractive (services faibles, prix élevés)

## Sécurité

- **API**: JWT tokens avec expiration
- **Base de données**: Connection pooling
- **Mots de passe**: Hashing bcrypt (production)
- **CORS**: Configuration restrictive

## Performance

- **Spark**: Cache/Persist sur DataFrames volumineux
- **Partitionnement**: 200 partitions shuffle
- **Compression**: Snappy pour Parquet
- **API**: Connection pooling PostgreSQL
- **Dashboard**: Cache Streamlit (TTL 600s)
