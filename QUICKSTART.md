# Guide de Démarrage Rapide - IAR Platform

## Installation Rapide

### Prérequis
- Python 3.9+
- Java 8+ (pour Spark)
- PostgreSQL 13+
- Git

### 1. Cloner le Projet
```bash
git clone <repository-url>
cd bigdata-iar
```

### 2. Installer les Dépendances
```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les packages
pip install -r requirements.txt
```

### 3. Configurer PostgreSQL
```bash
# Créer la base de données
createdb iar_db

# Initialiser les tables
./scripts/init_db.sh  # Linux/Mac
psql -U postgres -d iar_db -f src/sql/create_tables.sql  # Windows
```

### 4. Placer les Données
Copier les fichiers de données à la racine du projet:
- `full.xlsx` (DVF 2024)
- `document BPE24.xlsx` (BPE 2024)
- `v_commune_2024.csv` (Référentiel communes)

---

## Exécution du Pipeline

### Option 1: Pipeline Complet (Recommandé)
```bash
./scripts/run_pipeline.sh  # Linux/Mac
```

### Option 2: Étape par Étape

#### Étape 1: RAW Layer
```bash
./scripts/run_feeder.sh  # Linux/Mac
scripts\run_feeder.bat   # Windows
```

#### Étape 2: SILVER Layer
```bash
./scripts/run_processor.sh  # Linux/Mac
scripts\run_processor.bat   # Windows
```

#### Étape 3: GOLD Layer
```bash
./scripts/run_datamart.sh  # Linux/Mac
scripts\run_datamart.bat   # Windows
```

---

## Lancer les Services

### API REST
```bash
./scripts/run_api.sh  # Linux/Mac
scripts\run_api.bat   # Windows

# Ou directement:
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Accès**:
- API: http://localhost:8000
- Documentation Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Dashboard Streamlit
```bash
streamlit run viz/dashboard.py
```

**Accès**: http://localhost:8501

---

## Authentification API

### 1. Obtenir un Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Utiliser le Token
```bash
curl -X GET "http://localhost:8000/communes?page=1&size=10" \
  -H "Authorization: Bearer <votre_token>"
```

**Utilisateurs par défaut**:
- Username: `admin`, Password: `admin123`
- Username: `analyst`, Password: `analyst123`

---

## Structure du Projet

```
bigdata-iar/
├── config/          # Configurations (app, spark, api, logging)
├── src/
│   ├── common/      # Utilitaires partagés
│   ├── jobs/        # Jobs Spark (feeder, processor, datamart)
│   └── sql/         # Scripts SQL
├── api/             # API REST FastAPI
├── viz/             # Dashboard Streamlit
├── scripts/         # Scripts d'exécution
├── logs/            # Logs des jobs
├── docs/            # Documentation
└── data_lake/       # Data Lake (créé automatiquement)
    ├── raw/
    ├── silver/
    └── gold/
```

---

## Vérification

### Vérifier les Logs
```bash
# Logs des jobs
tail -f logs/feeder_*.txt
tail -f logs/processor_*.txt
tail -f logs/datamart_*.txt

# Logs API
tail -f logs/api.txt
```

### Vérifier la Base de Données
```bash
psql -U postgres -d iar_db

# Dans psql:
SELECT COUNT(*) FROM dm_commune_iar;
SELECT * FROM dm_commune_iar ORDER BY iar DESC LIMIT 10;
```

### Vérifier Spark UI
Pendant l'exécution des jobs Spark: http://localhost:4040

---

## Exemples d'Utilisation

### API - Top 10 Communes
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Get top communes
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/communes?page=1&size=10&sort=iar_desc",
    headers=headers
)
communes = response.json()["data"]

for commune in communes:
    print(f"{commune['nom_commune']}: IAR={commune['iar']:.3f}")
```

### Dashboard - Filtres
1. Ouvrir http://localhost:8501
2. Utiliser les filtres dans la sidebar:
   - Sélectionner un département
   - Ajuster la plage IAR
   - Ajuster la plage de prix
3. Explorer les 4 onglets d'analyse

---

## Configuration

### Modifier les Poids IAR
Éditer `config/app.yaml`:
```yaml
processing:
  iar_services_weight: 0.7  # 70% services
  iar_price_weight: 0.3     # 30% prix
```

### Modifier la Base de Données
Éditer `config/api.yaml`:
```yaml
database:
  url: "postgresql://user:password@host:port/database"
```

### Modifier les Paramètres Spark
Éditer `config/spark.yaml`:
```yaml
spark:
  driver:
    memory: "4g"
  executor:
    memory: "4g"
```

---

## Dépannage

### Erreur: "Module not found"
```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur: "Database connection failed"
```bash
# Vérifier que PostgreSQL est démarré
sudo service postgresql status

# Vérifier les credentials dans config/api.yaml
```

### Erreur: "Spark submit failed"
```bash
# Vérifier que Java est installé
java -version

# Vérifier que JAVA_HOME est défini
echo $JAVA_HOME
```

### Erreur: "File not found" (données)
```bash
# Vérifier que les fichiers sont à la racine
ls -lh full.xlsx
ls -lh "document BPE24.xlsx"
ls -lh v_commune_2024.csv
```

---

## Documentation Complète

- **Architecture**: `docs/architecture.md`
- **Dictionnaire de données**: `docs/data_dictionary.md`
- **Documentation API**: `docs/api_doc.md`
- **Rapport complet**: `docs/rapport.md`

---

## Prochaines Étapes

1.  Exécuter le pipeline complet
2.  Tester l'API avec Swagger
3.  Explorer le dashboard
4.  Enregistrer une vidéo de démonstration
5.  Déployer en production (optionnel)

---

## Conseils

- **Première exécution**: Le pipeline peut prendre 10-30 minutes selon la machine
- **Logs**: Toujours vérifier les logs en cas d'erreur
- **Spark UI**: Utiliser pour monitorer les performances
- **Cache**: Le dashboard utilise un cache de 10 minutes
- **Token JWT**: Expire après 60 minutes

---

## Support

Pour toute question ou problème:
1. Consulter les logs dans `logs/`
2. Vérifier la documentation dans `docs/`
3. Consulter le README.md

---

**Bon développement! **
