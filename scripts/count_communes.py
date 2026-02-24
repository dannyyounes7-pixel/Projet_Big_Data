from api.db import get_db

db = get_db()
result = db.execute_one('SELECT COUNT(*) as total FROM dm_commune_iar')
print(f'Total communes in DB: {result["total"]}')
