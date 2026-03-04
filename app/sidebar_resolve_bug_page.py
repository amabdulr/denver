"""
Resolve Bug Sidebar Page Component
Handles the Bug Resolution workflow for sidebar navigation app
"""

import streamlit as st
import os
from paths import PROJECT_ROOT
from bug2 import create_auth, get_bug_summary, get_bug_field_values, create_note


def send_resolution_email(recipient_username, bug_number, email_body_content, engineer_name="", subject=None):
    """
    Send bug resolution email to submitter(s)
    
    Args:
        recipient_username: Username(s) without @cisco.com. Can be a single username
            (e.g., 'amabdulr') or comma-separated usernames (e.g., 'amabdulr, johndoe').
        bug_number: The bug number
        email_body_content: The complete email body content (already formatted)
        engineer_name: Name of the engineer resolving the bug
        subject: Optional custom subject line. If None, defaults to 'Doc Bug {bug_number} Resolution'
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Support comma-separated recipient usernames
        usernames = [u.strip() for u in recipient_username.split(',') if u.strip()]
        if not usernames:
            return (False, "No valid recipient usernames provided.")
        
        recipient_emails = [f"{u}@cisco.com" for u in usernames]
        sender_email = f"{engineer_name.replace(' ', '.').lower()}@cisco.com" if engineer_name else recipient_emails[0]
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipient_emails)
        msg['Subject'] = subject if subject else f"Doc Bug {bug_number} Resolution"
        
        # Use the email body content as-is (already formatted with greeting, resolution, and signature)
        msg.attach(MIMEText(email_body_content, 'plain'))
        
        # Try common Cisco SMTP servers
        smtp_servers = ['outbound.cisco.com', 'smtp.cisco.com', 'localhost']
        
        for smtp_server in smtp_servers:
            try:
                server = smtplib.SMTP(smtp_server, timeout=5)
                text = msg.as_string()
                server.sendmail(sender_email, recipient_emails, text)
                server.quit()
                return (True, f"Email sent successfully to {', '.join(recipient_emails)} via {smtp_server}")
            except Exception as server_error:
                continue
        
        return (False, "Could not send email - all SMTP servers failed. Please check network connectivity.")
        
    except Exception as e:
        return (False, f"Error sending email: {str(e)}")


def render_resolve_bug_page():
    """Render the Resolve Bug page with full functionality for sidebar navigation"""
    st.header("🔧 Resolve Bug")
    st.markdown("Create resolution comments for CDETS bugs")
    
    # Step-by-step instructions
    with st.expander("📖 How to Use This Page", expanded=False):
        st.markdown("""
        #### Resolve CDETS Bugs with AI Assistance
        
        **Step 1: Fetch Bug Information**
        1. **Enter Bug Number**: Type the CDETS bug number (e.g., CSCwp05354) in the left column
        2. **Fetch Metadata**: Click "📥 Fetch Bug Metadata" to retrieve bug details from CDETS
        3. **Review Metadata**: Check the displayed bug information (Headline, Status, Severity, Product, etc.)
        
        **Step 2: Generate Resolution Comment**
                    
        1. Include the change description. 
        2. **Enter Chapter/Location**: Use the Number of Books/Chapters if more than one documentation location was impacted. For each location, provide the necessary details. 
        3. **Generate Comment**: Click "✨ Create Resolution Comment" in the right column
        
        **Step 3: Post and Notify**
        1. **Edit Comment** (optional): Modify the generated comment if needed
        2. **Post to CDETS**: Click "📤 Post Comment to CDETS" to add the resolution comment to the bug
        3. **Send Email** (optional): 
           - Modify your name for the email signature
           - Click "📧 Send email to submitter" to notify the submitter. Currently set to amabadulr@cisco.com.
        4. **Confirm Actions**: Check for success messages confirming the comment was posted and email sent
        
        **Tips**:
        - All bug metadata is automatically included in the resolution comment
        - The email uses a professional template with your resolution details
        - You can copy the comment before posting to save it externally
        - Make sure you're connected to Cisco network for CDETS access
        """)
    
    st.markdown("---")
    
    col1_resolve, col2_resolve = st.columns([1, 1])
    
    with col1_resolve:
        st.subheader("📝 Bug Information")
        
        # Bug number input
        resolve_bug_number = st.text_input(
            "Bug Number",
            placeholder="e.g., CSCwp05354",
            help="Enter a CDETS bug number",
            key="sidebar_resolve_bug_number"
        )
        
        # Fetch Metadata button
        fetch_metadata_button = st.button(
            "📥 Fetch Bug Metadata",
            type="primary",
            use_container_width=True,
            help="Fetch bug information and populate fields",
            key="sidebar_fetch_metadata"
        )
    
    # Handle Fetch Metadata button
    if fetch_metadata_button:
        if not resolve_bug_number.strip():
            st.error("⚠️ Please enter a bug number")
        else:
            with st.spinner("Fetching bug info..."):
                try:
                    auth = create_auth()
                    bug_summary = get_bug_summary(resolve_bug_number, auth)
                    st.session_state.resolve_bug_summary = bug_summary
                    
                    # Fetch key fields including Submitter and Engineer
                    fields = ["Component", "Product", "Version", "Status", "Submitter", "Engineer"]
                    field_values = get_bug_field_values(resolve_bug_number, fields, auth)
                    st.session_state.resolve_field_values = field_values
                    
                    # Auto-populate from bug fields
                    if 'Product' in field_values:
                        st.session_state.product_value = field_values['Product']
                    if 'Version' in field_values:
                        st.session_state.version_value = field_values['Version']
                    if 'Component' in field_values:
                        st.session_state.component_value = field_values['Component']
                    if 'Submitter' in field_values:
                        st.session_state.submitter_value = field_values['Submitter']
                    if 'Engineer' in field_values:
                        st.session_state.engineer_value = field_values['Engineer']
                    
                    st.success("✅ Bug info fetched and fields populated!")
                    st.session_state.resolve_data_fetched = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    with st.expander("🐛 Error Details"):
                        st.exception(e)
    
    # Show fields only after data has been fetched
    if st.session_state.get('resolve_data_fetched', False):
        st.markdown("---")
        
        # Platform (editable, pre-populated from bug metadata)
        product_value = st.text_input(
            "Platform",
            value=st.session_state.get('product_value', ''),
            placeholder="e.g., ewlc, sdwan",
            key="sidebar_product_input_resolve"
        )
        
        # Version (editable, pre-populated from bug metadata)
        version_value = st.text_input(
            "Version(s)",
            value=st.session_state.get('version_value', ''),
            placeholder="e.g., 17.9.5",
            key="sidebar_version_input_resolve"
        )
        
        # Technology (editable, pre-populated from bug metadata)
        component_value = st.text_input(
            "Technology",
            value=st.session_state.get('component_value', ''),
            placeholder="e.g., ewlc-docs, sdwan-routing",
            key="sidebar_component_input_resolve"
        )
        
        # Submitter (editable, pre-populated from bug metadata)
        submitter_value = st.text_input(
            "Submitter",
            value=st.session_state.get('submitter_value', ''),
            placeholder="Bug submitter",
            key="sidebar_submitter_input_resolve"
        )
        
        # Engineer (editable, pre-populated from bug metadata)
        engineer_value = st.text_input(
            "Engineer",
            value=st.session_state.get('engineer_value', ''),
            placeholder="Assigned engineer",
            key="sidebar_engineer_input_resolve"
        )
        
        st.markdown("---")
        
        # RCA Type dropdown
        rca_type_options = [
            "Eng.Escape_Restrictions",
            "Eng.Escape_Unnotified-Behavior-Change",
            "Eng.Escape_InaccurateReview",
            "Doc.Escape_GeneralErrors",
            "Doc.Escape_Content_Issue",
            "Doc.Escape_Profiling",
            "Doc.Enhancement-Future_Release",
            "Doc.WalkMe_UI_Errors",
            "Eng.Escape_WalkMe-UI-jQuery-Change",
            "WalkMe.Escape_Known-Limitations",
            "WalkMe.Escape_Issues",
            "Third-party.Escape",
            "Eng.Escape_InaccurateContent",
            "Eng.Escape_Unnotified-Feature",
            "Eng.Process-Escape"
        ]
        
        rca_type = st.selectbox(
            "RCA Type",
            options=rca_type_options,
            help="Select the RCA type",
            key="sidebar_rca_type"
        )
        
        st.markdown("---")
        
        # Change Description
        change_description = st.text_area(
            "Change Description",
            value="",
            height=100,
            placeholder="Describe the documentation changes made...",
            help="Enter a description of the changes made",
            key="sidebar_change_description"
        )
        
        st.markdown("---")
        
        # Number of Books/Chapters section
        st.subheader("📚 Documentation Locations")
        
        num_locations = st.number_input(
            "Number of Books/Chapters",
            min_value=1,
            max_value=10,
            value=1,
            step=1,
            help="Increase if more documentation locations are impacted by this bug",
            key="sidebar_num_locations"
        )
        
        # Create dynamic fields for each location
        for i in range(int(num_locations)):
            st.markdown(f"**Location {i+1}**")
            
            col_book, col_chapter = st.columns(2)
            with col_book:
                book = st.text_input(
                    "Book",
                    value="",
                    placeholder="Enter book name",
                    key=f"sidebar_book_{i}",
                    label_visibility="visible"
                )
            
            with col_chapter:
                chapter = st.text_input(
                    "Chapter",
                    value="",
                    placeholder="Enter chapter",
                    key=f"sidebar_chapter_{i}",
                    label_visibility="visible"
                )
            
            topic = st.text_input(
                "Topic",
                value="",
                placeholder="Enter topic",
                key=f"sidebar_topic_{i}",
                label_visibility="visible"
            )
            
            details = st.text_area(
                "Details",
                value="",
                height=100,
                placeholder="Enter details of the change...",
                key=f"sidebar_details_{i}",
                label_visibility="visible"
            )
            
            url = st.text_input(
                "URL",
                value="",
                placeholder="Enter URL",
                key=f"sidebar_url_{i}",
                label_visibility="visible"
            )
            
            if i < int(num_locations) - 1:
                st.markdown("---")
        
        st.markdown("---")
        
        # Create Resolution Comment button
        col_create, col_post = st.columns(2)
        
        with col_create:
            create_resolution_button = st.button(
                "📝 Create Resolution Comment",
                type="secondary",
                use_container_width=True,
                help="Generate formatted resolution comment",
                key="sidebar_create_resolution"
            )
        
        # Handle Create Resolution Comment
        if create_resolution_button:
            # Build resolution comment
            resolution_lines = []
            resolution_lines.append(f"RCA: {rca_type}")
            resolution_lines.append(f"Platform: {product_value}")
            resolution_lines.append(f"Version(s): {version_value}")
            resolution_lines.append(f"Technology: {component_value}")
            resolution_lines.append("")
            resolution_lines.append(f"Change Description: {change_description}")
            resolution_lines.append("")
            
            # Add each location
            for i in range(int(num_locations)):
                book_val = st.session_state.get(f'sidebar_book_{i}', '')
                chapter_val = st.session_state.get(f'sidebar_chapter_{i}', '')
                topic_val = st.session_state.get(f'sidebar_topic_{i}', '')
                details_val = st.session_state.get(f'sidebar_details_{i}', '')
                url_val = st.session_state.get(f'sidebar_url_{i}', '')
                
                resolution_lines.append(f"Book: {book_val}")
                resolution_lines.append(f"Chapter: {chapter_val}")
                resolution_lines.append(f"Topic: {topic_val}")
                resolution_lines.append(f"Details: {details_val}")
                resolution_lines.append(f"URL: {url_val}")
                if i < int(num_locations) - 1:
                    resolution_lines.append("")
            
            resolution_comment = "\n".join(resolution_lines)
            st.session_state.resolution_comment = resolution_comment
            
            # Create email body
            engineer_name = st.session_state.get('engineer_value', '')
            email_body = f"""Hello,

