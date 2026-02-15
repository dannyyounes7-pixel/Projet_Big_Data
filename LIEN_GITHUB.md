# Lien du Projet - IAR Platform

## Dépôt GitHub

**URL du projet** : https://github.com/dannyyounes7-pixel/Projet_Big_Data

---

## Instructions pour le Professeur

### Cloner le Projet

```bash
git clone https://github.com/dannyyounes7-pixel/Projet_Big_Data.git
cd Projet_Big_Data
```

### Documentation Disponible

Le projet contient 3 documents de référence :

1. **README.md** - Présentation générale du projet et vue d'ensemble technique

2. **GUIDE_LANCEMENT_COMPLET.md** - Guide détaillé étape par étape pour :
   - Installer les prérequis
   - Configurer l'environnement
   - Exécuter le pipeline Big Data (RAW → SILVER → GOLD)
   - Lancer l'API REST
   - Utiliser le dashboard

3. **PROBLEMATIQUE_BUSINESS.md** - Contexte et problématique du projet :
   - Objectifs business
   - Solution IAR (Indice d'Attractivité Rationnelle)
   - Valeur ajoutée
   - Cas d'usage

---

## Structure du Projet

```
Projet_Big_Data/
├── api/                               # API REST FastAPI avec JWT
├── config/                            # Configuration YAML
├── docs/                              # Documentation technique
├── scripts/                           # Scripts d'exécution
├── src/                               # Code source Python (jobs Spark)
├── viz/                               # Dashboard Streamlit
├── requirements.txt                   # Dépendances Python
├── README.md                          # Vue d'ensemble
├── GUIDE_LANCEMENT_COMPLET.md         # Guide de lancement
└── PROBLEMATIQUE_BUSINESS.md          # Documentation business
```

---

## Démarrage Rapide

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration Base de Données

```bash
createdb iar_db
psql -U postgres -d iar_db -f src/sql/create_tables.sql
```

### 3. Exécution du Pipeline

```bash
# RAW Layer
scripts/run_feeder.bat

# SILVER Layer
scripts/run_processor.bat

# GOLD Layer
scripts/run_datamart.bat
```

### 4. Lancement de l'API

```bash
scripts/run_api.bat
# OU
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### 5. Dashboard

```bash
streamlit run viz/dashboard.py
```

---

## Technologies Utilisées

- **Big Data** : Apache Spark (PySpark 3.5)
- **Base de données** : PostgreSQL
- **API** : FastAPI + JWT
- **Visualisation** : Streamlit + Plotly
- **Stockage** : Parquet (Snappy)

---

## Contact

**Auteur** : Danny Younes  
**GitHub** : https://github.com/dannyyounes7-pixel  
**Dépôt** : https://github.com/dannyyounes7-pixel/Projet_Big_Data
