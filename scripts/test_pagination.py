import requests
import time

BASE_URL = "http://localhost:8000"

def test_pagination():
    # 1. Login
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        token = resp.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
    except Exception as e:
        print(f"Login connection failed: {e}")
        return

    # 2. Test Pagination and Sorting
    sort_options = ["iar_desc", "iar_asc", "prix_desc", "prix_asc"]
    
    for sort in sort_options:
        print(f"\nTesting sort: {sort}")
        for page in range(1, 4):
            print(f"  Testing Page {page}...")
            try:
                resp = requests.get(f"{BASE_URL}/communes?page={page}&size=20&sort={sort}", headers=headers)
                print(f"    Status: {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"    Success. Items: {len(data['data'])}")
                else:
                    print(f"    Failed: {resp.text}")
            except Exception as e:
                print(f"    Connection error: {e}")
                return # Stop if we crash it

if __name__ == "__main__":
    test_pagination()
