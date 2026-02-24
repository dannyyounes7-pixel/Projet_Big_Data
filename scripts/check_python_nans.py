import psycopg2
import math

def check():
    try:
        conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/iar_db')
        cur = conn.cursor()
        
        print("Fetching IAR, Prix_m2_moyen, Score...")
        cur.execute("SELECT code_commune, iar, prix_m2_moyen, score_services_total FROM dm_commune_iar")
        
        cols = [desc[0] for desc in cur.description]
        print(f"Columns: {cols}")
        
        rows = cur.fetchall()
        print(f"Fetched {len(rows)} rows.")
        
        inf_count = 0
        nan_count = 0
        
        for i, row in enumerate(rows):
            code, iar, prix, score = row
            
            # Check IAR
            if iar is not None and (math.isnan(iar) or math.isinf(iar)):
                print(f"Row {i} ({code}): IAR is {iar}")
                if math.isinf(iar): inf_count += 1
                if math.isnan(iar): nan_count += 1
                
            # Check Prix
            if prix is not None and (math.isnan(prix) or math.isinf(prix)):
                print(f"Row {i} ({code}): Prix is {prix}")
                if math.isinf(prix): inf_count += 1
                if math.isnan(prix): nan_count += 1

            # Check Score
            if score is not None and (math.isnan(score) or math.isinf(score)):
                print(f"Row {i} ({code}): Score is {score}")
                if math.isinf(score): inf_count += 1
                if math.isnan(score): nan_count += 1
                
        print(f"Total Inf: {inf_count}")
        print(f"Total NaN: {nan_count}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
