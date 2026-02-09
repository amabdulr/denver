#!/usr/bin/env python3
"""
Quick script to check what fields are available in a bug
"""
from bug2 import create_auth, get_bug_summary
import xml.etree.ElementTree as ET

def list_all_bug_fields(bug_number):
    """List all available fields in a bug"""
    auth = create_auth()
    
    print(f"Fetching bug {bug_number}...")
    response = get_bug_summary(bug_number, auth)
    
    root = ET.fromstring(response.content)
    ns = {'cdets': 'cdetsng'}
    
    print(f"\n{'='*60}")
    print(f"Available fields in bug {bug_number}:")
    print(f"{'='*60}\n")
    
    defect = root.find('.//cdets:Defect', ns)
    if defect:
        fields = []
        for field_elem in defect.findall('.//cdets:Field', ns):
            field_name = field_elem.get('name')
            field_value = field_elem.text if field_elem.text else '(empty)'
            fields.append((field_name, field_value))
        
        # Sort by field name
        fields.sort()
        
        for field_name, field_value in fields:
            # Truncate long values
            display_value = field_value[:80] + "..." if len(field_value) > 80 else field_value
            print(f"  {field_name:30} = {display_value}")
        
        print(f"\n{'='*60}")
        print(f"Total fields: {len(fields)}")
        print(f"{'='*60}")
        
        # Check specifically for To-be-fixed
        to_be_fixed_found = any(name == 'To-be-fixed' for name, _ in fields)
        print(f"\n'To-be-fixed' field exists: {to_be_fixed_found}")
        
        if not to_be_fixed_found:
            # Check for similar field names
            similar = [name for name, _ in fields if 'fix' in name.lower() or 'to' in name.lower()]
            if similar:
                print(f"\nSimilar field names found: {', '.join(similar)}")
    else:
        print("No defect found in response")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        bug_number = sys.argv[1]
    else:
        bug_number = "CSCwr71167"  # Default bug from the error
    
    try:
        list_all_bug_fields(bug_number)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
