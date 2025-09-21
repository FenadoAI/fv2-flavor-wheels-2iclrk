#!/usr/bin/env python3
"""
Test script for Food Truck API endpoints
"""
import requests
import json

# API base URL - using port 8001 as mentioned in the instructions
BASE_URL = "http://localhost:8001/api"

def test_api_endpoint(method, endpoint, data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error testing {method} {endpoint}: {e}")
        return None

def main():
    print("Testing Food Truck API Endpoints")
    print("=" * 50)

    # Test basic endpoint
    test_api_endpoint("GET", "/")

    # Test food truck info
    test_api_endpoint("GET", "/foodtruck")

    # Test menu
    menu = test_api_endpoint("GET", "/menu")

    # Test locations
    locations = test_api_endpoint("GET", "/locations")

    # Test creating a new menu item
    new_item = {
        "name": "Spicy Chicken Wrap",
        "description": "Grilled chicken with spicy sauce wrapped in a flour tortilla",
        "price": 10.99,
        "category": "Wraps",
        "available": True
    }
    test_api_endpoint("POST", "/menu", new_item)

    # Test creating a new location
    new_location = {
        "name": "Park Square",
        "address": "789 Park Ave",
        "latitude": 40.7649,
        "longitude": -73.9776,
        "schedule": "Sat-Sun: 10:00AM-4:00PM",
        "active": True
    }
    test_api_endpoint("POST", "/locations", new_location)

    # Test updated menu and locations
    print("\n" + "=" * 50)
    print("After adding new items:")
    test_api_endpoint("GET", "/menu")
    test_api_endpoint("GET", "/locations")

if __name__ == "__main__":
    main()