# Dictionnaire de Données - IAR Platform

## Sources de Données

### DVF (Demandes de Valeurs Foncières) 2024

Fichier: `full.xlsx` (43 MB)

| Colonne | Type | Description |
|---------|------|-------------|
| date_mutation | Date | Date de la transaction immobilière |
| valeur_fonciere | Decimal | Valeur de la transaction en euros |
| code_commune | String(5) | Code INSEE de la commune |
| surface_reelle_bati | Decimal | Surface réelle bâtie en m² |
| nombre_pieces_principales | Integer | Nombre de pièces principales |
| type_local | String | Type de bien (Maison, Appartement, etc.) |
| nature_mutation | String | Nature de la mutation (Vente, etc.) |

### BPE (Base Permanente des Équipements) 2024

Fichier: `document BPE24.xlsx` (378 MB)

| Colonne | Type | Description |
|---------|------|-------------|
| DEPCOM | String | Code commune (à normaliser sur 5 caractères) |
| TYPEQU | String | Code type d'équipement |
| NB_EQUIP | Integer | Nombre d'équipements |

**Catégories TYPEQU**:
- **Santé** (D2xx, D3xx): Médecins, pharmacies, hôpitaux
- **Éducation** (C1xx, C2xx, C3xx): Écoles, collèges, lycées, universités
- **Transport** (E1xx): Gares, aéroports
- **Commerce** (B1xx, B2xx, B3xx): Supermarchés, commerces de proximité
- **Services Publics** (A1xx, A2xx, A3xx, A4xx, A5xx): Mairies, postes, banques
- **Loisirs** (F1xx, F2xx, F3xx): Cinémas, sports, culture

### Référentiel Communes 2024

Fichier: `v_commune_2024.csv` (3.5 MB)

| Colonne | Type | Description |
|---------|------|-------------|
| COM/CODGEO | String(5) | Code commune INSEE |
| LIBELLE/NOM | String | Nom de la commune |
| DEP | String(3) | Code département |
| REG | String(2) | Code région |

## Couche SILVER

### DVF Silver

| Colonne | Type | Description |
|---------|------|-------------|
| code_commune | String(5) | Code commune normalisé |
| prix_m2_moyen | Decimal | Prix moyen au m² |
| nb_ventes | Integer | Nombre de transactions |
| prix_m2_min | Decimal | Prix minimum au m² |
| prix_m2_max | Decimal | Prix maximum au m² |
| valeur_fonciere_moyenne | Decimal | Valeur foncière moyenne |
| surface_moyenne | Decimal | Surface moyenne |

### BPE Silver

| Colonne | Type | Description |
|---------|------|-------------|
| code_commune | String(5) | Code commune normalisé |
| score_sante | Decimal | Score pondéré santé |
| score_education | Decimal | Score pondéré éducation |
| score_transport | Decimal | Score pondéré transport |
| score_commerce | Decimal | Score pondéré commerce |
| score_services_publics | Decimal | Score pondéré services publics |
| score_loisirs | Decimal | Score pondéré loisirs |
| score_services_total | Decimal | Score total des services |
| nb_equipements_total | Integer | Nombre total d'équipements |

## Couche GOLD

### dm_commune_iar

Table principale avec l'IAR par commune.

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| code_commune | VARCHAR(5) | Code commune | PRIMARY KEY |
| nom_commune | VARCHAR(255) | Nom de la commune | |
| dep | VARCHAR(3) | Code département | INDEX |
| reg | VARCHAR(2) | Code région | INDEX |
| prix_m2 | DECIMAL(10,2) | Prix moyen au m² | |
| nb_ventes | INTEGER | Nombre de ventes | |
| prix_m2_min | DECIMAL(10,2) | Prix minimum au m² | |
| prix_m2_max | DECIMAL(10,2) | Prix maximum au m² | |
| score_services_total | DECIMAL(10,2) | Score total services | |
| score_sante | DECIMAL(10,2) | Score santé | |
| score_education | DECIMAL(10,2) | Score éducation | |
| score_transport | DECIMAL(10,2) | Score transport | |
| score_commerce | DECIMAL(10,2) | Score commerce | |
| score_services_publics | DECIMAL(10,2) | Score services publics | |
| score_loisirs | DECIMAL(10,2) | Score loisirs | |
| nb_equipements_total | INTEGER | Nombre total équipements | |
| prix_m2_norm | DECIMAL(10,6) | Prix normalisé [0,1] | |
| score_services_norm | DECIMAL(10,6) | Services normalisés [0,1] | |
| **iar** | DECIMAL(10,6) | **Indice IAR** | INDEX |
| rang_dep | INTEGER | Rang dans le département | |
| rang_reg | INTEGER | Rang dans la région | |
| rang_national | INTEGER | Rang national | |
| date_maj | TIMESTAMP | Date de mise à jour | DEFAULT NOW() |

