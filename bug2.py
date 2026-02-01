import requests
from requests_oauthlib import OAuth1
import xml.etree.ElementTree as ET

# Configuration
BUG_NUMBER = "CSCwr82677"

def create_auth():
    """
    Create OAuth1 authentication object for CDETS API
    
    Returns:
        OAuth1 authentication object
    """
    return OAuth1(
        client_key="a1fc1249-d5a8-4731-b6fd-45bac72dd354",
        client_secret="c0X7F9peBe3SZrzeltZmG8nAnm6eHCd6",
        signature_method="HMAC-SHA1"
    )

def get_file_content(bug_number, filename, auth):
    """
    Retrieve file contents from CDETS bug
    
    Args:
        bug_number: The bug ID (e.g., 'CSCvu26357')
        filename: The filename to retrieve
        auth: OAuth1 authentication object
    
    Returns:
        Response object with file content
    """
    url = f"https://cdetsng.cisco.com/wsapi/latest/api/bug/{bug_number}/file/{filename}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response

def get_bug_summary(bug_number, auth):
    """
    Retrieve bug summary/details from CDETS
    
    Args:
        bug_number: The bug ID (e.g., 'CSCvu26357')
        auth: OAuth1 authentication object
    
    Returns:
        Response object with bug details in XML format
    """
    url = f"https://cdetsng.cisco.com/wsapi/latest/api/bug/{bug_number}"
    headers = {"Accept": "application/xml"}
    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()
    return response

def get_note_info(bug_number, note_title, auth):
    """
    Retrieve note/enclosure information from CDETS
    
    Args:
        bug_number: The bug ID (e.g., 'CSCvu26357')
        note_title: The note/file title
        auth: OAuth1 authentication object
    
    Returns:
        Response object with note details in XML format
    """
    url = f"https://cdetsng.cisco.com/wsapi/latest/api/bug/{bug_number}/note/{note_title}/info"
    headers = {"Accept": "application/xml"}
    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()
    return response

def get_note_content(bug_number, note_title, auth):
    """
    Retrieve note content from CDETS
    
    Args:
        bug_number: The bug ID (e.g., 'CSCvu26357')
        note_title: The note title to retrieve
        auth: OAuth1 authentication object
    
    Returns:
        Response object with note content (plain text)
    """
    url = f"https://cdetsng.cisco.com/wsapi/latest/api/bug/{bug_number}/note/{note_title}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response

def get_all_notes(bug_number, auth):
    """
    Retrieve list of all notes from CDETS bug
    
    Args:
        bug_number: The bug ID (e.g., 'CSCvu26357')
        auth: OAuth1 authentication object
    
    Returns:
        List of note titles
    """
    url = f"https://cdetsng.cisco.com/wsapi/latest/api/bug/{bug_number}/notes"
    headers = {"Accept": "application/xml"}
    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()
    
    # Parse XML to extract note titles
    root = ET.fromstring(response.content)
    ns = {'cdets': 'cdetsng'}
    notes = []
    for note_elem in root.findall('.//cdets:Note', ns):
        for field in note_elem.findall('.//cdets:Field', ns):
            if field.get('name') == 'Title':
                notes.append(field.text)
                break
    return notes

def create_note(bug_number, note_title, note_content, note_type="Other", auth=None):
    """
    Create a note for a CDETS bug
    
    Args:
        bug_number: The bug ID (e.g., 'CSCvu26357')
        note_title: The title for the note
        note_content: The content/body of the note
        note_type: The type of note (default: "Other")
        auth: OAuth1 authentication object
    
    Returns:
        Response object from the API
    """
    url = f"https://cdetsng.cisco.com/wsapi/latest/api/bug/{bug_number}/note"
    headers = {
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }
    
    # Construct XML request body with correct format
    xml_body = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<Note xmlns="cdetsng" xmlns:ns1="http://www.w3.org/1999/xlink">
    <Field name="Note">{note_content}</Field>
    <Field name="Title">{note_title}</Field>
    <Field name="Type">{note_type}</Field>
