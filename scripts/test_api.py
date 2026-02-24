import requests

BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Login
    print("Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} {resp.text}")
        return
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Test Department Stats (01)
    dep = "01"
    print(f"Testing /departements/{dep}/stats...")
    resp = requests.get(f"{BASE_URL}/departements/{dep}/stats", headers=headers)
    if resp.status_code == 200:
        print(f"Success! Stats for {dep}:")
        print(resp.json())
    else:
        print(f"Failed to get stats for {dep}: {resp.status_code} {resp.text}")

    # 3. Test Department Stats (75)
    dep = "75"
    print(f"Testing /departements/{dep}/stats...")
    resp = requests.get(f"{BASE_URL}/departements/{dep}/stats", headers=headers)
    if resp.status_code == 200:
        print(f"Success! Stats for {dep}:")
        print(resp.json())
    elif resp.status_code == 404:
        print(f"Department {dep} not found (expected if data missing).")
    else:
        print(f"Failed to get stats for {dep}: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_api()