### dm_dep_stats

Statistiques agrégées par département.

| Colonne | Type | Description |
|---------|------|-------------|
| dep | VARCHAR(3) | Code département (PK) |
| prix_m2_moyen | DECIMAL(10,2) | Prix moyen départemental |
| prix_m2_median | DECIMAL(10,2) | Prix médian départemental |
| score_services_moyen | DECIMAL(10,2) | Score services moyen |
| iar_moyen | DECIMAL(10,6) | IAR moyen du département |
| nb_communes | INTEGER | Nombre de communes |
| nb_ventes_total | INTEGER | Total des ventes |
| nb_equipements_total | INTEGER | Total des équipements |
| top_commune_code | VARCHAR(5) | Code de la meilleure commune |
| top_commune_name | VARCHAR(255) | Nom de la meilleure commune |
| top_commune_iar | DECIMAL(10,6) | IAR de la meilleure commune |
| date_maj | TIMESTAMP | Date de mise à jour |

### dm_time_kpis

Indicateurs temporels (optionnel).

| Colonne | Type | Description |
|---------|------|-------------|
| mois | DATE | Mois de référence |
| dep | VARCHAR(3) | Code département |
| nb_ventes | INTEGER | Nombre de ventes du mois |
| prix_m2_moyen | DECIMAL(10,2) | Prix moyen du mois |
| valeur_fonciere_totale | DECIMAL(15,2) | Valeur totale des transactions |
| tendance | VARCHAR(20) | Tendance (hausse/baisse/stable) |
| variation_pct | DECIMAL(10,2) | Variation en % |
| date_maj | TIMESTAMP | Date de mise à jour |

## Règles de Validation

### DVF
1. `valeur_fonciere > 0`
2. `surface_reelle_bati > 0`
3. `date_mutation IS NOT NULL`
4. `code_commune IS NOT NULL` et normalisé sur 5 caractères
5. `prix_m2` dans l'intervalle [p1, p99] (suppression outliers)
6. `type_local` dans la liste des types valides
7. `nombre_pieces_principales > 0`

### BPE
1. `DEPCOM IS NOT NULL`
2. `TYPEQU IS NOT NULL`
3. `code_commune` normalisé sur 5 caractères

## Pondérations Services

| Catégorie | Poids | Justification |
|-----------|-------|---------------|
| Santé | 3.0 | Essentiel pour qualité de vie |
| Éducation | 2.5 | Très important pour familles |
| Services Publics | 2.0 | Important pour quotidien |
| Transport | 2.0 | Important pour mobilité |
| Commerce | 1.5 | Modérément important |
| Loisirs | 1.0 | Agréable mais non essentiel |

## Formules de Calcul

### Prix au m²
```
prix_m2 = valeur_fonciere / surface_reelle_bati
```

### Score Services
```
score_services_total = Σ (nb_equipements_categorie × poids_categorie)
```

### Normalisation Min-Max
```
valeur_norm = (valeur - min) / (max - min)
```

### IAR (Indice d'Attractivité Rationnelle)
```
IAR = 0.7 × services_norm + 0.3 × (1 - prix_norm)
```

Où:
- `services_norm`: Score services normalisé [0,1]
- `prix_norm`: Prix m² normalisé [0,1]
- Poids: 70% services, 30% prix (inversé)
