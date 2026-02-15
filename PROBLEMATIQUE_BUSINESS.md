# Problématique Business - IAR Platform

## Résumé Exécutif

Ce projet implémente une plateforme Big Data complète pour analyser les communes françaises selon leur **Indice d'Attractivité Rationnelle (IAR)**, qui mesure le rapport entre la qualité des services de proximité et les prix immobiliers.

**Résultat clé** : Identification des communes offrant le meilleur équilibre services/prix pour aider à la décision d'installation.

---

## Problématique Business

### Le Défi

Les particuliers, familles et jeunes actifs souhaitant s'installer dans une nouvelle commune font face à un dilemme complexe :
- Les grandes villes offrent de nombreux services mais des prix immobiliers prohibitifs
- Les petites communes rurales sont accessibles financièrement mais manquent souvent de services essentiels
- Il est difficile de comparer objectivement des milliers de communes selon ces deux dimensions

### Besoins Identifiés

1. **Pour les particuliers** : Trouver la commune idéale combinant qualité de vie et accessibilité financière
2. **Pour les collectivités** : Évaluer leur attractivité et identifier les axes d'amélioration
3. **Pour les investisseurs** : Repérer les zones sous-valorisées avec un potentiel de croissance

---

## Objectifs du Projet

### Objectif Principal

Construire une plateforme Big Data de bout en bout pour identifier les communes françaises les plus attractives en croisant :
- **Prix immobiliers** (données DVF 2024)
- **Services de proximité** (données BPE 2024)

### Objectifs Techniques

- Architecture médaillon (RAW → SILVER → GOLD)
- Traitement distribué avec Apache Spark
- Validation des données (7+ règles métier)
- Jointures et agrégations complexes
- Window functions pour rankings
- API REST sécurisée (JWT)
- Visualisation interactive

---

## La Solution : Indice d'Attractivité Rationnelle (IAR)

### Définition

L'IAR est un indicateur composite qui combine deux dimensions :

1. **Densité des services** (70% du poids)
   - Services de santé
   - Établissements d'éducation
   - Services publics
   - Transports
   - Commerces
   - Loisirs

2. **Prix immobiliers** (30% du poids)
   - Prix médian au m² par commune
   - Calculé à partir des transactions immobilières réelles

### Formule de Calcul

```
IAR = 0.7 × services_normalisés + 0.3 × (1 - prix_normalisés)
```

### Interprétation

- **IAR proche de 1** : Commune très attractive (nombreux services, prix raisonnables)
- **IAR proche de 0** : Commune moins attractive (peu de services ou prix élevés)

### Méthodologie

#### Pondération des Services

| Catégorie | Poids | Justification |
|-----------|-------|---------------|
| Santé | 3.0 | Essentiel pour qualité de vie |
| Éducation | 2.5 | Très important pour familles |
| Services Publics | 2.0 | Important pour quotidien |
| Transport | 2.0 | Important pour mobilité |
| Commerce | 1.5 | Modérément important |
| Loisirs | 1.0 | Agréable mais non essentiel |

#### Normalisation

Les données sont normalisées entre 0 et 1 pour permettre la comparaison :
- `prix_norm = (prix_m2 - min) / (max - min)`
- `services_norm = (score_services - min) / (max - min)`

Le prix est inversé dans la formule (1 - prix_norm) car un prix élevé est une pénalité.

---

## Valeur Ajoutée

### Pour les Particuliers et Familles

**Avantages** :
- Comparaison objective de milliers de communes
- Identification rapide des "sweet spots" (bon rapport services/prix)
- Prise de décision éclairée pour un déménagement
- Découverte de communes méconnues mais attractives

**Cas d'usage** :
- Jeune couple cherchant à acheter sa première maison
- Famille souhaitant s'installer en périphérie d'une grande ville
- Retraités cherchant une commune paisible mais bien équipée

### Pour les Collectivités Locales

**Avantages** :
- Évaluation objective de l'attractivité territoriale
- Identification des manques en services
- Benchmarking avec des communes similaires
- Aide à la planification des équipements

**Cas d'usage** :
- Maire souhaitant améliorer l'attractivité de sa commune
- Service d'urbanisme planifiant de nouveaux équipements
- Intercommunalité harmonisant les services sur le territoire

### Pour les Investisseurs Immobiliers

**Avantages** :
- Repérage des zones sous-valorisées
- Anticipation des tendances du marché
- Optimisation des investissements immobiliers
- Identification des communes à fort potentiel

