#!/usr/bin/env python3
"""
Test posting R-comments to a bug
"""
from bug2 import create_auth, create_note

def test_post_r_comment(bug_number):
    """Test posting an R-comment to a bug"""
    
    # Create dummy resolution comment
    dummy_resolution = """RCA: Doc.Escape_GeneralErrors
Platform: ewlc
Version(s): 17.9.5
Technology: ewlc-docs

Change Description: Fixed documentation error in the configuration guide

Book: Cisco Catalyst 9800 Series Wireless Controller Configuration Guide
Chapter: System Management
Topic: Login Security
Details: Updated the section to clarify that the sl_def_acl is automatically removed after the block period expires during normal operation, but may persist during HA switchover events. Added troubleshooting steps for manual removal if needed.
URL: https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/config-guide/b_wl_16_10_cg.html
"""
    
    print(f"Testing R-comment post to bug {bug_number}...")
    print("=" * 60)
    
    try:
        auth = create_auth()
        
        print("\n1. Creating R-comment note...")
        response = create_note(
            bug_number=bug_number,
            note_title="R-comments",
            note_content=dummy_resolution,
            note_type="R-comments",
            auth=auth
        )
        
        print(f"   ✓ Success! Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}..." if len(response.text) > 200 else f"   Response: {response.text}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        bug_number = sys.argv[1]
    else:
        bug_number = "CSCwr71167"  # Default bug
    
    test_post_r_comment(bug_number)