Please find the resolution of the bug {resolve_bug_number}.

{resolution_comment}

Thanks and Regards,
{engineer_name}"""
            st.session_state.email_body = email_body
            
            st.success("✅ Resolution comment created!")
        
        # Show preview if comment has been created
        if 'resolution_comment' in st.session_state and st.session_state.resolution_comment:
            with st.expander("📝 Preview Resolution Comment", expanded=True):
                st.text(st.session_state.resolution_comment)
            
            # Editable email preview
            st.markdown("---")
            st.subheader("📧 Email to Submitter")
            
            # Subject line (smart default like Tab 1)
            default_subject = f"Doc Bug {resolve_bug_number} Resolution"
            resolve_email_subject = st.text_input(
                "Subject Line",
                value=st.session_state.get('resolve_email_subject', default_subject),
                placeholder="e.g., Doc Bug CSCws27686 Resolution",
                help="Subject line for the email",
                key="resolve_email_subject"
            )
            
            # Recipient (auto-populated from Submitter, editable)
            default_recipient = st.session_state.get('submitter_value', '')
            resolve_email_recipient = st.text_input(
                "Recipient(s)",
                value=default_recipient,
                placeholder="e.g., johndoe or johndoe, janedoe",
                help="Auto-populated from CDETS Submitter. Comma-separated usernames (without @cisco.com).",
                key="resolve_email_recipient"
            )
            
            # Sender name (persisted via saved tester name like Tab 1)
            from sidebar_app import get_saved_tester_name
            saved_name = get_saved_tester_name()
            fallback_name = saved_name if saved_name else st.session_state.get('engineer_value', '')
            resolve_email_sender = st.text_input(
                "Your Name (for signature)",
                value=fallback_name,
                placeholder="Enter your name",
                help="This name will appear in the email signature",
                key="resolve_email_sender_name"
            )
            
            # Recipient preview
            if resolve_email_recipient.strip():
                recipients_display = ', '.join(f"{u.strip()}@cisco.com" for u in resolve_email_recipient.split(',') if u.strip())
                st.info(f"📬 Will send to: **{recipients_display}**")
            
            email_content = st.text_area(
                "Email Content",
                value=st.session_state.get('email_body', ''),
                height=300,
                help="Edit the email content before sending",
                key="sidebar_email_content_edit"
            )
        
        # Email option checkbox
        send_email = st.checkbox(
            "📧 Send email to submitter",
            value=False,
            help="Send resolution email to the bug submitter",
            key="sidebar_send_email"
        )
        
        # Post Resolution Comment button (only show after creating)
        with col_post:
            post_resolution_button = st.button(
                "📤 Post Resolution Comment",
                type="primary",
                use_container_width=True,
                help="Post the resolution comment to the bug",
                key="sidebar_post_resolution"
            )
        
        # Handle Post Resolution Comment
        if post_resolution_button:
            if not resolve_bug_number.strip():
                st.error("⚠️ Please enter a bug number")
            else:
                with st.spinner(f"📤 Posting resolution comment to {resolve_bug_number}..."):
                    try:
                        auth = create_auth()
                        response = create_note(
                            bug_number=resolve_bug_number,
                            note_title="R-comments",
                            note_content=st.session_state.resolution_comment,
                            note_type="R-comments",
                            auth=auth
                        )
                        st.success(f"✅ Resolution comment posted successfully!")
                        st.info(f"Response status: {response.status_code}")
                        
                        # Display bug link
                        bug_url = f"https://cdetsng.cisco.com/webui/#view={resolve_bug_number}"
                        st.markdown(f"🔗 **View Bug:** [{resolve_bug_number}]({bug_url})")
                        
                        # Send email if checkbox is selected
                        if send_email:
                            recipient = st.session_state.get('resolve_email_recipient', st.session_state.get('submitter_value', ''))
                            sender_name = st.session_state.get('resolve_email_sender_name', st.session_state.get('engineer_value', ''))
                            custom_subject = st.session_state.get('resolve_email_subject', '')
                            
                            if not recipient.strip():
                                st.error("⚠️ Please enter at least one recipient username.")
                            else:
                                # Use edited email content if available
                                email_content_to_send = st.session_state.get('sidebar_email_content_edit', st.session_state.get('email_body', ''))
                                recipients_display = ', '.join(f"{u.strip()}@cisco.com" for u in recipient.split(',') if u.strip())
                                
                                with st.spinner(f"📧 Sending email to {recipients_display}..."):
                                    success, message = send_resolution_email(
                                        recipient.strip(),
                                        resolve_bug_number,
                                        email_content_to_send,
                                        sender_name,
                                        subject=custom_subject
                                    )
                                    if success:
                                        st.success(f"📧 {message}")
                                    else:
                                        st.warning(f"⚠️ {message}")
                        
                        # Clear the created comment after posting
                        del st.session_state.resolution_comment
                    except Exception as e:
                        st.error(f"❌ Error posting comment: {str(e)}")
                        with st.expander("🐛 Error Details"):
                            st.exception(e)
    else:
        # Show message when no data has been fetched yet
        with col2_resolve:
            st.info("👈 Enter a bug number and click 'Fetch Bug Metadata' to get started")
    
    # Test Section
    st.markdown("---")
    st.subheader("🧪 Capture your test results!")
    
    with st.expander("📝 Test Results", expanded=False):
        st.markdown("Capture test results for resolve bug workflow")
        
        # Feature being tested
        resolve_test_feature = st.text_input(
            "Feature to be tested",
            placeholder="e.g., bug analysis, bug summarize, bulk RCA, bulk bugs, First draft, resolve bug",
            help="Enter the specific feature or functionality being tested",
            key="resolve_test_feature"
        )
        
        # Name of tester
        resolve_tester_name = st.text_input(
            "Name of tester",
            placeholder="Enter your name",
            help="Name of the person performing the test",
            key="resolve_tester_name"
        )
        
        # Comments text area
        resolve_test_comments = st.text_area(
            "Comments",
            placeholder="Enter any additional comments or observations...",
            height=100,
            key="resolve_test_comments"
        )
        
        # Wishlist text area
        resolve_test_wishlist = st.text_area(
            "Wishlist",
            placeholder="Enter feature requests, improvements, or wishlist items...",
            height=100,
            key="resolve_test_wishlist"
        )
        
        # Usefulness Rating
        st.markdown("---")
        resolve_usefulness = st.radio(
            "How useful is this feature?",
            options=[
                "⛔ I'd rather do this without AI",
                "🤔 Neutral - No strong preference",
                "👍 Yes, this is useful",
                "⭐ I'd prefer CIRCUIT over manual work"
            ],
            index=2,
            help="Rate how useful you find this AI-assisted feature",
            key="resolve_usefulness_rating"
        )
        
        # Add to Excel button
        resolve_add_to_excel_button = st.button(
            "📊 Add to Test Excel",
            type="primary",
            use_container_width=True,
            key="resolve_add_to_test_excel"
        )
        
        if resolve_add_to_excel_button:
            # Import the function from sidebar_app
            from sidebar_app import save_test_results_to_excel
            import os
            
            # Get the output content (resolution comment) if available
            output_content = "N/A"
            if 'resolution_comment' in st.session_state and st.session_state.resolution_comment:
                output_content = st.session_state.resolution_comment
            
            # Save to Excel with N/A for bug number and both sliders
            try:
                save_test_results_to_excel(
                    page_name="Resolve Bug",
                    feature=resolve_test_feature,
                    tester_name=resolve_tester_name,
                    bug_number="N/A",
                    output_content=output_content,
                    location_accuracy="N/A",
                    content_accuracy="N/A",
                    comments=resolve_test_comments,
                    wishlist=resolve_test_wishlist,
                    usefulness=resolve_usefulness
                )
                st.success("✅ Test results saved to testresults.xlsx!")
                
                # Provide download link
                try:
                    with open(os.path.join(PROJECT_ROOT, "tests", "testresults.xlsx"), "rb") as file:
                        st.download_button(
                            label="📥 Download testresults.xlsx",
                            data=file,
                            file_name="testresults.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="resolve_download_test_results"
                        )
                except:
                    pass
            except Exception as e:
                st.error(f"❌ Error saving to Excel: {str(e)}")
                with st.expander("🐛 Error Details"):
                    st.exception(e)
