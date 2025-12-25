import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_home():
    print("Testing Home...")
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 200
    print("Home OK")

def test_rate_limit():
    print("Testing Rate Limit...")
    # Threshold is 5. We make 6 requests.
    for i in range(6):
        resp = requests.get(f"{BASE_URL}/spam/")
        print(f"Req {i+1}: {resp.status_code}")
        if resp.status_code == 429:
            print("Rate Limit Triggered OK")
            return
    raise Exception("Rate Limit NOT triggered")

def test_protected():
    print("Testing Protected...")
    # Should redirect to login because we are not authenticated
    # But wait, our middleware checks MFA *after* authentication.
    # If not authenticated, standard Django login_required handles it.
    resp = requests.get(f"{BASE_URL}/protected/", allow_redirects=False)
    print(f"Protected Status: {resp.status_code}")
    assert resp.status_code == 302 # Redirect to login
    print("Protected Redirect OK")

if __name__ == "__main__":
    try:
        test_home()
        test_protected()
        test_rate_limit()
        print("ALL DEMO TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        exit(1)
