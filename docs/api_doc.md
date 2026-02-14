# Documentation API - IAR Platform

## Base URL

```
http://localhost:8000
```

## Authentication

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

### Login

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Utilisation du Token**:

Inclure le token dans le header `Authorization` pour toutes les requêtes protégées:

```
Authorization: Bearer <access_token>
```

### Utilisateurs par défaut

| Username | Password | Email |
|----------|----------|-------|
| admin | admin123 | admin@iar-platform.fr |
| analyst | analyst123 | analyst@iar-platform.fr |

---

## Endpoints

### 1. Communes

#### GET /communes

Récupère une liste paginée de communes avec filtres optionnels.

**Paramètres Query**:
- `page` (int, default=1): Numéro de page
- `size` (int, default=50, max=1000): Taille de page
- `sort` (string, default="iar_desc"): Tri
  - `iar_desc`: IAR décroissant
  - `iar_asc`: IAR croissant
  - `prix_desc`: Prix décroissant
  - `prix_asc`: Prix croissant
  - `services_desc`: Services décroissant
  - `services_asc`: Services croissant
- `dep` (string, optional): Filtre par département
- `reg` (string, optional): Filtre par région
- `iar_min` (float, optional): IAR minimum
- `iar_max` (float, optional): IAR maximum

**Exemple**:
```bash
curl -X GET "http://localhost:8000/communes?page=1&size=10&sort=iar_desc&dep=75" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "data": [
    {
      "code_commune": "75101",
      "nom_commune": "Paris 1er Arrondissement",
      "dep": "75",
      "reg": "11",
      "prix_m2": 12500.50,
      "nb_ventes": 150,
      "score_services_total": 250.5,
      "iar": 0.85,
      "rang_dep": 1,
      "rang_national": 5
    }
  ],
  "pagination": {
    "page": 1,
    "size": 10,
    "total_items": 35000,
    "total_pages": 3500,
    "has_next": true,
    "has_prev": false
  }
}
```

#### GET /communes/{code_commune}

Récupère les détails d'une commune spécifique.

**Paramètres Path**:
- `code_commune` (string): Code INSEE de la commune (5 caractères)

**Exemple**:
```bash
curl -X GET "http://localhost:8000/communes/75101" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "code_commune": "75101",
  "nom_commune": "Paris 1er Arrondissement",
  "dep": "75",
  "reg": "11",
  "prix_m2": 12500.50,
  "nb_ventes": 150,
  "prix_m2_min": 8000.00,
  "prix_m2_max": 18000.00,
  "score_services_total": 250.5,
  "score_sante": 80.0,
  "score_education": 60.0,
  "score_transport": 50.0,
  "score_commerce": 40.5,
  "score_services_publics": 15.0,
  "score_loisirs": 5.0,
  "nb_equipements_total": 120,
  "prix_m2_norm": 0.95,
  "score_services_norm": 0.90,
  "iar": 0.85,
  "rang_dep": 1,
  "rang_reg": 2,
  "rang_national": 5
}
```

---

### 2. Départements

#### GET /departements/{dep}/top

Récupère le top N des communes d'un département par IAR.

**Paramètres Path**:
- `dep` (string): Code département

**Paramètres Query**:
- `n` (int, default=10, max=100): Nombre de communes

**Exemple**:
```bash
curl -X GET "http://localhost:8000/departements/75/top?n=5" \
  -H "Authorization: Bearer <token>"
```

**Response**: Liste de communes (même format que GET /communes)

#### GET /departements/{dep}/stats

Récupère les statistiques d'un département.

**Exemple**:
```bash
curl -X GET "http://localhost:8000/departements/75/stats" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "dep": "75",
  "prix_m2_moyen": 10500.00,
  "prix_m2_median": 9800.00,
  "score_services_moyen": 180.5,
  "iar_moyen": 0.75,
  "nb_communes": 20,
  "nb_ventes_total": 5000,
  "nb_equipements_total": 2500,
  "top_commune_code": "75101",
  "top_commune_name": "Paris 1er Arrondissement",
  "top_commune_iar": 0.85
}
```

#### GET /departements

Récupère les statistiques de tous les départements.

**Paramètres Query**:
- `sort_by` (string, default="iar_moyen"): Champ de tri
- `order` (string, default="desc"): Ordre (asc/desc)

**Exemple**:
```bash
curl -X GET "http://localhost:8000/departements?sort_by=iar_moyen&order=desc" \
  -H "Authorization: Bearer <token>"
```

---

### 3. Statistiques

#### GET /stats/summary

Récupère les statistiques globales de la plateforme.

**Exemple**:
```bash
curl -X GET "http://localhost:8000/stats/summary" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "total_communes": 35000,
  "total_ventes": 500000,
  "total_equipements": 1200000,
  "prix_m2_moyen_national": 3500.00,
  "score_services_moyen_national": 85.5,
  "iar_moyen_national": 0.55,
  "iar_min": 0.10,
  "iar_max": 0.95
}
```

#### GET /stats/regions

Récupère les statistiques agrégées par région.

**Exemple**:
```bash
curl -X GET "http://localhost:8000/stats/regions" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "regions": [
    {
      "reg": "11",
      "nb_communes": 1500,
      "prix_m2_moyen": 8500.00,
      "score_services_moyen": 150.0,
      "iar_moyen": 0.70,
      "iar_min": 0.30,
      "iar_max": 0.90
    }
  ]
}
```

#### GET /stats/correlation

Récupère les données de corrélation prix-services.

**Exemple**:
```bash
curl -X GET "http://localhost:8000/stats/correlation" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "correlation": [
    {
      "prix_categorie": "Bas",
      "services_categorie": "Élevé",
      "nb_communes": 5000,
      "iar_moyen": 0.80
    }
  ]
}
```

---

### 4. Utilitaires

#### GET /health

Health check de l'API (non protégé).

**Exemple**:
```bash
curl -X GET "http://localhost:8000/health"
```

**Response**:
```json
{
  "status": "healthy",
  "service": "IAR Platform API",
  "version": "1.0.0"
}
```

#### GET /me

Récupère les informations de l'utilisateur connecté.

**Exemple**:
```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "username": "admin"
}
```

#### GET /

Endpoint racine avec informations API.

---

## Codes d'Erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 401 | Non authentifié (token manquant ou invalide) |
| 404 | Ressource non trouvée |
| 422 | Erreur de validation |
| 500 | Erreur serveur |

**Exemple d'erreur**:
```json
{
  "detail": "Could not validate credentials"
}
```

---

## Documentation Interactive

Swagger UI disponible à: `http://localhost:8000/docs`

ReDoc disponible à: `http://localhost:8000/redoc`

---

## Exemples d'Utilisation

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Get communes
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/communes?page=1&size=10&sort=iar_desc",
    headers=headers
)
communes = response.json()
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
});
const {access_token} = await loginResponse.json();

// Get communes
const response = await fetch('http://localhost:8000/communes?page=1&size=10', {
  headers: {'Authorization': `Bearer ${access_token}`}
});
const data = await response.json();
```

### cURL

```bash
# Login et sauvegarde du token
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Utilisation du token
curl -X GET "http://localhost:8000/communes?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```
