from api.db import get_db

def check_final():
    db = get_db()
    print("--- FINAL IAR DISTRIBUTION (Rank-Based) ---")
    stats = db.execute_one("""
         SELECT 
            MIN(iar) as min, MAX(iar) as max, AVG(iar) as avg,
            PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY iar) as median,
            COUNT(*) as nb_communes
         FROM dm_commune_iar
    """)
    print(f"IAR Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
    print(f"Average:   {stats['avg']:.4f}")
    print(f"Median:    {stats['median']:.4f}")
    print(f"Total Communes: {stats['nb_communes']}")

    print("\n--- SAMPLE TOP 5 ---")
    tops = db.execute_query("SELECT nom_commune, iar, prix_m2_moyen, score_services_total FROM dm_commune_iar ORDER BY iar DESC LIMIT 5")
    for t in tops:
        print(t)

if __name__ == "__main__":
    check_final()
