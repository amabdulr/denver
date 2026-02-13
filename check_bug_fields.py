#!/usr/bin/env python3
"""
Quick script to check what fields are available in a bug
"""
from bug2 import create_auth, get_bug_summary
import xml.etree.ElementTree as ET

def list_all_bug_fields(bug_number, highlight_fields=None):
    """List all available fields in a bug
    
    Args:
        bug_number: The bug ID to fetch
        highlight_fields: List of field names to highlight (case-insensitive)
    """
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
        
        # Show highlighted fields first if specified
        if highlight_fields:
            highlight_lower = [f.lower() for f in highlight_fields]
            highlighted = [(name, val) for name, val in fields if name.lower() in highlight_lower]
            
            if highlighted:
                print("📌 HIGHLIGHTED FIELDS:")
                print("-" * 60)
                for field_name, field_value in highlighted:
                    display_value = field_value[:80] + "..." if len(field_value) > 80 else field_value
                    print(f"  ⭐ {field_name:28} = {display_value}")
                print()
        
        print("ALL FIELDS:")
        print("-" * 60)
        
        # Determine if we're highlighting fields
        highlight_lower = [f.lower() for f in (highlight_fields or [])]
        
        for field_name, field_value in fields:
            # Truncate long values
            display_value = field_value[:80] + "..." if len(field_value) > 80 else field_value
            
            # Mark highlighted fields
            if highlight_lower and field_name.lower() in highlight_lower:
                print(f"  ⭐ {field_name:28} = {display_value}")
            else:
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
        # Additional args are fields to highlight
        highlight_fields = sys.argv[2:] if len(sys.argv) > 2 else ['Documentation-link']
    else:
        bug_number = "CSCwq89779"  # Default bug
        highlight_fields = ['Documentation-link']
    
    try:
        list_all_bug_fields(bug_number, highlight_fields)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
