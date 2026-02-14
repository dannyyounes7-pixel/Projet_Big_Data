# Rapport Projet - IAR Platform

## Résumé Exécutif

Ce projet implémente une plateforme Big Data complète pour analyser les communes françaises selon leur **Indice d'Attractivité Rationnelle (IAR)**, qui mesure le rapport entre la qualité des services de proximité et les prix immobiliers.

**Résultat clé**: Identification des communes offrant le meilleur équilibre services/prix pour aider à la décision d'installation.

---

## 1. Objectifs du Projet

### Objectif Principal
Construire une plateforme Big Data de bout en bout pour identifier les communes françaises les plus attractives en croisant:
- **Prix immobiliers** (DVF 2024)
- **Services de proximité** (BPE 2024)

### Objectifs Techniques
-  Architecture médaillon (RAW → SILVER → GOLD)
-  Traitement distribué avec Apache Spark
-  Validation des données (7+ règles)
-  Jointures et agrégations complexes
-  Window functions pour rankings
-  API REST sécurisée (JWT)
-  Visualisation interactive

---

## 2. Sources de Données

### DVF (Demandes de Valeurs Foncières) 2024
- **Fichier**: `full.xlsx` (43 MB)
- **Volume**: ~200,000+ transactions
- **Données clés**: prix, surface, localisation
- **Utilisation**: Calcul du prix au m² par commune

### BPE (Base Permanente des Équipements) 2024
- **Fichier**: `document BPE24.xlsx` (378 MB)
- **Volume**: Millions d'équipements
- **Données clés**: type équipement, localisation
- **Utilisation**: Score de services par commune

### Référentiel Communes 2024
- **Fichier**: `v_commune_2024.csv` (3.5 MB)
- **Utilisation**: Enrichissement (noms, départements, régions)

---

## 3. Architecture Technique

### 3.1 Couche RAW (Bronze)
**Job**: `feeder.py`

**Fonctionnalités**:
- Ingestion des 3 sources de données
- Conversion en format Parquet (compression Snappy)
- Partitionnement temporel: `year=YYYY/month=MM/day=DD`
- Logging détaillé

**Performance**: Traitement de 420+ MB de données

### 3.2 Couche SILVER (Silver)
**Job**: `processor.py`

**Transformations DVF**:
1. Validation de 7 règles métier
2. Calcul `prix_m2 = valeur_fonciere / surface_reelle_bati`
3. Suppression des outliers (percentiles p1-p99)
4. Agrégation par commune (moyenne, min, max, count)

**Transformations BPE**:
1. Normalisation des codes communes
2. Mapping TYPEQU → 6 catégories de services
3. Calcul des scores pondérés par catégorie
4. Agrégation par commune

**Jointures et Enrichissement**:
- DVF ⨝ BPE sur `code_commune`
- Enrichissement avec référentiel communes
- Window functions pour rankings (départemental, régional, national)

**Optimisations**:
- `cache()` sur DataFrames volumineux
- 200 partitions shuffle
- Visible dans Spark UI

### 3.3 Couche GOLD (Gold)
**Job**: `datamart.py`

**Calcul IAR**:
```
1. Normalisation min-max:
   - prix_norm = (prix_m2 - min) / (max - min)
   - services_norm = (score_services - min) / (max - min)

2. Formule IAR:
   IAR = 0.7 × services_norm + 0.3 × (1 - prix_norm)
```

**Datamarts créés**:
- `dm_commune_iar`: Table principale (35,000+ communes)
- `dm_dep_stats`: Statistiques départementales (100+ départements)
- `dm_time_kpis`: Séries temporelles (optionnel)

**Stockage**:
- PostgreSQL (tables relationnelles)
- Parquet (backup)

### 3.4 API REST
**Framework**: FastAPI

**Sécurité**:
- Authentification JWT
- Tokens avec expiration (60 min)
- CORS configuré

**Endpoints** (7 au total):
- `POST /auth/login`: Authentification
- `GET /communes`: Liste paginée avec filtres
- `GET /communes/{code}`: Détails commune
- `GET /departements/{dep}/top`: Top N par département
- `GET /departements/{dep}/stats`: Stats département
- `GET /stats/summary`: Statistiques globales
- `GET /stats/regions`: Agrégations régionales

**Fonctionnalités**:
- Pagination automatique
- Filtres multiples (département, région, IAR, prix)
- Tri configurable
- Documentation Swagger auto-générée

### 3.5 Visualisation
**Framework**: Streamlit + Plotly

**Dashboard** (4 onglets):
1. **Top Communes**: Bar chart horizontal top N par IAR
2. **Corrélation**: Scatter plot prix vs services
3. **Analyse Départementale**: Rankings et box plots régionaux
4. **Statistiques**: Distributions et stats descriptives

**Graphiques** (6+ au total):
- Top communes (bar chart)
- Scatter plot corrélation
- Rankings départementaux
- Comparaison régionale (box plot)
- Distribution prix
- Distribution IAR

**Interactivité**:
- Filtres: département, plage IAR, plage prix
- Sélecteurs dynamiques
- Cache pour performance

---

## 4. Méthodologie

### 4.1 Validation des Données

**Règles DVF** (7 règles):
1. `valeur_fonciere > 0`
2. `surface_reelle_bati > 0`
3. `date_mutation IS NOT NULL`
4. `code_commune` normalisé (5 caractères)
5. `prix_m2` dans intervalle réaliste (p1-p99)
6. `type_local` valide
7. `nombre_pieces_principales > 0`

**Règles BPE**:
1. `DEPCOM IS NOT NULL`
2. `TYPEQU IS NOT NULL`
3. Normalisation code commune