</Note>"""
    
    response = requests.post(url, auth=auth, headers=headers, data=xml_body)
    response.raise_for_status()
    return response

if __name__ == "__main__":
    url = f"https://cdetsng.cisco.com/wsapi/latest/api/bug/{BUG_NUMBER}/files"

    auth = create_auth()

    # Create a note called "AI-Analysis"
    try:
        print("Creating AI-Analysis note...")
        response = create_note(BUG_NUMBER, "AI-Analysis", "this is the body", auth=auth)
        print(f"✓ Note created successfully: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.HTTPError as e:
        print(f"✗ Error creating note: {e}")
        if hasattr(e.response, 'text'):
            print(f"Server response: {e.response.text}")
    except Exception as e:
        print(f"✗ Error creating note: {e}")

    # Comment out file retrieval for now - testing note creation only
    """
    headers = {
        "Accept": "application/xml"
    }

    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()

    # Debug: print raw XML
    print("Raw XML response:")
    print(response.text)
    print("\n" + "="*80 + "\n")

    # Parse XML response
    root = ET.fromstring(response.content)

    # Define namespaces
    ns = {
        'cdets': 'cdetsng',
        'ns2': 'http://www.w3.org/1999/xlink'
    }

    # Store file information in a list of dictionaries
    files_list = []

    # Find all File elements with proper namespace
    for file_elem in root.findall('.//cdets:File', ns):
        file_info = {}
        
        # Extract all Field elements
        for field in file_elem.findall('.//cdets:Field', ns):
            field_name = field.get('name')
            file_info[field_name] = field.text
        
        # Add the download URL
        href = file_elem.get('{http://www.w3.org/1999/xlink}href')
        if href:
            file_info['DownloadURL'] = href
        
        files_list.append(file_info)

    # Print the data structure
    print(f"Found {len(files_list)} files:\n")

    if files_list:
        for i, file in enumerate(files_list, 1):
            filename = file.get('Filename', 'Unknown')
            print(f"{i}. {filename}")
            print(f"   Type: {file.get('FileType', 'N/A')}")
            print(f"   Size: {file.get('FileSize', 'N/A')} bytes")
            print(f"   Created: {file.get('CreatedOn', 'N/A')} by {file.get('CreatedBy', 'N/A')}")
            print(f"   URL: {file.get('DownloadURL', 'N/A')}")
            print(f"   ALL FIELDS: {file}")  # Debug: show all available fields
            
            print()

        # Example: Access individual files
        print("\nExample retrievals:")
        print(f"First file name: {files_list[0].get('Filename')}")
        print(f"All filenames: {[f.get('Filename') for f in files_list]}")
        
        # Download all files and append to markdown file
        print("\n" + "="*80)
        print("Downloading bug summary and files, appending to bug_files.md")
        print("="*80)
        
        markdown_file = "bug_files.md"
        bug_number = BUG_NUMBER
        
        with open(markdown_file, 'w', encoding='utf-8') as md:
            md.write(f"# Bug {bug_number} - Complete Report\n\n")
            md.write(f"Generated on: {response.headers.get('Date', 'N/A')}\n\n")
            md.write("---\n\n")
            
            # Get and append bug summary first
            print("\nFetching bug summary...")
            try:
                summary_response = get_bug_summary(bug_number, auth)
                summary_root = ET.fromstring(summary_response.content)
                
                # Define namespaces for parsing
                summary_ns = {'cdets': 'cdetsng', 'ns2': 'http://www.w3.org/1999/xlink'}
                
                md.write("## Bug Summary\n\n")
                
                # Extract key bug fields
                defect = summary_root.find('.//cdets:Defect', summary_ns)
                if defect:
                    for field in defect.findall('.//cdets:Field', summary_ns):
                        field_name = field.get('name')
                        field_value = field.text if field.text else 'N/A'
                        
                        # Only include key summary fields
                        if field_name in ['Headline', 'Status', 'Severity', 'Priority', 'Product', 
                                         'Component', 'Version', 'Description', 'FoundIn', 'FixedIn']:
                            md.write(f"- **{field_name}**: {field_value}\n")
                
                md.write("\n---\n\n")
                print("   ✓ Bug summary added")
                
            except Exception as e:
                md.write(f"*Error fetching bug summary: {e}*\n\n---\n\n")
                print(f"   ✗ Error: {e}")
            
            # Now append file contents
            md.write("## Attached Files\n\n")
            
            for i, file in enumerate(files_list, 1):
                filename = file.get('Filename', 'Unknown')
                filetype = file.get('FileType', 'N/A')
                filesize = file.get('FileSize', 'N/A')
                
                print(f"\n{i}. Processing {filename}...")
                md.write(f"### {i}. {filename}\n\n")
                md.write(f"- **Type**: {filetype}\n")
                md.write(f"- **Size**: {filesize} bytes\n")
                md.write(f"- **Created**: {file.get('CreatedOn', 'N/A')} by {file.get('CreatedBy', 'N/A')}\n")
                md.write(f"- **URL**: {file.get('DownloadURL', 'N/A')}\n\n")
                
                # Check if it's a text file BEFORE downloading
                if 'text' in filetype.lower() or 'ascii' in filetype.lower():
                    try:
                        file_response = get_file_content(BUG_NUMBER, filename, auth)
                        md.write("**Content:**\n\n")
                        md.write("```\n")
                        md.write(file_response.text)
                        md.write("\n```\n\n")
                        print(f"   ✓ Downloaded and appended text content ({len(file_response.content)} bytes)")
                    except Exception as e:
                        md.write(f"*Error downloading file: {e}*\n\n")
                        print(f"   ✗ Error: {e}")
                else:
                    md.write(f"*Binary file - skipped download*\n\n")
                    print(f"   ⊗ Skipped binary file (no download)")
                
                md.write("\n")
        
        print(f"\n✓ All files processed and saved to {markdown_file}")
        
    else:
        print("No files found in the response.")
    """
