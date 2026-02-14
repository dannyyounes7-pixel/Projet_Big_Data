"""
Communes API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
import math

from api.auth import get_current_user
from api.db import get_db
from api.schemas import CommuneIAR, PaginatedResponse, PaginationMeta


router = APIRouter(prefix="/communes", tags=["Communes"])


@router.get("", response_model=PaginatedResponse)
def get_communes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    sort: str = Query("iar_desc", description="Sort field (iar_desc, iar_asc, prix_asc, prix_desc)"),
    dep: Optional[str] = Query(None, description="Filter by department"),
    reg: Optional[str] = Query(None, description="Filter by region"),
    iar_min: Optional[float] = Query(None, description="Minimum IAR"),
    iar_max: Optional[float] = Query(None, description="Maximum IAR"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get paginated list of communes with optional filters
    
    Requires JWT authentication
    """
    db = get_db()
    
    # Build query
    query = "SELECT * FROM dm_commune_iar WHERE 1=1"
    params = []
    
    # Apply filters
    if dep:
        query += " AND dep = %s"
        params.append(dep)
    
    if reg:
        query += " AND reg = %s"
        params.append(reg)
    
    if iar_min is not None:
        query += " AND iar >= %s"
        params.append(iar_min)
    
    if iar_max is not None:
        query += " AND iar <= %s"
        params.append(iar_max)
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as filtered"
    count_result = db.execute_one(count_query, tuple(params))
    total_items = count_result['total'] if count_result else 0
    
    # Apply sorting
    sort_mapping = {
        "iar_desc": "iar DESC",
        "iar_asc": "iar ASC",
        "prix_desc": "prix_m2 DESC",
        "prix_asc": "prix_m2 ASC",
        "services_desc": "score_services_total DESC",
        "services_asc": "score_services_total ASC"
    }
    
    order_by = sort_mapping.get(sort, "iar DESC")
    query += f" ORDER BY {order_by}"
    
    # Apply pagination
    offset = (page - 1) * size
    query += f" LIMIT %s OFFSET %s"
    params.extend([size, offset])
    
    # Execute query
    results = db.execute_query(query, tuple(params))
    
    # Calculate pagination metadata
    total_pages = math.ceil(total_items / size)
    
    pagination = PaginationMeta(
        page=page,
        size=size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    return {
        "data": results,
        "pagination": pagination
    }


@router.get("/{code_commune}", response_model=CommuneIAR)
def get_commune(
    code_commune: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details for a specific commune
    
    Requires JWT authentication
    """
    db = get_db()
    
    query = "SELECT * FROM dm_commune_iar WHERE code_commune = %s"
    result = db.execute_one(query, (code_commune,))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Commune {code_commune} not found")
    
    return result
