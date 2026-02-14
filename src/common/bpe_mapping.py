"""
BPE Equipment Type Mapping and Scoring
Maps TYPEQU codes to service categories with weights
"""

# Mapping of TYPEQU codes to service categories
# Based on INSEE BPE 2024 nomenclature

TYPEQU_CATEGORIES = {
    # SANTÉ (Healthcare)
    'D201': 'sante',  # Médecin omnipraticien
    'D202': 'sante',  # Spécialiste en cardiologie
    'D203': 'sante',  # Spécialiste en dermatologie
    'D204': 'sante',  # Spécialiste en gynécologie
    'D205': 'sante',  # Spécialiste en ophtalmologie
    'D206': 'sante',  # Spécialiste en ORL
    'D207': 'sante',  # Spécialiste en pédiatrie
    'D208': 'sante',  # Spécialiste en psychiatrie
    'D209': 'sante',  # Chirurgien dentiste
    'D210': 'sante',  # Sage-femme
    'D211': 'sante',  # Infirmier
    'D212': 'sante',  # Masseur kinésithérapeute
    'D221': 'sante',  # Pharmacie
    'D231': 'sante',  # Urgences
    'D232': 'sante',  # Maternité
    'D233': 'sante',  # Centre de santé
    'D301': 'sante',  # Hôpital de court séjour
    'D302': 'sante',  # Hôpital de moyen et long séjour
    
    # ÉDUCATION (Education)
    'C101': 'education',  # École maternelle
    'C102': 'education',  # École élémentaire
    'C104': 'education',  # Collège
    'C105': 'education',  # Lycée d'enseignement général et/ou technologique
    'C201': 'education',  # Lycée d'enseignement professionnel
    'C301': 'education',  # Établissement d'enseignement supérieur
    'C302': 'education',  # École d'ingénieurs
    'C303': 'education',  # École de commerce, gestion, comptabilité
    'C304': 'education',  # Université
    
    # TRANSPORT (Transportation)
    'E101': 'transport',  # Gare
    'E102': 'transport',  # Gare de voyageurs d'importance nationale
    'E103': 'transport',  # Gare de voyageurs d'importance régionale
    'E104': 'transport',  # Gare de voyageurs d'importance locale
    'E105': 'transport',  # Aéroport
    'E106': 'transport',  # Gare routière
    
    # COMMERCE (Commerce)
    'B101': 'commerce',  # Hypermarché
    'B102': 'commerce',  # Supermarché
    'B103': 'commerce',  # Grande surface de bricolage
    'B201': 'commerce',  # Supérette
    'B202': 'commerce',  # Épicerie
    'B203': 'commerce',  # Boulangerie
    'B204': 'commerce',  # Boucherie charcuterie
    'B205': 'commerce',  # Produits surgelés
    'B206': 'commerce',  # Poissonnerie
    'B301': 'commerce',  # Librairie papeterie journaux
    'B302': 'commerce',  # Magasin de vêtements
    'B303': 'commerce',  # Magasin d'équipement du foyer
    'B304': 'commerce',  # Magasin de chaussures
    'B305': 'commerce',  # Magasin d'électroménager et de matériel audio-vidéo
    'B306': 'commerce',  # Magasin de meubles
    'B307': 'commerce',  # Magasin d'articles de sports et de loisirs
    'B308': 'commerce',  # Magasin de revêtements murs et sols
    'B309': 'commerce',  # Droguerie quincaillerie bricolage
    
    # SERVICES PUBLICS (Public Services)
    'A101': 'services_publics',  # Pôle emploi
    'A104': 'services_publics',  # Mairie
    'A201': 'services_publics',  # Commissariat de police
    'A202': 'services_publics',  # Gendarmerie
    'A203': 'services_publics',  # Pompiers
    'A206': 'services_publics',  # Trésorerie
    'A207': 'services_publics',  # Tribunal de grande instance
    'A208': 'services_publics',  # Tribunal d'instance
    'A301': 'services_publics',  # Poste
    'A401': 'services_publics',  # Banque, Caisse d'Épargne
    'A501': 'services_publics',  # Crèche, garderie
    
    # LOISIRS (Leisure)
    'F101': 'loisirs',  # Cinéma
    'F102': 'loisirs',  # Théâtre
    'F103': 'loisirs',  # Musée
    'F104': 'loisirs',  # Bibliothèque médiathèque
    'F105': 'loisirs',  # Conservatoire
    'F201': 'loisirs',  # Bassin de natation
    'F301': 'loisirs',  # Terrain de grands jeux
    'F302': 'loisirs',  # Salle ou terrain spécialisé
    'F303': 'loisirs',  # Plateau EPS
    'F304': 'loisirs',  # Salle de sports
    'F305': 'loisirs',  # Terrain de golf
    'F306': 'loisirs',  # Centre équestre
    'F307': 'loisirs',  # Athlétisme
    'F308': 'loisirs',  # Tennis
}


# Category weights for service score calculation
# Higher weight = more important for quality of life
CATEGORY_WEIGHTS = {
    'sante': 3.0,           # Healthcare is critical
    'education': 2.5,       # Education is very important
    'transport': 2.0,       # Transportation is important
    'commerce': 1.5,        # Commerce is moderately important
    'services_publics': 2.0,  # Public services are important
    'loisirs': 1.0,         # Leisure is nice to have
}


def get_category(typequ: str) -> str:
    """
    Get service category for a given TYPEQU code
    
    Args:
        typequ: TYPEQU code from BPE
        
    Returns:
        Category name or 'autre' if not found
    """
    return TYPEQU_CATEGORIES.get(typequ, 'autre')


def get_category_weight(category: str) -> float:
    """
    Get weight for a service category
    
    Args:
        category: Service category name
        
    Returns:
        Weight value (default: 1.0 for unknown categories)
    """
    return CATEGORY_WEIGHTS.get(category, 1.0)


def get_all_categories() -> list:
    """
    Get list of all service categories
    
    Returns:
        List of category names
    """
    return list(CATEGORY_WEIGHTS.keys())


def get_typequ_mapping_dict() -> dict:
    """
    Get complete TYPEQU to category mapping
    
    Returns:
        Dictionary mapping TYPEQU codes to categories
    """
    return TYPEQU_CATEGORIES.copy()


def get_weights_dict() -> dict:
    """
    Get complete category weights mapping
    
    Returns:
        Dictionary mapping categories to weights
    """
    return CATEGORY_WEIGHTS.copy()
