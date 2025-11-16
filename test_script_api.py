"""
Quick test script to verify the script debugger API endpoints.
Run this after starting the backend server.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_create_script():
    """Test creating a script."""
    print("Testing script creation...")
    
    script_data = {
        "script_name": "test_filter",
        "description": "Filter data by amount",
        "script_content": "result = data[data['amount'] > 100]"
    }
    
    response = requests.post(f"{BASE_URL}/scripts/create", json=script_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201

def test_list_scripts():
    """Test listing all scripts."""
    print("\nTesting script listing...")
    
    response = requests.get(f"{BASE_URL}/scripts")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_script():
    """Test getting a specific script."""
    print("\nTesting get script...")
    
    response = requests.get(f"{BASE_URL}/scripts/test_filter")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("Script Debugger API Test")
    print("=" * 60)
    print("\nMake sure the backend server is running on http://localhost:8000")
    print()
    
    try:
        # Test endpoints
        test_create_script()
        test_list_scripts()
        test_get_script()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server")
        print("Please start the backend with: ./start_backend.sh")
    except Exception as e:
        print(f"\n❌ Error: {e}")
