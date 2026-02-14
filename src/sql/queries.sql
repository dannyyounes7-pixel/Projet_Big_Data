-- Sample queries for data validation and analysis

-- Top 10 communes by IAR
SELECT 
    code_commune,
    nom_commune,
    dep,
    iar,
    prix_m2,
    score_services_total,
    rang_national
FROM dm_commune_iar
ORDER BY iar DESC
LIMIT 10;

-- Top 10 communes by department
SELECT 
    code_commune,
    nom_commune,
    dep,
    iar,
    rang_dep
FROM dm_commune_iar
WHERE dep = '75'  -- Paris
ORDER BY iar DESC
LIMIT 10;

-- Departmental statistics
SELECT 
    dep,
    nb_communes,
    prix_m2_moyen,
    score_services_moyen,
    iar_moyen,
    top_commune_name,
    top_commune_iar
FROM dm_dep_stats
ORDER BY iar_moyen DESC
LIMIT 20;

-- Communes with high services but low prices (best IAR)
SELECT 
    code_commune,
    nom_commune,
    dep,
    iar,
    prix_m2,
    score_services_total,
    nb_equipements_total
FROM dm_commune_iar
WHERE iar > 0.7
ORDER BY iar DESC;

-- Price vs Services correlation
SELECT 
    CASE 
        WHEN prix_m2 < 2000 THEN 'Bas'
        WHEN prix_m2 < 4000 THEN 'Moyen'
        ELSE 'Élevé'
    END as prix_categorie,
    CASE 
        WHEN score_services_total < 50 THEN 'Faible'
        WHEN score_services_total < 100 THEN 'Moyen'
        ELSE 'Élevé'
    END as services_categorie,
    COUNT(*) as nb_communes,
    AVG(iar) as iar_moyen
FROM dm_commune_iar
GROUP BY prix_categorie, services_categorie
ORDER BY prix_categorie, services_categorie;

-- Data quality checks
SELECT 
    COUNT(*) as total_communes,
    COUNT(CASE WHEN iar IS NULL THEN 1 END) as iar_null,
    COUNT(CASE WHEN prix_m2 IS NULL THEN 1 END) as prix_null,
    COUNT(CASE WHEN score_services_total IS NULL THEN 1 END) as services_null,
    MIN(iar) as iar_min,
    MAX(iar) as iar_max,
    AVG(iar) as iar_moyen
FROM dm_commune_iar;

-- Regional comparison
SELECT 
    reg,
    COUNT(DISTINCT code_commune) as nb_communes,
    AVG(prix_m2) as prix_m2_moyen,
    AVG(score_services_total) as services_moyen,
    AVG(iar) as iar_moyen
FROM dm_commune_iar
WHERE reg IS NOT NULL
GROUP BY reg
ORDER BY iar_moyen DESC;
