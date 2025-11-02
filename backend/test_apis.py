#!/usr/bin/env python
"""
Simple API testing script for Pasky authentication endpoints.
Note: Full WebAuthn testing requires a browser, but this script tests
the basic endpoint responses.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
session = requests.Session()

def print_response(title, response):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_register_start():
    """Test registration start endpoint."""
    print("\n🔵 Testing: POST /api/auth/register/start/")
    
    # Test successful registration start
    data = {
        "username": f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
    }
    
    response = session.post(f"{BASE_URL}/auth/register/start/", json=data)
    print_response("✅ Registration Start (Success)", response)
    
    if response.status_code == 200:
        return response.json()
    return None

def test_register_start_errors():
    """Test registration start error cases."""
    print("\n🔵 Testing: POST /api/auth/register/start/ - Error Cases")
    
    # Test missing fields
    response = session.post(f"{BASE_URL}/auth/register/start/", json={"username": "test"})
    print_response("❌ Registration Start (Missing Email)", response)
    
    # Test duplicate username (if test user exists)
    response = session.post(f"{BASE_URL}/auth/register/start/", json={
        "username": "testuser",
        "email": "test2@example.com"
    })
    if response.status_code != 200:
        print_response("❌ Registration Start (Duplicate Username)", response)

def test_login_start():
    """Test login start endpoint."""
    print("\n🔵 Testing: POST /api/auth/login/start/")
    
    # Test with existing user (if any)
    data = {"username": "testuser"}
    response = session.post(f"{BASE_URL}/auth/login/start/", json=data)
    print_response("✅ Login Start", response)
    
    if response.status_code == 200:
        return response.json()
    return None

def test_login_start_errors():
    """Test login start error cases."""
    print("\n🔵 Testing: POST /api/auth/login/start/ - Error Cases")
    
    # Test missing username
    response = session.post(f"{BASE_URL}/auth/login/start/", json={})
    print_response("❌ Login Start (Missing Username)", response)
    
    # Test non-existent user
    response = session.post(f"{BASE_URL}/auth/login/start/", json={
        "username": "nonexistent_user_12345"
    })
    print_response("❌ Login Start (User Not Found)", response)

def test_user_info():
    """Test get user info endpoint (requires authentication)."""
    print("\n🔵 Testing: GET /api/auth/user/")
    
    response = session.get(f"{BASE_URL}/auth/user/")
    print_response("🔒 User Info (Requires Auth)", response)
    
    if response.status_code == 200:
        return response.json()
    return None

def test_logout():
    """Test logout endpoint."""
    print("\n🔵 Testing: POST /api/auth/logout/")
    
    response = session.post(f"{BASE_URL}/auth/logout/")
    print_response("🚪 Logout", response)

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚀 Pasky API Testing Script")
    print("="*60)
    print("\n⚠️  Note: Full WebAuthn flow requires browser interaction.")
    print("    This script tests basic endpoint responses only.\n")
    
    try:
        # Test registration flow
        reg_options = test_register_start()
        test_register_start_errors()
        
        # Test login flow
        login_options = test_login_start()
        test_login_start_errors()
        
        # Test protected endpoints
        user_info = test_user_info()
        
        # Test logout
        test_logout()
        
        print("\n" + "="*60)
        print("✅ Testing Complete!")
        print("="*60)
        print("\n📝 Summary:")
        print("   - Registration and login START endpoints tested")
        print("   - Error cases tested")
        print("   - Protected endpoint tested (may require auth)")
        print("\n⚠️  To test COMPLETE endpoints:")
        print("   1. Use the React frontend at http://localhost:3000")
        print("   2. Or use a browser with WebAuthn support")
        print("   3. Or implement full WebAuthn credential creation in Python")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server.")
        print("   Make sure Django server is running on http://localhost:8000")
        print("   Run: python manage.py runserver\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")

if __name__ == "__main__":
    main()