**Cas d'usage** :
- Promoteur immobilier cherchant de nouveaux terrains
- Investisseur locatif optimisant son portefeuille
- Fonds d'investissement analysant le marché français

---

## Architecture et Technologies

### Sources de Données

**DVF (Demandes de Valeurs Foncières) 2024**
- Volume : ~200,000+ transactions immobilières
- Utilisation : Calcul du prix au m² par commune

**BPE (Base Permanente des Équipements) 2024**
- Volume : ~1,200,000+ équipements
- Utilisation : Score de services par commune

**Référentiel Communes 2024**
- Volume : 35,000+ communes
- Utilisation : Enrichissement géographique

### Architecture Médaillon

```
SOURCE (DVF + BPE + Communes)
   ↓
RAW Layer (données brutes en Parquet)
   ↓
SILVER Layer (nettoyées, validées, enrichies)
   ↓
GOLD Layer (datamarts PostgreSQL)
   ↓
API REST (JWT + pagination)
   ↓
Visualisation (Dashboard Streamlit)
```

### Technologies Utilisées

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Big Data | Apache Spark 3.5 | Traitement distribué de gros volumes |
| Base de données | PostgreSQL 13+ | Stockage relationnel performant |
| API | FastAPI | Framework Python moderne et rapide |
| Authentification | JWT | Sécurisation des endpoints |
| Visualisation | Streamlit + Plotly | Dashboard interactif |
| Stockage | Parquet (Snappy) | Format optimisé pour l'analytique |

---

## Résultats et Insights

### Statistiques Globales

- **Communes analysées** : ~35,000
- **Transactions DVF** : ~200,000+
- **Équipements BPE** : ~1,200,000+
- **IAR moyen national** : ~0.55
- **Plage IAR** : [0.10, 0.95]

### Insights Clés

**Corrélation Prix-Services** :
- Les grandes villes ont de nombreux services mais des prix élevés
- Les petites communes rurales ont peu de services et des prix bas
- **Sweet spot** : Communes périurbaines avec un IAR élevé, offrant un bon équilibre

**Tendances observées** :
- Les communes de taille moyenne bien équipées sont souvent sous-valorisées
- La proximité des transports augmente significativement l'IAR
- Les zones périurbaines à 20-30 km des grandes villes offrent souvent le meilleur rapport

---

## Exemples d'Utilisation

### Exemple 1 : Recherche de Commune pour Installation

**Profil** : Jeune couple avec enfants, budget 300,000 €

**Recherche** :
1. Filtrer les communes avec IAR > 0.70
2. Filtrer les prix < 3,000 €/m²
3. Prioriser les communes avec bonne notation "Éducation"

**Résultat** : Liste de communes périurbaines bien équipées et accessibles

### Exemple 2 : Analyse Départementale

**Profil** : Collectivité départementale

**Recherche** :
1. Comparer l'IAR moyen de toutes les communes du département
2. Identifier les communes avec le plus faible score de services
3. Benchmarker avec les départements voisins

**Résultat** : Plan d'action pour améliorer l'attractivité territoriale

### Exemple 3 : Investissement Immobilier

**Profil** : Investisseur locatif

**Recherche** :
1. Identifier les communes avec IAR élevé mais prix encore bas
2. Vérifier la tendance d'évolution des prix
3. Analyser les projets d'équipements futurs

**Résultat** : Zones d'investissement à fort potentiel de valorisation

---

## Perspectives d'Évolution

### Court Terme
- Intégration de données supplémentaires (qualité de l'air, criminalité)
- Personnalisation des pondérations par profil utilisateur
- Historique des évolutions d'IAR

### Moyen Terme
- Prédictions de l'évolution de l'IAR avec machine learning
- Application mobile pour consultation en mobilité
- Alertes automatiques sur les opportunités

### Long Terme
- Expansion internationale (autres pays européens)
- Intégration de données temps réel
- Marketplace pour services immobiliers

---

## Conclusion

La plateforme IAR répond à un besoin réel du marché en fournissant une analyse objective et data-driven de l'attractivité des communes françaises. Elle combine :

- **Rigueur technique** : Architecture Big Data professionnelle
- **Pertinence business** : Indicateur actionnable pour différents acteurs
- **Facilité d'accès** : API et dashboard pour une utilisation simple

**La valeur créée** s'adresse à trois marchés distincts (B2C, B2G, B2B) avec un fort potentiel de monétisation et d'impact social positif en facilitant les meilleures décisions d'installation résidentielle.
