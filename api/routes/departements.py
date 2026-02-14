"""
Departments API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from api.auth import get_current_user
from api.db import get_db
from api.schemas import DepartmentStats, CommuneIAR


router = APIRouter(prefix="/departements", tags=["Departements"])


@router.get("/{dep}/top", response_model=List[CommuneIAR])
def get_top_communes_in_department(
    dep: str,
    n: int = Query(10, ge=1, le=100, description="Number of top communes"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get top N communes in a department by IAR
    
    Requires JWT authentication
    """
    db = get_db()
    
    query = """
        SELECT * FROM dm_commune_iar 
        WHERE dep = %s 
        ORDER BY iar DESC 
        LIMIT %s
    """
    
    results = db.execute_query(query, (dep, n))
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No communes found for department {dep}")
    
    return results


@router.get("/{dep}/stats", response_model=DepartmentStats)
def get_department_stats(
    dep: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics for a specific department
    
    Requires JWT authentication
    """
    db = get_db()
    
    query = "SELECT * FROM dm_dep_stats WHERE dep = %s"
    result = db.execute_one(query, (dep,))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Department {dep} not found")
    
    return result


@router.get("", response_model=List[DepartmentStats])
def get_all_departments(
    sort_by: str = Query("iar_moyen", description="Sort by field (iar_moyen, prix_m2_moyen, nb_communes)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics for all departments
    
    Requires JWT authentication
    """
    db = get_db()
    
    # Validate sort field
    valid_sorts = ["iar_moyen", "prix_m2_moyen", "score_services_moyen", "nb_communes"]
    if sort_by not in valid_sorts:
        sort_by = "iar_moyen"
    
    # Validate order
    order = "DESC" if order.lower() == "desc" else "ASC"
    
    query = f"SELECT * FROM dm_dep_stats ORDER BY {sort_by} {order}"
    results = db.execute_query(query)
    
    return results
