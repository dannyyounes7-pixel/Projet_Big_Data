"""
Statistics API Routes
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from api.auth import get_current_user
from api.db import get_db
from api.schemas import SummaryStats


router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/summary", response_model=SummaryStats)
def get_summary_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get global summary statistics
    
    Requires JWT authentication
    """
    try:
        db = get_db()
        
        query = """
            SELECT 
                COUNT(*) as total_communes,
                SUM(nb_ventes) as total_ventes,
                SUM(nb_equipements_total) as total_equipements,
                AVG(prix_m2_moyen) as prix_m2_moyen_national,
                AVG(score_services_total) as score_services_moyen_national,
                AVG(iar) as iar_moyen_national,
                MIN(iar) as iar_min,
                MAX(iar) as iar_max
            FROM dm_commune_iar
        """
        
        result = db.execute_one(query)
        
        return result
    except Exception as e:
        import traceback
        with open("last_error_stats.txt", "w") as f:
            f.write(f"Error in /summary: {str(e)}\n")
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions")
def get_regional_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics aggregated by region
    
    Requires JWT authentication
    """
    try:
        db = get_db()
        
        query = """
            SELECT 
                reg,
                COUNT(*) as nb_communes,
                AVG(prix_m2_moyen) as prix_m2_moyen,
                AVG(score_services_total) as score_services_moyen,
                AVG(iar) as iar_moyen,
                MIN(iar) as iar_min,
                MAX(iar) as iar_max
            FROM dm_commune_iar
            WHERE reg IS NOT NULL
            GROUP BY reg
            ORDER BY iar_moyen DESC
        """
        
        results = db.execute_query(query)
        
        return {"regions": results}
    except Exception as e:
        import traceback
        with open("last_error_stats.txt", "a") as f:
             f.write(f"Error in /regions: {str(e)}\n")
             f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation")
def get_price_services_correlation(
    current_user: dict = Depends(get_current_user)
):
    """
    Get correlation data between price and services
    
    Requires JWT authentication
    """
    try:
        db = get_db()
        
        query = """
            SELECT 
                CASE 
                    WHEN prix_m2_moyen < 2000 THEN 'Bas'
                    WHEN prix_m2_moyen < 4000 THEN 'Moyen'
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
            ORDER BY prix_categorie, services_categorie
        """
        
        results = db.execute_query(query)
        
        return {"correlation": results}
    except Exception as e:
        import traceback
        with open("last_error_stats.txt", "a") as f:
             f.write(f"Error in /correlation: {str(e)}\n")
             f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
