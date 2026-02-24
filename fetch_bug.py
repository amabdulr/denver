#!/usr/bin/env python3
"""Fetch bug content from CDETS."""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from bug2 import create_auth, get_bug_summary, get_all_notes, get_note_content, safe_parse_cdets_xml

bug_number = 'CSCwp97550'
auth = create_auth()
ns = {'cdets': 'cdetsng', 'ns2': 'http://www.w3.org/1999/xlink'}

summary_response = get_bug_summary(bug_number, auth)
summary_root = safe_parse_cdets_xml(summary_response.content)

defect = summary_root.find('.//cdets:Defect', ns)
if defect:
    for field in defect.findall('.//cdets:Field', ns):
        name = field.get('name')
        val = field.text if field.text else 'N/A'
        if name in ['Headline', 'Status', 'Severity', 'Product', 'Component', 'Version', 'Description']:
            print(f"\n{name}: {val}")

try:
    note_titles = get_all_notes(bug_number, auth)
    print(f"\nNotes ({len(note_titles)}):")
    for title in note_titles[:6]:
        try:
            note_resp = get_note_content(bug_number, title, auth)
            content = note_resp.text[:1000] if note_resp.text else '(empty)'
            print(f"\n--- {title} ---")
            print(content)
        except Exception as e:
            print(f"  Error: {e}")
except Exception as e:
    print(f"Notes error: {e}")
