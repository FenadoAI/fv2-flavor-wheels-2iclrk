#!/usr/bin/env python3
"""
Complete functionality test for Food Truck website
Tests both backend API and simulates frontend usage
"""
import requests
import json

def test_complete_functionality():
    print("🚚 Testing Complete Food Truck Website Functionality")
    print("=" * 60)

    base_url = "http://localhost:8001/api"

    # Test 1: Food Truck Info
    print("\n1. Testing Food Truck Info...")
    try:
        response = requests.get(f"{base_url}/foodtruck")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Food Truck: {info['name']}")
            print(f"   📱 Phone: {info['phone']}")
            print(f"   📧 Email: {info.get('email', 'N/A')}")
        else:
            print("❌ Food truck info failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 2: Menu Items
    print("\n2. Testing Menu...")
    try:
        response = requests.get(f"{base_url}/menu")
        if response.status_code == 200:
            menu = response.json()
            print(f"✅ Found {len(menu)} menu items")

            categories = set(item['category'] for item in menu)
            for category in categories:
                items = [item for item in menu if item['category'] == category]
                print(f"   📋 {category}: {len(items)} items")
                for item in items[:2]:  # Show first 2 items
                    print(f"      • {item['name']} - ${item['price']}")
        else:
            print("❌ Menu failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 3: Locations
    print("\n3. Testing Locations...")
    try:
        response = requests.get(f"{base_url}/locations")
        if response.status_code == 200:
            locations = response.json()
            print(f"✅ Found {len(locations)} locations")

            for loc in locations:
                status = "🟢 Active" if loc['active'] else "🔴 Inactive"
                print(f"   📍 {loc['name']} - {status}")
                print(f"      {loc['address']}")
                if loc['schedule']:
                    print(f"      🕐 {loc['schedule']}")
        else:
            print("❌ Locations failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 4: CRUD Operations
    print("\n4. Testing CRUD Operations...")

    # Create new menu item
    new_item = {
        "name": "Test Burger",
        "description": "A test burger for functionality verification",
        "price": 15.99,
        "category": "Test",
        "available": True
    }

    try:
        response = requests.post(f"{base_url}/menu", json=new_item)
        if response.status_code == 200:
            created_item = response.json()
            item_id = created_item['id']
            print(f"✅ Created menu item: {created_item['name']} (ID: {item_id[:8]}...)")

            # Clean up - delete the test item
            delete_response = requests.delete(f"{base_url}/menu/{item_id}")
            if delete_response.status_code == 200:
                print("✅ Successfully deleted test item")
            else:
                print("⚠️  Test item created but cleanup failed")
        else:
            print("❌ Menu item creation failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 5: Frontend Data Structure
    print("\n5. Verifying Frontend Data Structure...")
    try:
        # Get all data that frontend needs
        info_response = requests.get(f"{base_url}/foodtruck")
        menu_response = requests.get(f"{base_url}/menu")
        locations_response = requests.get(f"{base_url}/locations")

        if all(r.status_code == 200 for r in [info_response, menu_response, locations_response]):
            info = info_response.json()
            menu = menu_response.json()
            locations = locations_response.json()

            # Check required fields for frontend
            required_info_fields = ['name', 'description', 'phone']
            required_menu_fields = ['name', 'description', 'price', 'category', 'available']
            required_location_fields = ['name', 'address', 'latitude', 'longitude', 'active']

            # Verify info structure
            info_valid = all(field in info for field in required_info_fields)
            print(f"✅ Food truck info structure: {'Valid' if info_valid else 'Invalid'}")

            # Verify menu structure
            menu_valid = all(all(field in item for field in required_menu_fields) for item in menu)
            print(f"✅ Menu structure: {'Valid' if menu_valid else 'Invalid'}")

            # Verify locations structure
            locations_valid = all(all(field in loc for field in required_location_fields) for loc in locations)
            print(f"✅ Locations structure: {'Valid' if locations_valid else 'Invalid'}")

            if not all([info_valid, menu_valid, locations_valid]):
                return False

        else:
            print("❌ Failed to fetch all required data")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 All tests passed! Food Truck website is fully functional!")
    print("🌐 Frontend should be running at: http://localhost:3000")
    print("🔌 Backend API is running at: http://localhost:8001")
    print("📖 API docs available at: http://localhost:8001/docs")

    return True

if __name__ == "__main__":
    success = test_complete_functionality()
    exit(0 if success else 1)