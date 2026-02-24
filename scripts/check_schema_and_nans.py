import psycopg2
import sys

def check():
    try:
        conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/iar_db')
        cur = conn.cursor()
        
        # 1. Check Schema
        print("Schema for dm_commune_iar:")
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'dm_commune_iar'")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
            
        # 2. Check for NaNs
        print("\nChecking for NaN/Inf...")
        cols = ['iar', 'score_services_total', 'prix_m2']
        for col in cols:
            query = f"SELECT count(*) FROM dm_commune_iar WHERE {col} = 'NaN'"
            try:
                cur.execute(query)
                count = cur.fetchone()[0]
                if count > 0:
                    print(f"  WARNING: {col} has {count} NaNs")
            except Exception as e:
                print(f"  Error checking {col} for NaN: {e}")
                conn.rollback()

            query = f"SELECT count(*) FROM dm_commune_iar WHERE {col} = 'Infinity' OR {col} = '-Infinity'"
            try:
                cur.execute(query)
                count = cur.fetchone()[0]
                if count > 0:
                    print(f"  WARNING: {col} has {count} Infinity")
            except Exception as e:
                print(f"  Error checking {col} for Inf: {e}")
                conn.rollback()
        
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check()
