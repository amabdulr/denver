#!/usr/bin/env python3
"""
Test fetching Component field from a bug
"""
from bug2 import create_auth, get_bug_field_values

def test_component_field(bug_number):
    """Test fetching Component field"""
    auth = create_auth()
    
    print(f"Testing bug {bug_number}...")
    print("=" * 60)
    
    # Test fetching Component field
    print("\n1. Fetching Component field:")
    try:
        field_values = get_bug_field_values(bug_number, 'Component', auth)
        print(f"   Component: {field_values.get('Component', 'NOT FOUND')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test fetching To-be-fixed field
    print("\n2. Fetching To-be-fixed field:")
    try:
        field_values = get_bug_field_values(bug_number, 'To-be-fixed', auth)
        print(f"   To-be-fixed: {field_values.get('To-be-fixed', 'NOT FOUND')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test fetching multiple fields at once
    print("\n3. Fetching multiple fields (Component, To-be-fixed, Status):")
    try:
        field_values = get_bug_field_values(bug_number, 'Component,To-be-fixed,Status', auth)
        for field_name, field_value in field_values.items():
            print(f"   {field_name}: {field_value}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        bug_number = sys.argv[1]
    else:
        bug_number = "CSCwr71167"  # Default bug
    
    test_component_field(bug_number)
