#!/usr/bin/env python3
"""
Test the Post Resolution Comment functionality
"""
from bug2 import create_auth, create_note

def test_post_resolution():
    """
    Test posting a resolution comment to a bug
    """
    # Test data
    test_bug_number = "CSCwr71167"  # Use a test bug number
    test_resolution = """RCA: Doc.Escape_GeneralErrors
Platform: ewlc
Version(s): 17.9.5
Technology: ewlc-docs

Change Description: Fixed documentation error in the configuration guide

Book: Cisco Catalyst 9800 Series Wireless Controller Configuration Guide
Chapter: System Management
Topic: Login Security
Details: Updated the section to clarify sl_def_acl behavior during HA events.
URL: https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/config-guide/"""
    
    print(f"Testing Post Resolution Comment for bug: {test_bug_number}")
    print("=" * 60)
    print("\nResolution Comment to be posted:")
    print("-" * 60)
    print(test_resolution)
    print("-" * 60)
    
    try:
        # Create authentication
        auth = create_auth()
        print("\n✓ Authentication created successfully")
        
        # Test posting the note
        print(f"\nAttempting to post R-comment to {test_bug_number}...")
        response = create_note(
            bug_number=test_bug_number,
            note_title="R-comments",
            note_content=test_resolution,
            note_type="R-comments",
            auth=auth
        )
        
        print(f"\n✓ Response Status Code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✓ Resolution comment posted successfully!")
            return True
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("POST RESOLUTION COMMENT TEST")
    print("=" * 60)
    success = test_post_resolution()
    print("\n" + "=" * 60)
    if success:
        print("TEST PASSED ✓")
    else:
        print("TEST FAILED ✗")
