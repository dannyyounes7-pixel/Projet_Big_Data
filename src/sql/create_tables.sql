-- DDL for IAR Platform Datamarts (PostgreSQL)

-- Drop existing tables
DROP TABLE IF EXISTS dm_commune_iar CASCADE;
DROP TABLE IF EXISTS dm_dep_stats CASCADE;
DROP TABLE IF EXISTS dm_time_kpis CASCADE;

-- Main commune IAR table
CREATE TABLE dm_commune_iar (
    code_commune VARCHAR(5) PRIMARY KEY,
    nom_commune VARCHAR(255),
    dep VARCHAR(3),
    reg VARCHAR(2),
    
    -- Prix immobilier
    prix_m2 DECIMAL(10, 2),
    nb_ventes INTEGER,
    prix_m2_min DECIMAL(10, 2),
    prix_m2_max DECIMAL(10, 2),
    
    -- Services par catégorie
    score_services_total DECIMAL(10, 2),
    score_sante DECIMAL(10, 2),
    score_education DECIMAL(10, 2),
    score_transport DECIMAL(10, 2),
    score_commerce DECIMAL(10, 2),
    score_services_publics DECIMAL(10, 2),
    score_loisirs DECIMAL(10, 2),
    nb_equipements_total INTEGER,
    
    -- Valeurs normalisées
    prix_m2_norm DECIMAL(10, 6),
    score_services_norm DECIMAL(10, 6),
    
    -- IAR et rankings
    iar DECIMAL(10, 6),
    rang_dep INTEGER,
    rang_reg INTEGER,
    rang_national INTEGER,
    
    -- Metadata
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departmental statistics table
CREATE TABLE dm_dep_stats (
    dep VARCHAR(3) PRIMARY KEY,
    
    -- Aggregated statistics
    prix_m2_moyen DECIMAL(10, 2),
    prix_m2_median DECIMAL(10, 2),
    score_services_moyen DECIMAL(10, 2),
    iar_moyen DECIMAL(10, 6),
    
    -- Counts
    nb_communes INTEGER,
    nb_ventes_total INTEGER,
    nb_equipements_total INTEGER,
    
    -- Top commune
    top_commune_code VARCHAR(5),
    top_commune_name VARCHAR(255),
    top_commune_iar DECIMAL(10, 6),
    
    -- Metadata
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time series KPIs table (optional - for temporal analysis)
CREATE TABLE dm_time_kpis (
    mois DATE,
    dep VARCHAR(3),
    
    -- Monthly metrics
    nb_ventes INTEGER,
    prix_m2_moyen DECIMAL(10, 2),
    valeur_fonciere_totale DECIMAL(15, 2),
    
    -- Trend indicators
    tendance VARCHAR(20),  -- 'hausse', 'baisse', 'stable'
    variation_pct DECIMAL(10, 2),
    
    -- Metadata
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (mois, dep)
);

-- Indexes for performance
CREATE INDEX idx_commune_iar_dep ON dm_commune_iar(dep);
CREATE INDEX idx_commune_iar_reg ON dm_commune_iar(reg);
CREATE INDEX idx_commune_iar_score ON dm_commune_iar(iar DESC);
CREATE INDEX idx_commune_iar_prix ON dm_commune_iar(prix_m2);
CREATE INDEX idx_dep_stats_iar ON dm_dep_stats(iar_moyen DESC);

-- Comments
COMMENT ON TABLE dm_commune_iar IS 'Datamart principal avec IAR par commune';
COMMENT ON TABLE dm_dep_stats IS 'Statistiques agrégées par département';
COMMENT ON TABLE dm_time_kpis IS 'Indicateurs temporels mensuels';

COMMENT ON COLUMN dm_commune_iar.iar IS 'Indice Attractivité Rationnelle = 0.7*services_norm + 0.3*(1-prix_norm)';
COMMENT ON COLUMN dm_commune_iar.rang_dep IS 'Rang IAR dans le département';
COMMENT ON COLUMN dm_commune_iar.rang_reg IS 'Rang IAR dans la région';
COMMENT ON COLUMN dm_commune_iar.rang_national IS 'Rang IAR national';
