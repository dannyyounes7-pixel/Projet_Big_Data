import psycopg2

def check_schema():
    try:
        conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/iar_db')
        cur = conn.cursor()
        
        with open("schema.txt", "w") as f:
            f.write("Table: dm_commune_iar\n")
            cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'dm_commune_iar'")
            rows = cur.fetchall()
            for row in rows:
                f.write(f"  {row[0]}: {row[1]}\n")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
