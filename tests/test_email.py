#!/usr/bin/env python3
"""
Test sending email for bug resolution
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_resolution_email(recipient_username, bug_number, resolution_comment, engineer_name=""):
    """
    Send bug resolution email to submitter
    
    Args:
        recipient_username: Username without @cisco.com (e.g., 'amabdulr')
        bug_number: The bug number
        resolution_comment: The resolution comment text
        engineer_name: Name of the engineer resolving the bug
    """
    # Construct email address
    recipient_email = f"{recipient_username}@cisco.com"
    sender_email = f"{recipient_username}@cisco.com"  # Using same for testing
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Doc Bug {bug_number} Resolution"
    
    # Email body
    body = f"""Hello,

Please find the resolution of the bug {bug_number}.

{resolution_comment}

Thanks and Regards,
{engineer_name}
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    print(f"Attempting to send email to: {recipient_email}")
    print("=" * 60)
    print("Subject:", msg['Subject'])
    print("\nBody:")
    print(body)
    print("=" * 60)
    
    try:
        # Try common Cisco SMTP servers
        smtp_servers = ['outbound.cisco.com', 'smtp.cisco.com', 'localhost']
        
        for smtp_server in smtp_servers:
            try:
                print(f"\nTrying SMTP server: {smtp_server}")
                server = smtplib.SMTP(smtp_server, timeout=5)
                
                # Send email
                text = msg.as_string()
                server.sendmail(sender_email, recipient_email, text)
                server.quit()
                
                print(f"\n✓ Email sent successfully to {recipient_email} via {smtp_server}")
                return True
                
            except Exception as server_error:
                print(f"  Failed with {smtp_server}: {server_error}")
                continue
        
        print(f"\n✗ Could not send email - all SMTP servers failed")
        return False
        
    except Exception as e:
        print(f"\n✗ Error sending email: {e}")
        print("\nNote: Email sending requires proper SMTP configuration.")
        print("On Cisco network, you may need to use 'outbound.cisco.com' or similar SMTP server.")
        return False

if __name__ == "__main__":
    # Test email
    test_recipient = "amabdulr"
    test_bug = "CSCwr71167"
    test_engineer = "Arun Mabdullah"
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
    
    send_resolution_email(test_recipient, test_bug, test_resolution, test_engineer)
