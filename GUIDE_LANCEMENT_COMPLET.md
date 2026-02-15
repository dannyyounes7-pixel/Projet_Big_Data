# Guide Complet de Lancement - IAR Platform

## 📋 Table des Matières

1. [Vue d'ensemble du Projet](#vue-densemble-du-projet)
2. [Prérequis et Installation](#prérequis-et-installation)
3. [Configuration de l'Environnement](#configuration-de-lenvironnement)
4. [Préparation des Données](#préparation-des-données)
5. [Exécution du Pipeline Big Data](#exécution-du-pipeline-big-data)
6. [Lancement de l'API REST](#lancement-de-lapi-rest)
7. [Connexion et Utilisation de l'API](#connexion-et-utilisation-de-lapi)
8. [Utilisation des Données](#utilisation-des-données)
9. [Lancement du Dashboard](#lancement-du-dashboard)
10. [Vérification et Dépannage](#vérification-et-dépannage)

---

## 1. Vue d'ensemble du Projet

### Qu'est-ce que la plateforme IAR ?

La plateforme IAR (Indice d'Attractivité Rationnelle) est une solution Big Data qui analyse les communes françaises pour identifier celles offrant le meilleur rapport **services de proximité / prix immobilier**.

### Architecture du Projet

```
┌─────────────────┐
│  Données Source │  (DVF 2024 + BPE 2024 + Communes)
└────────┬────────┘
         ↓
┌─────────────────┐
│   RAW Layer     │  (Données brutes en Parquet)
└────────┬────────┘
         ↓
┌─────────────────┐
│  SILVER Layer   │  (Données nettoyées et enrichies)
└────────┬────────┘
         ↓
┌─────────────────┐
│   GOLD Layer    │  (Datamarts PostgreSQL)
└────────┬────────┘
         ↓
┌─────────────────┐
│   API REST      │  (FastAPI + JWT)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Visualisation  │  (Dashboard Streamlit)
└─────────────────┘
```

### Formule IAR

```
IAR = 0.7 × services_normalisés + 0.3 × (1 - prix_normalisés)
```

- **IAR proche de 1** : Commune très attractive (nombreux services, prix raisonnables)
- **IAR proche de 0** : Commune moins attractive (peu de services ou prix élevés)

---

## 2. Prérequis et Installation

### 2.1 Vérifier les Prérequis

Avant de commencer, vous devez avoir installé :

#### Python 3.9+

```powershell
# Vérifier la version de Python
python --version
```

**Résultat attendu** : `Python 3.9.x` ou supérieur

Si Python n'est pas installé :
```powershell
# Installer Python avec winget
winget install Python.Python.3.11
```

#### Java 8+

```powershell
# Vérifier la version de Java
java -version
```

**Résultat attendu** : `java version "1.8.x"` ou supérieur

Si Java n'est pas installé :
```powershell
# Installer Java avec winget
winget install Oracle.JDK.17
```

#### PostgreSQL 13+

```powershell
# Vérifier PostgreSQL
psql --version
```

**Résultat attendu** : `psql (PostgreSQL) 13.x` ou supérieur

Si PostgreSQL n'est pas installé :
```powershell
# Installer PostgreSQL avec winget
winget install PostgreSQL.PostgreSQL
```

### 2.2 Installer les Dépendances Python

```powershell
# Naviguer vers le répertoire du projet
cd "c:\Users\33601\Desktop\Projetèfinal"

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
venv\Scripts\activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer toutes les dépendances
pip install -r requirements.txt
```

**Résultat attendu** : Installation réussie de tous les packages sans erreurs.

**Packages installés** :
- `pyspark==3.5.0` - Traitement Big Data
- `fastapi==0.109.0` - Framework API
- `streamlit==1.30.0` - Dashboard
- `psycopg2-binary==2.9.9` - Connexion PostgreSQL
- Et bien d'autres...

---

## 3. Configuration de l'Environnement

### 3.1 Configurer PostgreSQL

#### Étape 1 : Créer la base de données

```powershell
# Se connecter à PostgreSQL
psql -U postgres

# Dans psql, créer la base de données
CREATE DATABASE iar_db;

# Vérifier la création
\l

# Quitter psql
\q
```

**Résultat attendu** : La base `iar_db` apparaît dans la liste des bases de données.

#### Étape 2 : Initialiser les tables

```powershell
# Exécuter le script d'initialisation
psql -U postgres -d iar_db -f src\sql\create_tables.sql
```

**Résultat attendu** : Messages de création des tables :
- `CREATE TABLE dm_commune_iar`
- `CREATE TABLE dm_departement_stats`
- `CREATE TABLE dm_region_stats`

#### Étape 3 : Vérifier les tables

```powershell
# Se connecter à la base iar_db
psql -U postgres -d iar_db

# Lister les tables
\dt

# Quitter
\q
```

**Résultat attendu** : Vous devriez voir 3 tables listées.

### 3.2 Configurer les Fichiers de Configuration

Les fichiers de configuration sont déjà prêts dans le dossier `config/` :

#### `config/app.yaml`
- Chemins du Data Lake
- Configuration de la base de données
- Poids de la formule IAR (70% services, 30% prix)

#### `config/api.yaml`
- Configuration du serveur API
- Paramètres JWT
- CORS

#### `config/spark.yaml`
- Mémoire allouée à Spark
- Nombre de partitions

**Vérification** :
```powershell
# Vérifier que les fichiers existent
dir config\*.yaml
```

---

## 4. Préparation des Données

### 4.1 Vérifier les Fichiers de Données

Les fichiers suivants doivent être présents à la racine du projet :

```powershell
# Vérifier les fichiers
dir *.xlsx
dir *.csv
```

**Fichiers requis** :
1. `full.xlsx` (environ 43 MB) - Données DVF 2024 (transactions immobilières)
2. `document BPE24.xlsx` (environ 378 MB) - Données BPE 2024 (équipements)
3. `v_commune_2024.csv` (environ 3.5 MB) - Référentiel des communes

**Résultat attendu** : Les 3 fichiers sont présents.

### 4.2 Structure des Données

#### DVF 2024 (`full.xlsx`)
Contient les transactions immobilières :
- `code_commune` : Code INSEE de la commune
- `valeur_fonciere` : Prix de vente en euros
- `surface_reelle_bati` : Surface en m²
- `nombre_pieces_principales` : Nombre de pièces
- `date_mutation` : Date de la transaction

#### BPE 2024 (`document BPE24.xlsx`)
Contient les équipements de proximité :
- `DEPCOM` : Code INSEE de la commune
- `TYPEQU` : Type d'équipement (école, médecin, commerce, etc.)
- Environ 200 types d'équipements différents

#### Communes (`v_commune_2024.csv`)
Référentiel des communes :
- `code_commune` : Code INSEE
- `nom_commune` : Nom de la commune
- `code_departement` : Code du département
- `nom_departement` : Nom du département
- `code_region` : Code de la région

---

## 5. Exécution du Pipeline Big Data

Le pipeline se compose de 3 étapes principales qui transforment les données brutes en datamarts exploitables.

### 5.1 Étape 1 : RAW Layer (Feeder)

Cette étape charge les données sources et les convertit en format Parquet.

```powershell
# Exécuter le feeder
scripts\run_feeder.bat
```

**Ce qui se passe** :
1. Lecture des fichiers Excel et CSV
2. Conversion en format Parquet (compression Snappy)
3. Partitionnement par date d'exécution
4. Sauvegarde dans `data_lake/raw/`

**Durée estimée** : 5-10 minutes

**Résultat attendu** :
```
==========================================
Starting RAW Layer Feeder
==========================================
[INFO] Reading DVF data from full.xlsx...
[INFO] Reading BPE data from document BPE24.xlsx...
[INFO] Reading communes data from v_commune_2024.csv...
[INFO] Writing to data_lake/raw/dvf/run_date=2024-02-15/
[INFO] Writing to data_lake/raw/bpe/run_date=2024-02-15/
[INFO] Writing to data_lake/raw/ref_communes/run_date=2024-02-15/
[SUCCESS] Feeder completed successfully!
```

**Vérification** :
```powershell
# Vérifier la création du Data Lake
dir data_lake\raw\
```

Vous devriez voir 3 dossiers : `dvf`, `bpe`, `ref_communes`

### 5.2 Étape 2 : SILVER Layer (Processor)

Cette étape nettoie, valide et enrichit les données.

```powershell
# Exécuter le processor
scripts\run_processor.bat
```

**Ce qui se passe** :
1. **DVF** :
   - Filtrage des transactions valides (maisons et appartements)
   - Calcul du prix au m²
   - Suppression des outliers (1er et 99e percentile)
   - Calcul du prix médian par commune

2. **BPE** :
   - Comptage des équipements par commune
   - Calcul de la densité de services

3. **Jointure** :
   - Fusion DVF + BPE + Communes
   - Normalisation des valeurs (0-1)
   - Calcul de l'IAR

**Durée estimée** : 10-20 minutes

**Résultat attendu** :
```
==========================================
Starting SILVER Layer Processor
==========================================
[INFO] Processing DVF data...
[INFO] Filtering valid transactions...
[INFO] Calculating prix_m2...
[INFO] Removing outliers...
[INFO] Processing BPE data...
[INFO] Counting equipment by commune...
[INFO] Joining datasets...
[INFO] Calculating IAR...
[INFO] Writing to data_lake/silver/joined/
[SUCCESS] Processor completed successfully!
```

**Vérification** :
```powershell
# Vérifier les données SILVER
dir data_lake\silver\joined\
```

### 5.3 Étape 3 : GOLD Layer (Datamart)

Cette étape charge les données finales dans PostgreSQL.

```powershell
# Exécuter le datamart
scripts\run_datamart.bat
```

**Ce qui se passe** :
1. Lecture des données SILVER
2. Création de 3 datamarts :
   - `dm_commune_iar` : Données par commune
   - `dm_departement_stats` : Statistiques par département
   - `dm_region_stats` : Statistiques par région
3. Chargement dans PostgreSQL

**Durée estimée** : 5-10 minutes

**Résultat attendu** :
```
==========================================
Starting GOLD Layer Datamart
==========================================
[INFO] Reading SILVER data...
[INFO] Creating commune datamart...
[INFO] Creating departement datamart...
[INFO] Creating region datamart...
[INFO] Loading to PostgreSQL...
[SUCCESS] Datamart completed successfully!
```

**Vérification** :
```powershell
# Se connecter à PostgreSQL
psql -U postgres -d iar_db

# Compter les communes
SELECT COUNT(*) FROM dm_commune_iar;

# Voir les top 10 communes
SELECT nom_commune, iar, prix_m2_median, nb_services 
FROM dm_commune_iar 
ORDER BY iar DESC 
LIMIT 10;

# Quitter
\q
```

**Résultat attendu** : Plusieurs milliers de communes dans la table.

### 5.4 Pipeline Complet (Optionnel)

Pour exécuter les 3 étapes d'un coup :

```powershell
# Exécuter le pipeline complet (Linux/Mac uniquement)
# Sur Windows, exécuter les 3 scripts séparément
```

---

## 6. Lancement de l'API REST

### 6.1 Démarrer l'API

```powershell
# Méthode 1 : Utiliser le script
scripts\run_api.bat

# Méthode 2 : Commande directe
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Résultat attendu** :
```
==========================================
Starting IAR Platform API
==========================================
INFO:     Will watch for changes in these directories: ['c:\\Users\\33601\\Desktop\\Projetèfinal']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 6.2 Vérifier l'API

Ouvrir un navigateur et accéder à :

#### Page d'accueil de l'API
```
http://localhost:8000
```

**Résultat attendu** : JSON avec les informations de l'API

#### Documentation Swagger (Interactive)
```
http://localhost:8000/docs
```

**Résultat attendu** : Interface Swagger UI avec tous les endpoints

#### Documentation ReDoc
```
http://localhost:8000/redoc
```

**Résultat attendu** : Documentation alternative en format ReDoc

#### Health Check
```
http://localhost:8000/health
```

**Résultat attendu** :
```json
{
  "status": "healthy",
  "service": "IAR Platform API",
  "version": "1.0.0"
}
```

---

## 7. Connexion et Utilisation de l'API

### 7.1 Authentification JWT

L'API utilise JWT (JSON Web Tokens) pour sécuriser les endpoints.

#### Étape 1 : Obtenir un Token

**Méthode 1 : Avec PowerShell**

```powershell
# Créer la requête de login
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

# Envoyer la requête
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# Afficher le token
$token = $response.access_token
Write-Host "Token: $token"
```

**Méthode 2 : Avec Swagger UI**

1. Aller sur http://localhost:8000/docs
2. Cliquer sur `POST /auth/login`
3. Cliquer sur "Try it out"
4. Entrer les credentials :
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. Cliquer sur "Execute"
6. Copier le `access_token` de la réponse

**Résultat attendu** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Utilisateurs Disponibles

| Username | Password | Description |
|----------|----------|-------------|
| `admin` | `admin123` | Administrateur |
| `analyst` | `analyst123` | Analyste |

#### Étape 2 : Utiliser le Token

**Dans Swagger UI** :
1. Cliquer sur le bouton "Authorize" (cadenas) en haut à droite
2. Entrer : `Bearer <votre_token>`
3. Cliquer sur "Authorize"
4. Tous les endpoints sont maintenant accessibles

**Avec PowerShell** :
```powershell
# Créer les headers avec le token
$headers = @{
    "Authorization" = "Bearer $token"
}

# Faire une requête protégée
$communes = Invoke-RestMethod -Uri "http://localhost:8000/communes?page=1&size=10" `
    -Method Get `
    -Headers $headers

# Afficher les résultats
$communes.data | Format-Table
```

### 7.2 Endpoints Disponibles

#### 🔐 Authentication

##### POST `/auth/login`
Obtenir un token JWT

**Request Body** :
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 🏘️ Communes

##### GET `/communes`
Lister toutes les communes avec pagination

**Query Parameters** :
- `page` (int, default=1) : Numéro de page
- `size` (int, default=50) : Nombre de résultats par page
- `sort` (string) : Tri (`iar_desc`, `iar_asc`, `prix_asc`, `prix_desc`)
- `dep` (string, optional) : Filtrer par département

**Exemple** :
```powershell
# Top 10 communes par IAR
$communes = Invoke-RestMethod -Uri "http://localhost:8000/communes?page=1&size=10&sort=iar_desc" `
    -Headers $headers
```

**Response** :
```json
{
  "data": [
    {
      "code_commune": "75056",
      "nom_commune": "Paris",
      "code_departement": "75",
      "nom_departement": "Paris",
      "code_region": "11",
      "iar": 0.856,
      "prix_m2_median": 9500.0,
      "nb_services": 1250,
      "services_normalises": 0.95,
      "prix_normalises": 0.78
    }
  ],
  "total": 35000,
  "page": 1,
  "size": 10,
  "pages": 3500
}
```

##### GET `/communes/{code_commune}`
Détails d'une commune spécifique

**Exemple** :
```powershell
# Détails de Paris
$paris = Invoke-RestMethod -Uri "http://localhost:8000/communes/75056" `
    -Headers $headers
```

#### 🗺️ Départements

##### GET `/departements/{dep}/top`
Top N communes d'un département

**Query Parameters** :
- `n` (int, default=10) : Nombre de communes

**Exemple** :
```powershell
# Top 10 communes du département 75 (Paris)
$top = Invoke-RestMethod -Uri "http://localhost:8000/departements/75/top?n=10" `
    -Headers $headers
```

##### GET `/departements/{dep}/stats`
Statistiques d'un département

**Exemple** :
```powershell
# Stats du département 75
$stats = Invoke-RestMethod -Uri "http://localhost:8000/departements/75/stats" `
    -Headers $headers
```

**Response** :
```json
{
  "code_departement": "75",
  "nom_departement": "Paris",
  "nb_communes": 1,
  "iar_moyen": 0.856,
  "prix_m2_moyen": 9500.0,
  "nb_services_moyen": 1250.0
}
```

#### 📊 Statistiques

##### GET `/stats/summary`
Statistiques globales

**Exemple** :
```powershell
$summary = Invoke-RestMethod -Uri "http://localhost:8000/stats/summary" `
    -Headers $headers
```

**Response** :
```json
{
  "total_communes": 35000,
  "iar_moyen": 0.45,
  "prix_m2_moyen": 2500.0,
  "nb_services_moyen": 50.0,
  "top_commune": {
    "code_commune": "75056",
    "nom_commune": "Paris",
    "iar": 0.856
  }
}
```

##### GET `/stats/regions`
Statistiques par région

---

## 8. Utilisation des Données

### 8.1 Exemples avec PowerShell

#### Exemple 1 : Trouver les Communes les Plus Attractives

```powershell
# Se connecter
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$token = $response.access_token
$headers = @{ "Authorization" = "Bearer $token" }

# Récupérer le top 20
$top20 = Invoke-RestMethod -Uri "http://localhost:8000/communes?page=1&size=20&sort=iar_desc" `
    -Headers $headers

# Afficher sous forme de tableau
$top20.data | Select-Object nom_commune, iar, prix_m2_median, nb_services | Format-Table
```

#### Exemple 2 : Analyser un Département

```powershell
# Top 10 communes du département 69 (Rhône)
$rhone = Invoke-RestMethod -Uri "http://localhost:8000/departements/69/top?n=10" `
    -Headers $headers

# Statistiques du département
$stats = Invoke-RestMethod -Uri "http://localhost:8000/departements/69/stats" `
    -Headers $headers

Write-Host "Département: $($stats.nom_departement)"
Write-Host "Nombre de communes: $($stats.nb_communes)"
Write-Host "IAR moyen: $($stats.iar_moyen)"
Write-Host "Prix m² moyen: $($stats.prix_m2_moyen) €"
```

#### Exemple 3 : Comparer Plusieurs Communes

```powershell
# Comparer Paris, Lyon, Marseille
$codes = @("75056", "69123", "13055")

foreach ($code in $codes) {
    $commune = Invoke-RestMethod -Uri "http://localhost:8000/communes/$code" `
        -Headers $headers
    
    Write-Host "$($commune.nom_commune): IAR=$($commune.iar), Prix=$($commune.prix_m2_median)€/m²"
}
```

### 8.2 Exemples avec Python

#### Script Python Complet

```python
import requests
import pandas as pd

# Configuration
BASE_URL = "http://localhost:8000"

# 1. Authentification
def get_token():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]

# 2. Récupérer les données
def get_top_communes(token, n=50):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/communes",
        params={"page": 1, "size": n, "sort": "iar_desc"},
        headers=headers
    )
    return response.json()["data"]

# 3. Analyser les données
def main():
    # Obtenir le token
    token = get_token()
    print("✓ Authentification réussie")
    
    # Récupérer les top 50 communes
    communes = get_top_communes(token, n=50)
    print(f"✓ {len(communes)} communes récupérées")
    
    # Convertir en DataFrame
    df = pd.DataFrame(communes)
    
    # Afficher les statistiques
    print("\n=== Top 10 Communes par IAR ===")
    print(df[['nom_commune', 'iar', 'prix_m2_median', 'nb_services']].head(10))
    
    # Statistiques globales
    print("\n=== Statistiques ===")
    print(f"IAR moyen: {df['iar'].mean():.3f}")
    print(f"Prix m² moyen: {df['prix_m2_median'].mean():.0f} €")
    print(f"Services moyen: {df['nb_services'].mean():.0f}")
    
    # Sauvegarder en CSV
    df.to_csv("top_communes.csv", index=False)
    print("\n✓ Données sauvegardées dans top_communes.csv")

if __name__ == "__main__":
    main()
```

**Exécution** :
```powershell
python analyse_iar.py
```

### 8.3 Exporter les Données

#### Exporter en CSV

```powershell
# Récupérer toutes les communes et sauvegarder en CSV
$allCommunes = @()
$page = 1
$totalPages = 1

do {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/communes?page=$page&size=100" `
        -Headers $headers
    
    $allCommunes += $response.data
    $totalPages = $response.pages
    $page++
    
    Write-Host "Page $page/$totalPages"
} while ($page -le $totalPages)

# Exporter en CSV
$allCommunes | Export-Csv -Path "communes_iar.csv" -NoTypeInformation
Write-Host "✓ Données exportées dans communes_iar.csv"
```

---

## 9. Lancement du Dashboard

### 9.1 Démarrer le Dashboard Streamlit

```powershell
# Lancer le dashboard
streamlit run viz\dashboard.py
```

**Résultat attendu** :
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

### 9.2 Utiliser le Dashboard

Ouvrir le navigateur sur http://localhost:8501

#### Interface du Dashboard

**Sidebar (Barre latérale)** :
- 🔍 Filtres :
  - Sélection du département
  - Plage IAR (min-max)
  - Plage de prix (min-max)
- 📊 Options d'affichage

**Onglets Principaux** :

1. **📈 Vue d'ensemble**
   - Top 10 communes par IAR (bar chart)
   - Statistiques globales
   - Carte de France (si disponible)

2. **🔍 Analyse Détaillée**
   - Corrélation prix vs services (scatter plot)
   - Distribution des IAR (histogram)
   - Box plots par région

3. **🗺️ Analyse Géographique**
   - Rankings départementaux
   - Comparaison régionale
   - Heatmap

4. **📊 Statistiques**
   - Tableaux détaillés
   - Métriques clés
   - Export de données

### 9.3 Fonctionnalités du Dashboard

- **Filtrage interactif** : Filtrer par département, plage IAR, plage de prix
- **Graphiques dynamiques** : Zoom, pan, hover pour détails
- **Export** : Télécharger les graphiques en PNG
- **Cache** : Données mises en cache pendant 10 minutes pour performance

---

## 10. Vérification et Dépannage

### 10.1 Vérifications de Santé

#### Vérifier le Data Lake

```powershell
# Vérifier la structure
tree data_lake /F

# Vérifier les tailles
dir data_lake\raw\* -Recurse | Measure-Object -Property Length -Sum
dir data_lake\silver\* -Recurse | Measure-Object -Property Length -Sum
```

#### Vérifier la Base de Données

```powershell
# Se connecter
psql -U postgres -d iar_db

# Vérifier les données
SELECT 
    'dm_commune_iar' as table_name,
    COUNT(*) as row_count
FROM dm_commune_iar
UNION ALL
SELECT 
    'dm_departement_stats',
    COUNT(*)
FROM dm_departement_stats
UNION ALL
SELECT 
    'dm_region_stats',
    COUNT(*)
FROM dm_region_stats;

# Quitter
\q
```

#### Vérifier l'API

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Tester l'authentification
$body = @{username="admin"; password="admin123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -ContentType "application/json" -Body $body
```

### 10.2 Consulter les Logs

```powershell
# Logs des jobs Spark
Get-Content logs\feeder_*.txt -Tail 50
Get-Content logs\processor_*.txt -Tail 50
Get-Content logs\datamart_*.txt -Tail 50

# Logs de l'API (si configuré)
Get-Content logs\api.txt -Tail 50
```

### 10.3 Problèmes Courants

#### Problème 1 : "Module not found"

**Cause** : Environnement virtuel non activé ou dépendances manquantes

**Solution** :
```powershell
# Activer l'environnement
venv\Scripts\activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

#### Problème 2 : "Database connection failed"

**Cause** : PostgreSQL non démarré ou mauvais credentials

**Solution** :
```powershell
# Vérifier le service PostgreSQL
Get-Service postgresql*

# Démarrer PostgreSQL si nécessaire
Start-Service postgresql-x64-13

# Vérifier les credentials dans config/app.yaml
```

#### Problème 3 : "Spark submit failed"

**Cause** : Java non installé ou JAVA_HOME non défini

**Solution** :
```powershell
# Vérifier Java
java -version

# Définir JAVA_HOME (adapter le chemin)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
```

#### Problème 4 : "File not found" (données)

**Cause** : Fichiers de données manquants

**Solution** :
```powershell
# Vérifier la présence des fichiers
dir full.xlsx
dir "document BPE24.xlsx"
dir v_commune_2024.csv

# Les placer à la racine du projet si nécessaire
```

#### Problème 5 : "Port already in use"

**Cause** : Port 8000 ou 8501 déjà utilisé

**Solution** :
```powershell
# Trouver le processus utilisant le port
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F

# Ou utiliser un autre port
python -m uvicorn api.app:app --port 8001
```

#### Problème 6 : "Token expired"

**Cause** : Token JWT expiré (durée : 60 minutes)

**Solution** :
```powershell
# Obtenir un nouveau token
$body = @{username="admin"; password="admin123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -ContentType "application/json" -Body $body
$token = $response.access_token
```

### 10.4 Monitoring Spark

Pendant l'exécution des jobs Spark, accéder à :

```
http://localhost:4040
```

**Informations disponibles** :
- Jobs en cours et terminés
- Stages et tasks
- Storage (cache)
- Environment
- Executors
- SQL queries

---

## 📝 Récapitulatif des Commandes

### Installation
```powershell
cd "c:\Users\33601\Desktop\Projetèfinal"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Base de Données
```powershell
createdb iar_db
psql -U postgres -d iar_db -f src\sql\create_tables.sql
```

### Pipeline Big Data
```powershell
scripts\run_feeder.bat      # RAW Layer
scripts\run_processor.bat   # SILVER Layer
scripts\run_datamart.bat    # GOLD Layer
```

### API
```powershell
scripts\run_api.bat
# ou
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Dashboard
```powershell
streamlit run viz\dashboard.py
```

### Authentification
```powershell
# Login
$body = @{username="admin"; password="admin123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -ContentType "application/json" -Body $body
$token = $response.access_token

# Utiliser le token
$headers = @{"Authorization" = "Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/communes?page=1&size=10" -Headers $headers
```

---

## 🎯 Checklist de Lancement

- [ ] Python 3.9+ installé
- [ ] Java 8+ installé
- [ ] PostgreSQL 13+ installé
- [ ] Dépendances Python installées
- [ ] Base de données `iar_db` créée
- [ ] Tables PostgreSQL initialisées
- [ ] Fichiers de données présents (full.xlsx, document BPE24.xlsx, v_commune_2024.csv)
- [ ] RAW Layer exécuté avec succès
- [ ] SILVER Layer exécuté avec succès
- [ ] GOLD Layer exécuté avec succès
- [ ] Données chargées dans PostgreSQL
- [ ] API démarrée sur http://localhost:8000
- [ ] Authentification JWT fonctionnelle
- [ ] Endpoints API testés
- [ ] Dashboard démarré sur http://localhost:8501
- [ ] Visualisations fonctionnelles

---

## 📚 Ressources Supplémentaires

- **README.md** : Vue d'ensemble du projet
- **QUICKSTART.md** : Guide de démarrage rapide
- **docs/architecture.md** : Architecture détaillée
- **docs/data_dictionary.md** : Dictionnaire de données
- **docs/api_doc.md** : Documentation API complète
- **docs/rapport.md** : Rapport technique complet

---

## 🎉 Félicitations !

Vous avez maintenant une plateforme Big Data complète et fonctionnelle pour analyser l'attractivité des communes françaises !

**Prochaines étapes suggérées** :
1. Explorer les données via le dashboard
2. Créer des analyses personnalisées avec l'API
3. Ajuster les poids IAR selon vos besoins
4. Déployer en production (optionnel)
5. Créer une vidéo de démonstration

---

**Support** : Pour toute question, consulter les logs dans `logs/` et la documentation dans `docs/`
