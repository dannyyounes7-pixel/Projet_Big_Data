"""
Pydantic Schemas for API Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from decimal import Decimal


# Authentication schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Commune schemas
class CommuneIAR(BaseModel):
    code_commune: str
    nom_commune: Optional[str]
    dep: Optional[str]
    reg: Optional[str]
    prix_m2: Optional[float]
    nb_ventes: Optional[int]
    prix_m2_min: Optional[float]
    prix_m2_max: Optional[float]
    score_services_total: Optional[float]
    score_sante: Optional[float] = None
    score_education: Optional[float] = None
    score_transport: Optional[float] = None
    score_commerce: Optional[float] = None
    score_services_publics: Optional[float] = None
    score_loisirs: Optional[float] = None
    nb_equipements_total: Optional[int] = None
    prix_m2_norm: Optional[float]
    score_services_norm: Optional[float]
    iar: Optional[float]
    rang_dep: Optional[int]
    rang_reg: Optional[int]
    rang_national: Optional[int]
    
    class Config:
        from_attributes = True


# Department statistics schema
class DepartmentStats(BaseModel):
    dep: str
    prix_m2_moyen: Optional[float]
    prix_m2_median: Optional[float]
    score_services_moyen: Optional[float]
    iar_moyen: Optional[float]
    nb_communes: Optional[int]
    nb_ventes_total: Optional[int]
    nb_equipements_total: Optional[int]
    top_commune_code: Optional[str]
    top_commune_name: Optional[str]
    top_commune_iar: Optional[float]
    
    class Config:
        from_attributes = True


# Pagination schema
class PaginationMeta(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    data: List[Any]
    pagination: PaginationMeta


# Summary statistics schema
class SummaryStats(BaseModel):
    total_communes: int
    total_ventes: int
    total_equipements: int
    prix_m2_moyen_national: float
    score_services_moyen_national: float
    iar_moyen_national: float
    iar_min: float
    iar_max: float