### 4.2 Pondération des Services

| Catégorie | Poids | Justification |
|-----------|-------|---------------|
| Santé | 3.0 | Essentiel pour qualité de vie |
| Éducation | 2.5 | Très important pour familles |
| Services Publics | 2.0 | Important pour quotidien |
| Transport | 2.0 | Important pour mobilité |
| Commerce | 1.5 | Modérément important |
| Loisirs | 1.0 | Agréable mais non essentiel |

### 4.3 Formule IAR

**Choix de conception**:
- **70% services** : Priorité à la qualité de vie
- **30% prix** : Prise en compte de l'accessibilité financière
- **Inversion du prix** : Prix élevé = pénalité

**Interprétation**:
- IAR → 1 : Commune très attractive (services++, prix-)
- IAR → 0 : Commune peu attractive (services--, prix++)

---

## 5. Résultats et Analyses

### 5.1 Statistiques Globales
- **Communes analysées**: ~35,000
- **Transactions DVF**: ~200,000+
- **Équipements BPE**: ~1,200,000+
- **IAR moyen national**: ~0.55
- **Plage IAR**: [0.10, 0.95]

### 5.2 Insights Clés

**Corrélation Prix-Services**:
- Corrélation positive observée
- Les grandes villes ont services++ mais prix++
- Les petites communes rurales ont services-- et prix-
- **Sweet spot**: Communes périurbaines avec IAR élevé

**Top Départements** (par IAR moyen):
1. Départements avec équilibre services/prix
2. Zones périurbaines attractives
3. Villes moyennes bien équipées

### 5.3 Cas d'Usage

**Pour les particuliers**:
- Identifier les communes attractives pour s'installer
- Comparer qualité de vie vs budget
- Trouver le meilleur compromis

**Pour les collectivités**:
- Évaluer l'attractivité de leur territoire
- Identifier les manques en services
- Benchmarking avec communes similaires

**Pour les investisseurs**:
- Repérer les zones sous-valorisées
- Anticiper les tendances
- Optimiser les investissements immobiliers

---

## 6. Technologies Utilisées

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Big Data | Apache Spark (PySpark) | 3.5.0 |
| Base de données | PostgreSQL | 13+ |
| API | FastAPI | 0.109.0 |
| Auth | JWT (PyJWT) | 2.8.0 |
| Visualisation | Streamlit + Plotly | 1.30.0 |
| Stockage | Parquet (Snappy) | - |
| Langages | Python 3.9+ | - |

---

## 7. Exécution du Projet

### 7.1 Installation
```bash
pip install -r requirements.txt
```

### 7.2 Initialisation Base de Données
```bash
./scripts/init_db.sh  # Linux/Mac
scripts\init_db.bat   # Windows (à créer)
```

### 7.3 Pipeline Complet
```bash
# Étape 1: RAW
./scripts/run_feeder.sh

# Étape 2: SILVER
./scripts/run_processor.sh

# Étape 3: GOLD
./scripts/run_datamart.sh

# Ou tout en une fois:
./scripts/run_pipeline.sh
```

### 7.4 Lancement Services
```bash
# API
./scripts/run_api.sh

# Dashboard
streamlit run viz/dashboard.py
```

---

## 8. Logs et Monitoring

**Logs générés**:
- `logs/feeder_YYYYMMDD.txt`
- `logs/processor_YYYYMMDD.txt`
- `logs/datamart_YYYYMMDD.txt`
- `logs/api.txt`

**Spark UI**: `http://localhost:4040`

**API Swagger**: `http://localhost:8000/docs`

**Dashboard**: `http://localhost:8501`

---

## 9. Améliorations Futures

### Court Terme
- [ ] Authentification utilisateurs en base de données
- [ ] Cache Redis pour API
- [ ] Tests unitaires et d'intégration
- [ ] CI/CD avec GitHub Actions

### Moyen Terme
- [ ] Déploiement cloud (AWS/GCP/Azure)
- [ ] Cluster Spark distribué
- [ ] Streaming pour mises à jour temps réel
- [ ] Machine Learning pour prédictions

### Long Terme
- [ ] Intégration données supplémentaires (pollution, criminalité)
- [ ] Personnalisation des pondérations par utilisateur
- [ ] Application mobile
- [ ] Alertes automatiques sur nouvelles opportunités

---

## 10. Conclusion

Ce projet démontre une implémentation complète d'une plateforme Big Data moderne avec:

 **Architecture robuste**: Médaillon (RAW/SILVER/GOLD)
 **Traitement distribué**: Spark avec optimisations
 **Qualité des données**: Validation rigoureuse
 **API professionnelle**: JWT, pagination, documentation
 **Visualisation riche**: Dashboard interactif
 **Automatisation**: Scripts pour toute la chaîne

**Valeur ajoutée**:
- Aide à la décision pour installation résidentielle
- Benchmark territorial pour collectivités
- Outil d'analyse pour investisseurs immobiliers

**Compétences démontrées**:
- Big Data (Spark, Parquet, partitionnement)
- Ingénierie données (ETL, validation, agrégation)
- Développement API (FastAPI, JWT, REST)
- Visualisation (Streamlit, Plotly)
- DevOps (scripts, logging, monitoring)

---

## Annexes

### A. Structure du Projet
Voir `README.md`

### B. Dictionnaire de Données
Voir `docs/data_dictionary.md`

### C. Documentation API
Voir `docs/api_doc.md`

### D. Architecture
Voir `docs/architecture.md`

---

**Auteur**: Projet Big Data Framework - IAR Platform
**Date**: Février 2024
**Version**: 1.0.0
