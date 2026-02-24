"""
Script de test pour l'API IAR Platform
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test du endpoint health"""
    print("\n" + "="*60)
    print("TEST: Endpoint Health")
    print("="*60)
    
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_login():
    """Test de l'authentification"""
    print("\n" + "="*60)
    print("TEST: Authentification JWT")
    print("="*60)
    
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Token reçu: {result.get('access_token', '')[:50]}...")
        print(f"Type: {result.get('token_type')}")
        return result.get('access_token')
    else:
        print(f"Erreur: {response.text}")
        return None

def test_stats(token):
    """Test du endpoint stats/summary"""
    print("\n" + "="*60)
    print("TEST: Endpoint Stats Summary")
    print("="*60)
    
    if not token:
        print("Pas de token disponible, test ignoré")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/stats/summary", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Communes analysées: {data.get('total_communes', 0):,}")
        print(f"Ventes totales: {data.get('total_ventes', 0):,}")
        print(f"IAR moyen: {data.get('iar_moyen_national', 0):.4f}")
        return True
    else:
        print(f"Erreur: {response.text}")
        return False

def test_communes(token):
    """Test du endpoint communes avec pagination"""
    print("\n" + "="*60)
    print("TEST: Endpoint Communes (pagination)")
    print("="*60)
    
    if not token:
        print("Pas de token disponible, test ignoré")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "size": 5, "sort": "iar_desc"}
    
    response = requests.get(f"{API_URL}/communes", headers=headers, params=params)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Page: {data.get('page')}/{data.get('pages')}")
        print(f"Total: {data.get('total')} communes")
        print(f"\nTop 5 communes par IAR:")
        for commune in data.get('data', [])[:5]:
            print(f"  - {commune.get('nom_commune')} ({commune.get('code_commune')}): IAR = {commune.get('iar', 0):.4f}")
        return True
    else:
        print(f"Erreur: {response.text}")
        return False

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("TEST API IAR PLATFORM")
    print("="*60)
    
    results = {}
    
    # Test 1: Health
    results['health'] = test_health()
    
    # Test 2: Login
    token = test_login()
    results['login'] = token is not None
    
    # Test 3: Stats
    results['stats'] = test_stats(token)
    
    # Test 4: Communes
    results['communes'] = test_communes(token)
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✓ OK" if success else "✗ ÉCHEC"
        print(f"{test_name.upper():15} : {status}")
    
    total_tests = len(results)
    successful_tests = sum(1 for v in results.values() if v)
    
    print(f"\nRésultat: {successful_tests}/{total_tests} tests réussis")
    
    if successful_tests == total_tests:
        print("\n✓ API FONCTIONNELLE ET CONFORME")
    else:
        print("\n⚠ Certains tests ont échoué")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter à l'API")
        print("Assurez-vous que l'API est lancée sur http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
