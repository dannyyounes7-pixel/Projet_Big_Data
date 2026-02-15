# Guide Complet de Lancement - IAR Platform

##  Table des Matires

1. [Vue d'ensemble du Projet](#vue-densemble-du-projet)
2. [Prrequis et Installation](#prrequis-et-installation)
3. [Configuration de l'Environnement](#configuration-de-lenvironnement)
4. [Prparation des Donnes](#prparation-des-donnes)
5. [Excution du Pipeline Big Data](#excution-du-pipeline-big-data)
6. [Lancement de l'API REST](#lancement-de-lapi-rest)
7. [Connexion et Utilisation de l'API](#connexion-et-utilisation-de-lapi)
8. [Utilisation des Donnes](#utilisation-des-donnes)
9. [Lancement du Dashboard](#lancement-du-dashboard)
10. [Vrification et Dpannage](#vrification-et-dpannage)

---

## 1. Vue d'ensemble du Projet

### Qu'est-ce que la plateforme IAR ?

La plateforme IAR (Indice d'Attractivit Rationnelle) est une solution Big Data qui analyse les communes franaises pour identifier celles offrant le meilleur rapport **services de proximit / prix immobilier**.

### Architecture du Projet

```

  Donnes Source   (DVF 2024 + BPE 2024 + Communes)

         

   RAW Layer       (Donnes brutes en Parquet)

         

  SILVER Layer     (Donnes nettoyes et enrichies)

         

   GOLD Layer      (Datamarts PostgreSQL)

         

   API REST        (FastAPI + JWT)

         

  Visualisation    (Dashboard Streamlit)

```

### Formule IAR

```
IAR = 0.7  services_normaliss + 0.3  (1 - prix_normaliss)
```

- **IAR proche de 1** : Commune trs attractive (nombreux services, prix raisonnables)
- **IAR proche de 0** : Commune moins attractive (peu de services ou prix levs)

---

## 2. Prrequis et Installation

### 2.1 Vrifier les Prrequis

Avant de commencer, vous devez avoir install :

#### Python 3.9+

```powershell
# Vrifier la version de Python
python --version
```

**Rsultat attendu** : `Python 3.9.x` ou suprieur

Si Python n'est pas install :
```powershell
# Installer Python avec winget
winget install Python.Python.3.11
```

#### Java 8+

```powershell
# Vrifier la version de Java
java -version
```

**Rsultat attendu** : `java version "1.8.x"` ou suprieur

Si Java n'est pas install :
```powershell
# Installer Java avec winget
winget install Oracle.JDK.17
```

#### PostgreSQL 13+

```powershell
# Vrifier PostgreSQL
psql --version
```

**Rsultat attendu** : `psql (PostgreSQL) 13.x` ou suprieur

Si PostgreSQL n'est pas install :
```powershell
# Installer PostgreSQL avec winget
winget install PostgreSQL.PostgreSQL
```

### 2.2 Installer les Dpendances Python

```powershell
# Naviguer vers le rpertoire du projet
cd "c:\Users\33601\Desktop\Projetfinal"

# Crer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
venv\Scripts\activate

# Mettre  jour pip
python -m pip install --upgrade pip

# Installer toutes les dpendances
pip install -r requirements.txt
```

**Rsultat attendu** : Installation russie de tous les packages sans erreurs.

**Packages installs** :
- `pyspark==3.5.0` - Traitement Big Data
- `fastapi==0.109.0` - Framework API
- `streamlit==1.30.0` - Dashboard
- `psycopg2-binary==2.9.9` - Connexion PostgreSQL
- Et bien d'autres...

---

## 3. Configuration de l'Environnement

### 3.1 Configurer PostgreSQL

#### tape 1 : Crer la base de donnes

```powershell
# Se connecter  PostgreSQL
psql -U postgres

# Dans psql, crer la base de donnes
CREATE DATABASE iar_db;

# Vrifier la cration
\l

# Quitter psql
\q
```

**Rsultat attendu** : La base `iar_db` apparat dans la liste des bases de donnes.

#### tape 2 : Initialiser les tables

```powershell
# Excuter le script d'initialisation
psql -U postgres -d iar_db -f src\sql\create_tables.sql
```

**Rsultat attendu** : Messages de cration des tables :
- `CREATE TABLE dm_commune_iar`
- `CREATE TABLE dm_departement_stats`
- `CREATE TABLE dm_region_stats`

#### tape 3 : Vrifier les tables

```powershell
# Se connecter  la base iar_db
psql -U postgres -d iar_db

# Lister les tables
\dt

# Quitter
\q
```

**Rsultat attendu** : Vous devriez voir 3 tables listes.

### 3.2 Configurer les Fichiers de Configuration

Les fichiers de configuration sont dj prts dans le dossier `config/` :

#### `config/app.yaml`
- Chemins du Data Lake
- Configuration de la base de donnes
- Poids de la formule IAR (70% services, 30% prix)

#### `config/api.yaml`
- Configuration du serveur API
- Paramtres JWT
- CORS

#### `config/spark.yaml`
- Mmoire alloue  Spark
- Nombre de partitions

**Vrification** :
```powershell
# Vrifier que les fichiers existent
dir config\*.yaml
```

---

## 4. Prparation des Donnes

### 4.1 Vrifier les Fichiers de Donnes

Les fichiers suivants doivent tre prsents  la racine du projet :

```powershell
# Vrifier les fichiers
dir *.xlsx
dir *.csv
```

**Fichiers requis** :
1. `full.xlsx` (environ 43 MB) - Donnes DVF 2024 (transactions immobilires)
2. `document BPE24.xlsx` (environ 378 MB) - Donnes BPE 2024 (quipements)
3. `v_commune_2024.csv` (environ 3.5 MB) - Rfrentiel des communes

**Rsultat attendu** : Les 3 fichiers sont prsents.

### 4.2 Structure des Donnes

#### DVF 2024 (`full.xlsx`)
Contient les transactions immobilires :
- `code_commune` : Code INSEE de la commune
- `valeur_fonciere` : Prix de vente en euros
- `surface_reelle_bati` : Surface en m
- `nombre_pieces_principales` : Nombre de pices
- `date_mutation` : Date de la transaction

#### BPE 2024 (`document BPE24.xlsx`)
Contient les quipements de proximit :
- `DEPCOM` : Code INSEE de la commune
- `TYPEQU` : Type d'quipement (cole, mdecin, commerce, etc.)
- Environ 200 types d'quipements diffrents

#### Communes (`v_commune_2024.csv`)
Rfrentiel des communes :
- `code_commune` : Code INSEE
- `nom_commune` : Nom de la commune
- `code_departement` : Code du dpartement
- `nom_departement` : Nom du dpartement
- `code_region` : Code de la rgion

---

## 5. Excution du Pipeline Big Data

Le pipeline se compose de 3 tapes principales qui transforment les donnes brutes en datamarts exploitables.

### 5.1 tape 1 : RAW Layer (Feeder)

Cette tape charge les donnes sources et les convertit en format Parquet.

```powershell
# Excuter le feeder
scripts\run_feeder.bat
```

**Ce qui se passe** :
1. Lecture des fichiers Excel et CSV
2. Conversion en format Parquet (compression Snappy)
3. Partitionnement par date d'excution
4. Sauvegarde dans `data_lake/raw/`

**Dure estime** : 5-10 minutes

**Rsultat attendu** :
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

**Vrification** :
```powershell
# Vrifier la cration du Data Lake
dir data_lake\raw\
```

Vous devriez voir 3 dossiers : `dvf`, `bpe`, `ref_communes`

### 5.2 tape 2 : SILVER Layer (Processor)

Cette tape nettoie, valide et enrichit les donnes.

```powershell
# Excuter le processor
scripts\run_processor.bat
```

**Ce qui se passe** :
1. **DVF** :
   - Filtrage des transactions valides (maisons et appartements)
   - Calcul du prix au m
   - Suppression des outliers (1er et 99e percentile)
   - Calcul du prix mdian par commune

2. **BPE** :
   - Comptage des quipements par commune
   - Calcul de la densit de services

3. **Jointure** :
   - Fusion DVF + BPE + Communes
   - Normalisation des valeurs (0-1)
   - Calcul de l'IAR

**Dure estime** : 10-20 minutes

**Rsultat attendu** :
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

**Vrification** :
```powershell
# Vrifier les donnes SILVER
dir data_lake\silver\joined\
```

### 5.3 tape 3 : GOLD Layer (Datamart)

Cette tape charge les donnes finales dans PostgreSQL.

```powershell
# Excuter le datamart
scripts\run_datamart.bat
```

**Ce qui se passe** :
1. Lecture des donnes SILVER
2. Cration de 3 datamarts :
   - `dm_commune_iar` : Donnes par commune
   - `dm_departement_stats` : Statistiques par dpartement
   - `dm_region_stats` : Statistiques par rgion
3. Chargement dans PostgreSQL

**Dure estime** : 5-10 minutes

**Rsultat attendu** :
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

**Vrification** :
```powershell
# Se connecter  PostgreSQL
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

**Rsultat attendu** : Plusieurs milliers de communes dans la table.

### 5.4 Pipeline Complet (Optionnel)

Pour excuter les 3 tapes d'un coup :

```powershell
# Excuter le pipeline complet (Linux/Mac uniquement)
# Sur Windows, excuter les 3 scripts sparment
```

---

## 6. Lancement de l'API REST

### 6.1 Dmarrer l'API

```powershell
# Mthode 1 : Utiliser le script
scripts\run_api.bat

# Mthode 2 : Commande directe
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Rsultat attendu** :
```
==========================================
Starting IAR Platform API
==========================================
INFO:     Will watch for changes in these directories: ['c:\\Users\\33601\\Desktop\\Projetfinal']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 6.2 Vrifier l'API

Ouvrir un navigateur et accder  :

#### Page d'accueil de l'API
```
http://localhost:8000
```

**Rsultat attendu** : JSON avec les informations de l'API

#### Documentation Swagger (Interactive)
```
http://localhost:8000/docs
```

**Rsultat attendu** : Interface Swagger UI avec tous les endpoints

#### Documentation ReDoc
```
http://localhost:8000/redoc
```

**Rsultat attendu** : Documentation alternative en format ReDoc

#### Health Check
```
http://localhost:8000/health
```

**Rsultat attendu** :
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

L'API utilise JWT (JSON Web Tokens) pour scuriser les endpoints.

#### tape 1 : Obtenir un Token

**Mthode 1 : Avec PowerShell**

```powershell
# Crer la requte de login
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

# Envoyer la requte
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# Afficher le token
$token = $response.access_token
Write-Host "Token: $token"
```

**Mthode 2 : Avec Swagger UI**

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
6. Copier le `access_token` de la rponse

**Rsultat attendu** :
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

#### tape 2 : Utiliser le Token

**Dans Swagger UI** :
1. Cliquer sur le bouton "Authorize" (cadenas) en haut  droite
2. Entrer : `Bearer <votre_token>`
3. Cliquer sur "Authorize"
4. Tous les endpoints sont maintenant accessibles

**Avec PowerShell** :
```powershell
# Crer les headers avec le token
$headers = @{
    "Authorization" = "Bearer $token"
}

# Faire une requte protge
$communes = Invoke-RestMethod -Uri "http://localhost:8000/communes?page=1&size=10" `
    -Method Get `
    -Headers $headers

# Afficher les rsultats
$communes.data | Format-Table
```

### 7.2 Endpoints Disponibles

####  Authentication

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

####  Communes

##### GET `/communes`
Lister toutes les communes avec pagination

**Query Parameters** :
- `page` (int, default=1) : Numro de page
- `size` (int, default=50) : Nombre de rsultats par page
- `sort` (string) : Tri (`iar_desc`, `iar_asc`, `prix_asc`, `prix_desc`)
- `dep` (string, optional) : Filtrer par dpartement

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
Dtails d'une commune spcifique

**Exemple** :
```powershell
# Dtails de Paris
$paris = Invoke-RestMethod -Uri "http://localhost:8000/communes/75056" `
    -Headers $headers
```

####  Dpartements

##### GET `/departements/{dep}/top`
Top N communes d'un dpartement

**Query Parameters** :
- `n` (int, default=10) : Nombre de communes

**Exemple** :
```powershell
# Top 10 communes du dpartement 75 (Paris)
$top = Invoke-RestMethod -Uri "http://localhost:8000/departements/75/top?n=10" `
    -Headers $headers
```

##### GET `/departements/{dep}/stats`
Statistiques d'un dpartement

**Exemple** :
```powershell
# Stats du dpartement 75
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

####  Statistiques

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
Statistiques par rgion

---

## 8. Utilisation des Donnes

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

# Rcuprer le top 20
$top20 = Invoke-RestMethod -Uri "http://localhost:8000/communes?page=1&size=20&sort=iar_desc" `
    -Headers $headers

# Afficher sous forme de tableau
$top20.data | Select-Object nom_commune, iar, prix_m2_median, nb_services | Format-Table
```

#### Exemple 2 : Analyser un Dpartement

```powershell
# Top 10 communes du dpartement 69 (Rhne)
$rhone = Invoke-RestMethod -Uri "http://localhost:8000/departements/69/top?n=10" `
    -Headers $headers

# Statistiques du dpartement
$stats = Invoke-RestMethod -Uri "http://localhost:8000/departements/69/stats" `
    -Headers $headers

Write-Host "Dpartement: $($stats.nom_departement)"
Write-Host "Nombre de communes: $($stats.nb_communes)"
Write-Host "IAR moyen: $($stats.iar_moyen)"
Write-Host "Prix m moyen: $($stats.prix_m2_moyen) "
```

#### Exemple 3 : Comparer Plusieurs Communes

```powershell
# Comparer Paris, Lyon, Marseille
$codes = @("75056", "69123", "13055")

foreach ($code in $codes) {
    $commune = Invoke-RestMethod -Uri "http://localhost:8000/communes/$code" `
        -Headers $headers
    
    Write-Host "$($commune.nom_commune): IAR=$($commune.iar), Prix=$($commune.prix_m2_median)/m"
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

# 2. Rcuprer les donnes
def get_top_communes(token, n=50):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/communes",
        params={"page": 1, "size": n, "sort": "iar_desc"},
        headers=headers
    )
    return response.json()["data"]

# 3. Analyser les donnes
def main():
    # Obtenir le token
    token = get_token()
    print(" Authentification russie")
    
    # Rcuprer les top 50 communes
    communes = get_top_communes(token, n=50)
    print(f" {len(communes)} communes rcupres")
    
    # Convertir en DataFrame
    df = pd.DataFrame(communes)
    
    # Afficher les statistiques
    print("\n=== Top 10 Communes par IAR ===")
    print(df[['nom_commune', 'iar', 'prix_m2_median', 'nb_services']].head(10))
    
    # Statistiques globales
    print("\n=== Statistiques ===")
    print(f"IAR moyen: {df['iar'].mean():.3f}")
    print(f"Prix m moyen: {df['prix_m2_median'].mean():.0f} ")
    print(f"Services moyen: {df['nb_services'].mean():.0f}")
    
    # Sauvegarder en CSV
    df.to_csv("top_communes.csv", index=False)
    print("\n Donnes sauvegardes dans top_communes.csv")

if __name__ == "__main__":
    main()
```

**Excution** :
```powershell
python analyse_iar.py
```

### 8.3 Exporter les Donnes

#### Exporter en CSV

```powershell
# Rcuprer toutes les communes et sauvegarder en CSV
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
Write-Host " Donnes exportes dans communes_iar.csv"
```

---

## 9. Lancement du Dashboard

### 9.1 Dmarrer le Dashboard Streamlit

```powershell
# Lancer le dashboard
streamlit run viz\dashboard.py
```

**Rsultat attendu** :
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

### 9.2 Utiliser le Dashboard

Ouvrir le navigateur sur http://localhost:8501

#### Interface du Dashboard

**Sidebar (Barre latrale)** :
-  Filtres :
  - Slection du dpartement
  - Plage IAR (min-max)
  - Plage de prix (min-max)
-  Options d'affichage

**Onglets Principaux** :

1. ** Vue d'ensemble**
   - Top 10 communes par IAR (bar chart)
   - Statistiques globales
   - Carte de France (si disponible)

2. ** Analyse Dtaille**
   - Corrlation prix vs services (scatter plot)
   - Distribution des IAR (histogram)
   - Box plots par rgion

3. ** Analyse Gographique**
   - Rankings dpartementaux
   - Comparaison rgionale
   - Heatmap

4. ** Statistiques**
   - Tableaux dtaills
   - Mtriques cls
   - Export de donnes

### 9.3 Fonctionnalits du Dashboard

- **Filtrage interactif** : Filtrer par dpartement, plage IAR, plage de prix
- **Graphiques dynamiques** : Zoom, pan, hover pour dtails
- **Export** : Tlcharger les graphiques en PNG
- **Cache** : Donnes mises en cache pendant 10 minutes pour performance

---

## 10. Vrification et Dpannage

### 10.1 Vrifications de Sant

#### Vrifier le Data Lake

```powershell
# Vrifier la structure
tree data_lake /F

# Vrifier les tailles
dir data_lake\raw\* -Recurse | Measure-Object -Property Length -Sum
dir data_lake\silver\* -Recurse | Measure-Object -Property Length -Sum
```

#### Vrifier la Base de Donnes

```powershell
# Se connecter
psql -U postgres -d iar_db

# Vrifier les donnes
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

#### Vrifier l'API

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

# Logs de l'API (si configur)
Get-Content logs\api.txt -Tail 50
```

### 10.3 Problmes Courants

#### Problme 1 : "Module not found"

**Cause** : Environnement virtuel non activ ou dpendances manquantes

**Solution** :
```powershell
# Activer l'environnement
venv\Scripts\activate

# Rinstaller les dpendances
pip install -r requirements.txt
```

#### Problme 2 : "Database connection failed"

**Cause** : PostgreSQL non dmarr ou mauvais credentials

**Solution** :
```powershell
# Vrifier le service PostgreSQL
Get-Service postgresql*

# Dmarrer PostgreSQL si ncessaire
Start-Service postgresql-x64-13

# Vrifier les credentials dans config/app.yaml
```

#### Problme 3 : "Spark submit failed"

**Cause** : Java non install ou JAVA_HOME non dfini

**Solution** :
```powershell
# Vrifier Java
java -version

# Dfinir JAVA_HOME (adapter le chemin)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
```

#### Problme 4 : "File not found" (donnes)

**Cause** : Fichiers de donnes manquants

**Solution** :
```powershell
# Vrifier la prsence des fichiers
dir full.xlsx
dir "document BPE24.xlsx"
dir v_commune_2024.csv

# Les placer  la racine du projet si ncessaire
```

#### Problme 5 : "Port already in use"

**Cause** : Port 8000 ou 8501 dj utilis

**Solution** :
```powershell
# Trouver le processus utilisant le port
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F

# Ou utiliser un autre port
python -m uvicorn api.app:app --port 8001
```

#### Problme 6 : "Token expired"

**Cause** : Token JWT expir (dure : 60 minutes)

**Solution** :
```powershell
# Obtenir un nouveau token
$body = @{username="admin"; password="admin123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -ContentType "application/json" -Body $body
$token = $response.access_token
```

### 10.4 Monitoring Spark

Pendant l'excution des jobs Spark, accder  :

```
http://localhost:4040
```

**Informations disponibles** :
- Jobs en cours et termins
- Stages et tasks
- Storage (cache)
- Environment
- Executors
- SQL queries

---

##  Rcapitulatif des Commandes

### Installation
```powershell
cd "c:\Users\33601\Desktop\Projetfinal"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Base de Donnes
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

##  Checklist de Lancement

- [ ] Python 3.9+ install
- [ ] Java 8+ install
- [ ] PostgreSQL 13+ install
- [ ] Dpendances Python installes
- [ ] Base de donnes `iar_db` cre
- [ ] Tables PostgreSQL initialises
- [ ] Fichiers de donnes prsents (full.xlsx, document BPE24.xlsx, v_commune_2024.csv)
- [ ] RAW Layer excut avec succs
- [ ] SILVER Layer excut avec succs
- [ ] GOLD Layer excut avec succs
- [ ] Donnes charges dans PostgreSQL
- [ ] API dmarre sur http://localhost:8000
- [ ] Authentification JWT fonctionnelle
- [ ] Endpoints API tests
- [ ] Dashboard dmarr sur http://localhost:8501
- [ ] Visualisations fonctionnelles

---

##  Ressources Supplmentaires

- **README.md** : Vue d'ensemble du projet
- **QUICKSTART.md** : Guide de dmarrage rapide
- **docs/architecture.md** : Architecture dtaille
- **docs/data_dictionary.md** : Dictionnaire de donnes
- **docs/api_doc.md** : Documentation API complte
- **docs/rapport.md** : Rapport technique complet

---

##  Flicitations !

Vous avez maintenant une plateforme Big Data complte et fonctionnelle pour analyser l'attractivit des communes franaises !

**Prochaines tapes suggres** :
1. Explorer les donnes via le dashboard
2. Crer des analyses personnalises avec l'API
3. Ajuster les poids IAR selon vos besoins
4. Dployer en production (optionnel)
5. Crer une vido de dmonstration

---

**Support** : Pour toute question, consulter les logs dans `logs/` et la documentation dans `docs/`

