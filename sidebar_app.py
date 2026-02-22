"""
Streamlit App - Cisco Documentation Assistant (Sidebar Navigation)
Main application file with sidebar-based navigation
Analysis & Summary - Full Implementation
"""

import streamlit as st
from dotenv import load_dotenv
from bug2 import create_auth, get_bug_summary, get_file_content, get_note_content, get_all_notes, create_note, get_bug_field_values, safe_parse_cdets_xml
import xml.etree.ElementTree as ET
import requests
import json
import os
import hashlib
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook, Workbook

# Import helper functions
from app_functions import run_agent, format_output, apply_prompt_file, extract_doc_clues_data, match_terms_to_guides
from utils import get_llm
from sidebar_first_draft_page import render_first_draft_page
from sidebar_bulk_analysis_page import render_bulk_analysis_page
from sidebar_resolve_bug_page import render_resolve_bug_page
from sidebar_hallucination_check_page import render_hallucination_check_page

# Load the .env file
load_dotenv()

# Config file for persistent settings
CONFIG_FILE = "app_config.json"

# Set page config FIRST - must be the first Streamlit command
st.set_page_config(
    page_title="Bug Doctor - Cisco Documentation Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_config():
    """Load application configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Save application configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def get_saved_product():
    """Get the saved product name from config"""
    config = load_config()
    return config.get('product_name', 'Cisco 9800')

def save_product_preference(product_name):
    """Save the product name preference"""
    config = load_config()
    config['product_name'] = product_name
    save_config(config)

def get_saved_tester_name():
    """Get the saved tester name from config"""
    config = load_config()
    return config.get('tester_name', '')

def save_tester_name(tester_name):
    """Save the tester name preference"""
    config = load_config()
    config['tester_name'] = tester_name
    save_config(config)

def get_available_guides(product_name):
    """Get list of available PDF guides for a product from the vector store"""
    try:
        # Check if vector store is initialized in session state
        if 'vector_store' not in st.session_state or st.session_state.vector_store is None:
            # Vector store not initialized yet, return empty list
            return []
        
        vectorstore = st.session_state.vector_store
        
        # Map UI product names to internal product codes
        product_mapping = {
            "Cisco SD-WAN": "sdwan",
            "Cisco 9800": "9800",
            "ASR 9000": "ASR9000",
            "Cisco 8000": "Cisco8000",
            "cisco_generic": "cisco_generic"
        }
        
        product_code = product_mapping.get(product_name, product_name)
        
        # Query vector store to get unique sources for this product
        results = vectorstore.get(
            where={"product": product_code},
            include=["metadatas"]
        )
        
        # Extract unique guide names (PDF filenames only)
        guides = set()
        for metadata in results.get('metadatas', []):
            source = metadata.get('source', '')
            if source and source.endswith('.pdf'):
                # Extract just the filename
                guide_name = source.split('/')[-1]
                guides.add(guide_name)
        
        return sorted(list(guides))
    except Exception as e:
        st.error(f"Error retrieving guides: {str(e)}")
        return []

def estimate_tokens(text):
    """Rough token estimation: ~4 chars per token"""
    return len(text) // 4

def get_relevant_context(conversation_history, window_size=3, max_tokens=4000):
    """
    Get relevant context from conversation history with token limits
    
    Args:
        conversation_history: List of Q&A exchanges
        window_size: Number of recent exchanges to include
        max_tokens: Maximum tokens for context
    
    Returns:
        Formatted context string
    """
    if not conversation_history:
        return ""
    
    # Get last N exchanges
    recent_exchanges = conversation_history[-window_size:] if len(conversation_history) > window_size else conversation_history
    
    # Build context with token awareness
    context_parts = []
    total_tokens = 0
    
    for idx, exchange in enumerate(reversed(recent_exchanges), 1):
        # Format exchange
        exchange_text = f"Previous Q{len(recent_exchanges)-idx+1}: {exchange['question']}\nPrevious A{len(recent_exchanges)-idx+1}: {exchange['answer'][:1000]}...\n"  # Limit answer preview
        
        tokens = estimate_tokens(exchange_text)
        if total_tokens + tokens > max_tokens:
            break
        
        context_parts.insert(0, exchange_text)
        total_tokens += tokens
    
    if context_parts:
        return "RECENT CONVERSATION CONTEXT:\n" + "\n".join(context_parts)
    return ""

def build_followup_prompt(followup_question, context, use_rag):
    """
    Build a well-structured follow-up prompt
    
    Args:
        followup_question: The user's follow-up question
        context: Previous conversation context
        use_rag: Whether RAG search is enabled
    
    Returns:
        Formatted prompt string
    """
    if use_rag:
        # For RAG: Focus on new search with context awareness
        prompt = f"""You are answering a follow-up question in an ongoing conversation about Cisco documentation.

{context}

CURRENT FOLLOW-UP QUESTION: {followup_question}

INSTRUCTIONS:
- You have context from previous exchanges above
- Search the documentation database for information relevant to this follow-up
- Reference previous answers if relevant (e.g., "As mentioned earlier...")
- If this question asks for clarification/expansion of a previous answer, identify what to expand
- Provide a direct, focused answer to the follow-up question
- Do not repeat information already provided unless specifically asked

Your answer:"""
    else:
        # For direct LLM: Pure conversational follow-up
        prompt = f"""You are continuing a conversation about Cisco documentation and bug analysis.

{context}

USER FOLLOW-UP: {followup_question}

INSTRUCTIONS:
- Answer based on the conversation context above and your general knowledge
- Reference previous exchanges when relevant
- If asking for clarification, expand on the specific point mentioned
- Keep answers concise and focused on what was asked
- Use natural conversational language

Your answer:"""
    
    return prompt

def save_test_results_to_excel(page_name, feature, tester_name, bug_number, output_content, location_accuracy, content_accuracy, comments, wishlist, usefulness="N/A"):
    """
    Save test results to Excel file
    
    Args:
        page_name: Name of the page/tab being tested
        feature: Feature being tested
        tester_name: Name of person performing the test
        bug_number: Bug number(s) entered by user
        output_content: Generated content from analysis
        location_accuracy: Slider value for location accuracy (1-10)
        content_accuracy: Slider value for content accuracy (1-10)
        comments: User comments
        wishlist: User wishlist/feature requests
        usefulness: Usefulness rating of the feature
    """
    excel_file = "testresults.xlsx"
    
    # Create data row with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {
        "Timestamp": timestamp,
        "Page Name": page_name,
        "Feature": feature,
        "Name of Tester": tester_name,
        "Bug Number": bug_number,
        "Output Content": output_content,
        "Location Accuracy": location_accuracy,
        "Content Accuracy": content_accuracy,
        "Comments": comments,
        "Wishlist": wishlist,
        "Usefulness": usefulness
    }
    
    # Check if file exists
    if os.path.exists(excel_file):
        # Load existing workbook and append
        try:
            df_existing = pd.read_excel(excel_file)
            df_new = pd.DataFrame([new_row])
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_excel(excel_file, index=False, engine='openpyxl')
        except Exception as e:
            # If there's any issue reading, create new file
            df = pd.DataFrame([new_row])
            df.to_excel(excel_file, index=False, engine='openpyxl')
    else:
        # Create new file with headers
        df = pd.DataFrame([new_row])
        df.to_excel(excel_file, index=False, engine='openpyxl')

# ==================== PAGE FUNCTIONS ====================

def render_analysis_summary_page():
    """Render the Analysis & Summary page with full functionality"""
    st.header("🔍 Analysis & Summary")
    
    # Add model recommendation note
    st.info("💡 **Recommended Models:** This page works best with **gpt-4.1** or **gpt-4o** for intelligent query parsing. Other models use a simpler search method but work reliably.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ===== FETCH BUG FROM CDETS SECTION =====
        st.markdown("<h3 style='color: #1f77b4;'>Step 1: Enter Bug Number. Click Fetch Bug</h3>", unsafe_allow_html=True)
        
        # Add checkbox for extracting all notes with better visibility
        st.markdown("**📋 Note Extraction Options**")
        extract_all_notes = st.checkbox(
            "**Extract all notes** (default: Behavior-changed + Release-note only)",
            value=False,
            help="Check this to extract all notes from the bug. By default, only 'Behavior-changed' and 'Release-note' notes are extracted along with the bug summary and Documentation-link field.",
            key="analysis_extract_all_notes"
        )
        
        bug_col1, bug_col2 = st.columns([3, 1])
        with bug_col1:
            bug_number_input = st.text_input(
                "Bug Number(s)",
                placeholder="e.g., CSCwp05354 or CSCwp05354, CSCwp12345, CSCwp67890",
                help="Enter one or more CDETS bug numbers (comma-separated) to fetch bug details",
                key="analysis_bug_number"
            )
        with bug_col2:
            st.write("")  # Spacer
            fetch_bug_button = st.button("🔍 Fetch Bug", use_container_width=True, key="analysis_fetch_bug")
        
        # Show success message after fetch
        if 'bug_fetched' in st.session_state and st.session_state.bug_fetched:
            st.success(f"✅ Successfully fetched bug data!")
            st.session_state.bug_fetched = False  # Clear the flag
        
        # Display notes summary right after fetch (most visible location)
        if 'fetched_notes_summary' in st.session_state and st.session_state.fetched_notes_summary:
            all_notes_summary = st.session_state.fetched_notes_summary
            total_notes = sum(len(notes) for notes in all_notes_summary.values())
            
            with st.expander(f"📋 Extracted Notes Summary ({total_notes} total notes)", expanded=True):
                for bug_num, notes in all_notes_summary.items():
                    if notes:
                        st.markdown(f"**Bug {bug_num}** ({len(notes)} notes):")
                        for idx, note_title in enumerate(notes, 1):
                            st.markdown(f"  {idx}. {note_title}")
                    else:
                        st.markdown(f"**Bug {bug_num}**: No notes extracted")
                    if bug_num != list(all_notes_summary.keys())[-1]:  # Not the last bug
                        st.markdown("---")
        
        # Handle fetch bug button
        if fetch_bug_button and bug_number_input:
            # Parse multiple bug numbers (comma-separated)
            bug_numbers = [bug.strip() for bug in bug_number_input.split(',') if bug.strip()]
            
            with st.spinner(f"Fetching {len(bug_numbers)} bug(s) from CDETS..."):
                try:
                    auth = create_auth()
                    ns = {'cdets': 'cdetsng', 'ns2': 'http://www.w3.org/1999/xlink'}
                    
                    # Combined content for all bugs
                    all_bugs_content = ""
                    all_notes_summary = {}  # Track notes per bug for display
                    
                    for bug_idx, bug_number in enumerate(bug_numbers, 1):
                        # Add separator between bugs
                        if bug_idx > 1:
                            all_bugs_content += "\n\n" + "="*80 + "\n\n"
                        
                        # Get bug summary
                        summary_response = get_bug_summary(bug_number, auth)
                        summary_root = safe_parse_cdets_xml(summary_response.content)
                        
                        # Build bug content
                        bug_content = f"# Bug {bug_number} - Complete Report\n\n"
                        bug_content += "## Bug Summary\n\n"
                        
                        # Extract bug fields
                        defect = summary_root.find('.//cdets:Defect', ns)
                        if defect:
                            for field in defect.findall('.//cdets:Field', ns):
                                field_name = field.get('name')
                                field_value = field.text if field.text else 'N/A'
                                
                                if field_name in ['Headline', 'Status', 'Severity', 'Priority', 'Product', 
                                                 'Component', 'Version', 'Description', 'FoundIn', 'FixedIn']:
                                    bug_content += f"**{field_name}:** {field_value}\n\n"
                        
                        # Extract Documentation-link field
                        try:
                            doc_link_values = get_bug_field_values(bug_number, 'Documentation-link', auth)
                            doc_link = doc_link_values.get('Documentation-link', 'N/A')
                            if doc_link and doc_link != 'N/A':
                                bug_content += f"**Documentation-link:** {doc_link}\n\n"
                        except Exception as e:
                            # If Documentation-link field doesn't exist or error, skip silently
                            pass
                        
                        # Get notes
                        bug_content += "\n## Notes\n\n"
                        
                        note_titles = []  # Collect note titles for this bug
                        
                        if extract_all_notes:
                            # Extract all notes
                            try:
                                all_note_titles = get_all_notes(bug_number, auth)
                                note_titles = all_note_titles
                                
                                for i, note_title in enumerate(all_note_titles, 1):
                                    try:
                                        note_response = get_note_content(bug_number, note_title, auth)
                                        bug_content += f"### {i}. {note_title}\n\n"
                                        bug_content += f"**Content:**\n{note_response.text}\n\n"
                                    except Exception as e:
                                        bug_content += f"*Error fetching note '{note_title}': {str(e)}*\n\n"
                            except Exception as e:
                                bug_content += f"*Error fetching notes list: {str(e)}*\n\n"
                        else:
                            # Extract Behavior-changed and Release-note by default
                            default_notes = ["Behavior-changed", "Release-note"]
                            note_titles = []
                            
                            for note_title in default_notes:
                                try:
                                    note_response = get_note_content(bug_number, note_title, auth)
                                    bug_content += f"### {note_title}\n\n"
                                    bug_content += f"**Content:**\n{note_response.text}\n\n"
                                    note_titles.append(note_title)
                                except Exception as e:
                                    # If note doesn't exist, skip silently
                                    bug_content += f"*Note '{note_title}' not found*\n\n"
                        
                        # Store note titles for this bug
                        all_notes_summary[bug_number] = note_titles
                        
                        # Append this bug's content to the combined content
                        all_bugs_content += bug_content
                    
                    # Store in session state
                    st.session_state.uploaded_file_content = all_bugs_content
                    st.session_state.fetched_notes_summary = all_notes_summary  # Store notes summary
                    st.session_state.bug_fetched = True  # Flag to show success message
                    # Set the text area value directly
                    st.session_state.analysis_rca_text_area = all_bugs_content
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error fetching bug(s): {str(e)}")
                    with st.expander("🐛 Error Details"):
                        st.exception(e)
        
        st.markdown("---")
        
        # Step 1: (OR) Paste SR RCA
        st.subheader("(OR)")
        st.markdown("<h3 style='color: #1f77b4;'>Step 1: Paste your SR RCA</h3>", unsafe_allow_html=True)
        
        # RCA content input
        rca_content = st.text_area(
            "Bug Report / RCA Content",
            height=300,
            placeholder="Paste your bug report, root cause analysis, or SR RCA here...",
            help="Use this field to paste your SR RCA or bug content",
            key="analysis_rca_text_area"
        )
        
        st.markdown("---")
        
        # Step 2: Detect Technology Terms
        st.markdown("<h3 style='color: #1f77b4;'>Step 2: Detect Technology Terms</h3>", unsafe_allow_html=True)
        
        # ===== EXTRACTED TECHNOLOGY TERMS (on-demand, cached in session_state) =====
        has_rca = bool(rca_content and rca_content.strip())
        
        if has_rca:
            rca_hash = hash(rca_content.strip())
            has_cached_results = (
                'cached_clues_data' in st.session_state
                and st.session_state.get('_last_rca_hash_for_terms') == rca_hash
            )
        else:
            rca_hash = None
            has_cached_results = False
        
        # Always show the button row
        col_detect, col_clear = st.columns([3, 1])
        with col_detect:
            btn_label = "🔄 Re-detect Terms" if has_cached_results else "🔍 Detect Technology Terms"
            detect_clicked = st.button(btn_label, key="detect_tech_terms", use_container_width=True,
                                       type="primary" if not has_cached_results else "secondary")
        with col_clear:
            if has_cached_results:
                if st.button("🗑️ Clear", key="clear_tech_terms", use_container_width=True, help="Clear cached detection results"):
                    for k in ['cached_clues_data', '_last_rca_hash_for_terms', 'tech_terms_multiselect',
                               'selected_tech_terms', 'selected_raw_tech_terms', '_guide_state_hash']:
                        st.session_state.pop(k, None)
                    import app_functions
                    app_functions._networking_terms_cache = None
                    st.rerun()
        
        if not has_rca:
            if detect_clicked:
                st.warning("⚠️ No bug/RCA content found. Fetch a bug or paste content above first.")
            st.session_state.selected_raw_tech_terms = None
        elif has_rca:
            # Run detection only when button is clicked
            if detect_clicked:
                with st.spinner("🔍 Detecting technologies… please wait"):
                    # Clear cached networking terms so any JSON edits are picked up
                    import app_functions
                    app_functions._networking_terms_cache = None
                    
                    clues_data = extract_doc_clues_data(rca_content)
                    st.session_state.cached_clues_data = clues_data
                    st.session_state._last_rca_hash_for_terms = rca_hash
                    # Reset selections for fresh results
                    for k in ['tech_terms_multiselect', 'selected_tech_terms', 'selected_raw_tech_terms', '_guide_state_hash']:
                        st.session_state.pop(k, None)
                    st.rerun()
            
            # Display cached results if available
            if has_cached_results:
                clues_data = st.session_state.cached_clues_data
                all_detected_terms = [term for _, term in clues_data.get('tech_terms', [])]
                url_clues = clues_data.get('url_clues', [])
                
                # Summary line
                if all_detected_terms:
                    term_preview = ", ".join(t.upper() for t in all_detected_terms[:8])
                    if len(all_detected_terms) > 8:
                        term_preview += f" … +{len(all_detected_terms) - 8} more"
                    st.success(f"✅ Detected **{len(all_detected_terms)}** technology term(s) and **{len(url_clues)}** documentation URL(s)")
                else:
                    st.warning("⚠️ No known networking terms detected. The search will use the full bug content as-is.")
                
                st.markdown("<h3 style='color: #1f77b4;'>🔧 Detected Technology Terms</h3>", unsafe_allow_html=True)
                st.caption("Auto-extracted from your bug/RCA content. Deselect irrelevant terms to focus the search.")
                
                # Show URL clues as info (not selectable — always used)
                if url_clues:
                    for clue in url_clues:
                        chapter_str = ', '.join(c.upper() for c in clue['chapter_clues']) if clue['chapter_clues'] else 'none'
                        st.info(f"📎 **Book:** {clue['book_pdf']}  ·  **Chapter clues:** {chapter_str}")
                
                # Show technology terms as multiselect
                if all_detected_terms:
                    display_terms = [term.upper() for _, term in clues_data.get('tech_terms', [])]
                    
                    if 'selected_tech_terms' not in st.session_state:
                        st.session_state.selected_tech_terms = display_terms.copy()
                    
                    selected_display = st.multiselect(
                        f"Technology terms ({len(all_detected_terms)} detected)",
                        options=display_terms,
                        default=st.session_state.selected_tech_terms,
                        key="tech_terms_multiselect",
                        help="Remove terms that aren't relevant to narrow the search"
                    )
                    st.session_state.selected_tech_terms = selected_display
                    
                    selected_raw_terms = [t.lower() for t in selected_display]
                    st.session_state.selected_raw_tech_terms = selected_raw_terms
                    
                    st.caption(f"✅ {len(selected_raw_terms)} of {len(all_detected_terms)} terms selected")
                else:
                    st.caption("You can add terms to `networking_terms.json` to improve detection.")
                    st.session_state.selected_raw_tech_terms = None
            elif not detect_clicked:
                st.caption("Click **Detect Technology Terms** to scan your bug/RCA content for networking keywords.")
                st.session_state.selected_raw_tech_terms = None
        
        st.markdown("---")
        
        # Step 3: Choose your docset
        st.markdown("<h3 style='color: #1f77b4;'>Step 3: Choose your docset</h3>", unsafe_allow_html=True)
        
        # ===== PRODUCT NAME SECTION =====
        product_options = ["Cisco SD-WAN", "Cisco 9800", "ASR 9000", "Cisco 8000", "cisco_generic"]
        saved_product = get_saved_product()
        
        # Find index of saved product, default to 1 if not found
        try:
            default_index = product_options.index(saved_product)
        except ValueError:
            default_index = 1
        
        product_name = st.selectbox(
            "Product Name",
            options=product_options,
            index=default_index,
            help="Select the Cisco product (selection is remembered)",
            key="analysis_product_name",
            on_change=lambda: save_product_preference(st.session_state.get("analysis_product_name"))
        )
        
        # ===== GUIDE SELECTION SECTION =====
        st.markdown("**📚 Select Guides**")
        st.caption("Limit the search scope to specific guides (optional)")
        
        # Get available guides for the selected product
        available_guides = get_available_guides(product_name)
        
        if available_guides:
            # Define priority guides for Cisco SD-WAN (curated subset)
            sdwan_priority_guides = [
                "systems-interfaces-book-xe-sdwan.pdf",
                "security-book-xe.pdf",
                "sdwan-xe-gs-book.pdf",
                "policies-book-xe.pdf",
                "appqoe-book-xe.pdf",
                "cloud-onramp-book-xe.pdf",
                "monitor-maintain-book.pdf",
                "compatibility-and-server-recommendations.pdf"
            ]
            
            # Initialize session state for selected guides if not exists
            # Default: NO guides checked — auto-match from terms will populate them
            if 'selected_guides' not in st.session_state:
                st.session_state.selected_guides = []
            
            # Reset guides when product changes
            if 'last_product' not in st.session_state or st.session_state.last_product != product_name:
                st.session_state.selected_guides = []
                st.session_state.last_product = product_name
                # Clear checkbox widget states
                for guide in available_guides:
                    key = f"guide_{guide}"
                    if key in st.session_state:
                        del st.session_state[key]
            
            # Guide action buttons row
            col_guide1, col_guide2, col_guide3 = st.columns(3)
            with col_guide1:
                if st.button("✅ Select All", use_container_width=True, key="select_all_guides"):
                    st.session_state.selected_guides = available_guides.copy()
                    for guide in available_guides:
                        key = f"guide_{guide}"
                        if key in st.session_state:
                            st.session_state[key] = True
                    st.rerun()
            with col_guide2:
                if st.button("❌ Deselect All", use_container_width=True, key="deselect_all_guides"):
                    st.session_state.selected_guides = []
                    for guide in available_guides:
                        key = f"guide_{guide}"
                        if key in st.session_state:
                            st.session_state[key] = False
                    st.rerun()
            with col_guide3:
                # "Check Priority Guides" button — only enabled for SD-WAN
                is_sdwan = product_name == "Cisco SD-WAN"
                if st.button(
                    "⭐ Check Priority Guides",
                    use_container_width=True,
                    key="check_priority_guides",
                    disabled=not is_sdwan,
                    help="Check the curated high-priority SD-WAN guides" if is_sdwan else "Only available for Cisco SD-WAN product"
                ):
                    priority_set = set(g for g in sdwan_priority_guides if g in available_guides)
                    # Additive: keep existing selections and add priority guides
                    current = set(st.session_state.get('selected_guides', []))
                    merged = current | priority_set
                    st.session_state.selected_guides = list(merged)
                    for guide in available_guides:
                        key = f"guide_{guide}"
                        st.session_state[key] = guide in merged
                    st.rerun()
            
            # Display guides as checkboxes in an expander
            with st.expander(f"📖 Available Guides ({len(available_guides)})", expanded=True):
                st.caption(f"Found {len(available_guides)} guide(s) for {product_name}")
                
                # Auto-match guides based on detected technology terms
                auto_matched_guides = set()
                auto_match_reasons = {}  # guide -> [matched terms]
                guide_scores = {}  # guide -> score (number of terms pointing to it)
                current_selected_terms = []
                
                if rca_content and rca_content.strip():
                    current_selected_terms = st.session_state.get('selected_raw_tech_terms', []) or []
                    if current_selected_terms:
                        matched, _ = match_terms_to_guides(current_selected_terms, product_name)
                        # Extract guide scores (stored under special key)
                        guide_scores = matched.pop('_guide_scores', {})
                        st.session_state['_guide_scores'] = guide_scores
                        # Store the term→guide mapping so run_agent can derive section hints
                        st.session_state['_matched_term_guides'] = dict(matched)
                        for term, matched_guide_list in matched.items():
                            if term.startswith('_'):
                                continue
                            for g in matched_guide_list:
                                auto_matched_guides.add(g)
                                if g not in auto_match_reasons:
                                    auto_match_reasons[g] = []
                                auto_match_reasons[g].append(term.upper())
                
                if auto_matched_guides:
                    # Sort by score and show top guides
                    top_guide = max(auto_matched_guides, key=lambda g: guide_scores.get(g, 0)) if guide_scores else None
                    top_msg = f"🎯 **{len(auto_matched_guides)}** guide(s) auto-selected"
                    if top_guide:
                        top_msg += f" — **#{1}: {top_guide}** (score={guide_scores.get(top_guide, 0)})"
                    st.info(top_msg)
                
                # Build a hash that changes when content/terms change, to reset checkbox defaults
                terms_sig = str(sorted(current_selected_terms)).encode() if current_selected_terms else b"none"
                guide_state_hash = hashlib.md5(
                    (rca_content or "").encode() + terms_sig + product_name.encode()
                ).hexdigest()[:8]
                
                # Reset checkbox states when content, terms, or product changes
                prev_guide_hash = st.session_state.get('_guide_state_hash', '')
                if prev_guide_hash != guide_state_hash:
                    for guide in available_guides:
                        key = f"guide_{guide}"
                        if key in st.session_state:
                            del st.session_state[key]
                    st.session_state['_guide_state_hash'] = guide_state_hash
                    
                    # Start with ONLY auto-matched guides checked (empty if no matches)
                    st.session_state.selected_guides = list(auto_matched_guides)
                
                # Create checkboxes for each guide, sorted by score (highest first)
                # Matched guides come first (sorted by score), then unmatched
                sorted_guides = sorted(
                    available_guides,
                    key=lambda g: guide_scores.get(g, 0),
                    reverse=True
                )
                for guide in sorted_guides:
                    checkbox_key = f"guide_{guide}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = guide in st.session_state.get('selected_guides', available_guides)
                    
                    # Build label with match indicator and score
                    score = guide_scores.get(guide, 0)
                    if guide in auto_match_reasons:
                        match_tags = ", ".join(auto_match_reasons[guide])
                        rank_marker = f"🥇" if score == max(guide_scores.values(), default=0) and score > 0 else "⭐"
                        label = f"{guide}  {rank_marker} score={score} ({match_tags})"
                    else:
                        label = guide
                    
                    st.checkbox(label, key=checkbox_key)
                
                # Collect selected guides from checkboxes
                selected_guides = [guide for guide in available_guides if st.session_state.get(f"guide_{guide}", False)]
                st.session_state.selected_guides = selected_guides
                
                # Show selection summary
                if selected_guides:
                    st.success(f"✅ {len(selected_guides)} guide(s) selected")
                else:
                    st.info("ℹ️ No guides selected - will search all guides")
        else:
            st.warning(f"⚠️ No guides found for {product_name}")
        
        # Load default prompt from BugAnalyze.md (always read fresh from disk)
        try:
            with open("BugAnalyze.md", "r") as f:
                default_prompt = f.read()
        except FileNotFoundError:
            default_prompt = "Analyze the Bug/RCA content"
        
        # Keep session state in sync with the file on disk
        # so edits to BugAnalyze.md are reflected without clearing session
        if 'analysis_question' not in st.session_state or st.session_state.get('_last_prompt_hash') != hash(default_prompt):
            st.session_state['analysis_question'] = default_prompt
            st.session_state['_last_prompt_hash'] = hash(default_prompt)
        
        st.markdown("---")
        
        # Question input for Analysis
        question = st.text_area(
            "Task/Prompt",
            key="analysis_question",
            height=200
        )
        
        st.markdown("---")
    
    with col2:
        # Step 4: Click Analyze or Summarize
        st.markdown("<h3 style='color: #1f77b4;'>Step 4: Click Analyze or Summarize</h3>", unsafe_allow_html=True)
        
        st.markdown("**🔍 Analysis & Summary Tools**")
        
        # Analysis and Summary buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True, key="analysis_analyze")

        with col_btn2:
            summarize_button = st.button("📝 Summarize", use_container_width=True, key="analysis_summarize")

        with col_btn3:
            clear_button = st.button("🗑️ Clear", use_container_width=True, key="analysis_clear")
        
        # Status message placeholder (appears below buttons)
        status_placeholder = st.empty()
        
        st.markdown("---")
        
        st.markdown("**📊 Output**")
        
        output_container = st.container()
        
        # Display conversation: latest follow-up first so the user sees the newest answer without scrolling
        if st.session_state.conversation_history:
            with output_container:
                followups = st.session_state.conversation_history[1:]
                if followups:
                    # Show the most recent follow-up at the top
                    latest = followups[-1]
                    latest_num = len(followups)
                    q_preview = latest['question'][:200] + "..." if len(latest['question']) > 200 else latest['question']
                    st.markdown(f"**💬 Follow-up {latest_num} _(latest)_:** {q_preview}")
                    st.markdown(latest['answer'])

                    # Show older follow-ups in reverse order (newest → oldest) inside a collapsible
                    if len(followups) > 1:
                        with st.expander(f"📜 Earlier follow-ups ({len(followups) - 1})", expanded=False):
                            for i in range(len(followups) - 2, -1, -1):
                                exchange = followups[i]
                                q_prev = exchange['question'][:200] + "..." if len(exchange['question']) > 200 else exchange['question']
                                st.markdown(f"**💬 Follow-up {i + 1}:** {q_prev}")
                                st.markdown(exchange['answer'])
                                if i > 0:
                                    st.markdown("---")

                    # Initial analysis tucked into a collapsible below
                    with st.expander("📋 Initial Analysis", expanded=False):
                        st.markdown(st.session_state.conversation_history[0]['answer'])
                else:
                    # No follow-ups yet — show the initial analysis directly
                    st.markdown(st.session_state.conversation_history[0]['answer'])
        
        # Test Section
        st.markdown("---")
        st.markdown("<h3 style='color: #1f77b4;'>Step 5: Post your test results (Optional)</h3>", unsafe_allow_html=True)
        
        with st.expander("📝 Test Results", expanded=False):
            st.markdown("Capture test results for this analysis")
            
            # Feature being tested
            test_feature = st.text_input(
                "Feature to be tested",
                placeholder="e.g., bug analysis, bug summarize, bulk RCA, bulk bugs, First draft, resolve bug",
                help="Enter the specific feature or functionality being tested",
                key="test_feature"
            )
            
            # Name of tester
            saved_tester_name = get_saved_tester_name()
            tester_name = st.text_input(
                "Name of tester",
                value=saved_tester_name,
                placeholder="Enter your name",
                help="Name of the person performing the test (saved for future sessions)",
                key="tester_name",
                on_change=lambda: save_tester_name(st.session_state.get("tester_name", ""))
            )
            
            # Sliders for accuracy ratings
            location_accuracy = st.slider(
                "Location Accuracy",
                min_value=1,
                max_value=10,
                value=10,
                help="Rate the accuracy of the location/chapter recommendations (1=Poor, 10=Excellent)",
                key="test_location_accuracy"
            )
            
            content_accuracy = st.slider(
                "Content Accuracy",
                min_value=1,
                max_value=10,
                value=10,
                help="Rate the accuracy of the content generated (1=Poor, 10=Excellent)",
                key="test_content_accuracy"
            )
            
            # Comments text area
            test_comments = st.text_area(
                "Comments",
                placeholder="Enter any additional comments or observations...",
                height=100,
                key="test_comments"
            )
            
            # Wishlist text area
            test_wishlist = st.text_area(
                "Wishlist",
                placeholder="Enter feature requests, improvements, or wishlist items...",
                height=100,
                key="test_wishlist"
            )
            
            # Usefulness Rating
            st.markdown("---")
            test_usefulness = st.radio(
                "How useful is this feature?",
                options=[
                    "⛔ I'd rather do this without AI",
                    "🤔 Neutral - No strong preference",
                    "👍 Yes, this is useful",
                    "⭐ I'd prefer CIRCUIT over manual work"
                ],
                index=2,
                help="Rate how useful you find this AI-assisted feature",
                key="test_usefulness_rating"
            )
            
            # Add to Excel button
            add_to_excel_button = st.button(
                "📊 Add to Test Excel",
                type="primary",
                use_container_width=True,
                key="add_to_test_excel"
            )
            
            if add_to_excel_button:
                # Get bug number
                bug_number = st.session_state.get('analysis_bug_number', '')
                if not bug_number:
                    st.error("⚠️ Please enter a bug number first.")
                elif not st.session_state.conversation_history:
                    st.error("⚠️ No output found. Please run an analysis first.")
                else:
                    # Get the output content (last answer from conversation history)
                    output_content = st.session_state.conversation_history[-1]['answer']
                    
                    # Save to Excel
                    try:
                        save_test_results_to_excel(
                            page_name="Analysis & Summary",
                            feature=test_feature,
                            tester_name=tester_name,
                            bug_number=bug_number,
                            output_content=output_content,
                            location_accuracy=location_accuracy,
                            content_accuracy=content_accuracy,
                            comments=test_comments,
                            wishlist=test_wishlist,
                            usefulness=test_usefulness
                        )
                        st.success("✅ Test results saved to testresults.xlsx!")
                        
                        # Provide download link
                        try:
                            with open("testresults.xlsx", "rb") as file:
                                st.download_button(
                                    label="📥 Download testresults.xlsx",
                                    data=file,
                                    file_name="testresults.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        except:
                            pass
                    except Exception as e:
                        st.error(f"❌ Error saving to Excel: {str(e)}")
                        with st.expander("🐛 Error Details"):
                            st.exception(e)
        
        st.markdown("---")
        
        # Step 6: Post Analysis to CDETS
        st.markdown("<h3 style='color: #1f77b4;'>Step 6: Post Analysis to CDETS</h3>", unsafe_allow_html=True)
        
        # Add "Post Analysis to Bug" button above output
        post_analysis_button = st.button("📤 Post Analysis to Bug", type="secondary", use_container_width=True, key="analysis_post_to_bug")
        
        # ===== FOLLOW-UP SECTION - Placed after output display =====
        if st.session_state.initial_analysis_done and st.session_state.conversation_history:
            st.markdown("---")
            st.markdown("### 💬 Conversation Thread")
            st.caption("View your questions and answers, then ask follow-ups below")
            
            # Show recent follow-up questions in reverse order (newest first)
            if len(st.session_state.conversation_history) > 1:
                with st.container():
                    st.markdown("**Recent follow-ups:**")
                    followups = st.session_state.conversation_history[1:]
                    recent = followups[-3:]
                    for j in range(len(recent) - 1, -1, -1):
                        num = len(followups) - (len(recent) - 1 - j)
                        q_preview = recent[j]['question'][:150] + "..." if len(recent[j]['question']) > 150 else recent[j]['question']
                        tag = " _(latest)_" if j == len(recent) - 1 else ""
                        st.markdown(f"💬 **{num}.{tag}** {q_preview}")
            
            # Full conversation history
            with st.expander("📜 Full Conversation History", expanded=False):
                for idx, exchange in enumerate(st.session_state.conversation_history, 1):
                    label = "Initial Analysis" if idx == 1 else f"Follow-up {idx - 1}"
                    q_preview = exchange['question'][:80] + "..." if len(exchange['question']) > 80 else exchange['question']
                    with st.expander(f"{label}: {q_preview}", expanded=False):
                        st.markdown(f"**Question:**")
                        st.markdown(exchange['question'])
                        st.markdown(f"**Answer:**")
                        st.markdown(exchange['answer'])
            
            # Follow-up question input - more prominent
            followup_question = st.text_area(
                "Your follow-up question",
                placeholder="e.g., Can you explain the first point in more detail? Can you provide more examples?",
                height=100,
                key="analysis_followup_input"
            )
            
            ask_followup_button = st.button(
                "💬 Ask Follow-up", 
                type="primary", 
                use_container_width=True, 
                key="analysis_ask_followup"
            )
            
            # Handle follow-up button
            if ask_followup_button and followup_question.strip():
                with st.spinner("💭 Thinking..."):
                    try:
                        # Build conversation history for the LLM
                        # (Direct LLM call — NOT run_agent, which would re-run the
                        #  full BugAnalyze pipeline with boost queries, wrong for follow-ups)
                        conversation_context = ""
                        for i, ex in enumerate(st.session_state.conversation_history):
                            if i == 0:
                                # First exchange is the initial analysis — include answer only
                                # (the question is the full BugAnalyze prompt, too long and irrelevant)
                                conversation_context += f"Initial Analysis Result:\n{ex['answer']}\n\n"
                            else:
                                conversation_context += f"Follow-up Q{i}: {ex['question']}\nFollow-up A{i}: {ex['answer']}\n\n"
                        
                        followup_prompt = f"""You are a Cisco documentation assistant continuing a conversation about bug analysis.

Previous conversation:
{conversation_context}
User's follow-up question: {followup_question}

Instructions:
- Answer based on the conversation above and your general knowledge
- If referencing a previous answer, be specific about which point
- If the user asks for clarification, expand on the specific point mentioned
- Keep the answer focused and concise
- Do not repeat the entire analysis unless specifically asked
"""
                        
                        # Direct LLM call for fast, focused follow-ups
                        _model = st.session_state.get('selected_model', 'gpt-4o')
                        llm = get_llm(model_name=_model)
                        llm_result = llm.invoke(followup_prompt)
                        answer = llm_result.content if hasattr(llm_result, 'content') else str(llm_result)
                        
                        # Add to conversation history
                        st.session_state.conversation_history.append({
                            "question": followup_question,
                            "answer": answer
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing follow-up: {str(e)}")
                        with st.expander("🐛 Error Details"):
                            st.exception(e)
    
    # ===== HANDLE BUTTON CLICKS =====
    
    # Handle Analyze button
    if analyze_button:
        if not rca_content.strip():
            status_placeholder.error("⚠️ Please provide RCA content to analyze.")
        elif not product_name.strip():
            status_placeholder.error("⚠️ Please provide a product name.")
        elif not question.strip():
            status_placeholder.error("⚠️ Please provide a question or task description.")
        else:
            with status_placeholder:
                with st.spinner("🔍 Analyzing documentation and generating recommendations..."):
                    try:
                        # Store in session state
                        st.session_state.product_name = product_name
                        st.session_state.current_rca_content = rca_content
                        st.session_state.initial_analysis_done = True
                        
                        # Get selected guides LIVE from checkbox widget states
                        # (not from st.session_state.selected_guides which may be stale
                        #  if the user toggled a checkbox and clicked Analyze in the same interaction)
                        live_guides = get_available_guides(product_name)
                        selected_guides = [g for g in live_guides if st.session_state.get(f"guide_{g}", False)]
                        st.session_state.selected_guides = selected_guides  # sync back
                        
                        # Get user-selected technology terms (None = use all)
                        selected_tech_terms = st.session_state.get('selected_raw_tech_terms', None)
                        
                        # Use the question from the text area (user may have edited it)
                        # The text area is already synced with BugAnalyze.md on startup/file changes
                        # but user edits in the UI take precedence at execution time
                        result = run_agent(product_name, question, rca_content, selected_guides, selected_tech_terms)
                        
                        # Add to conversation history
                        st.session_state.conversation_history.append({
                            "question": question,
                            "answer": result['output'] if 'output' in result else str(result)
                        })
                        
                        st.success("✅ Analysis complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        with st.expander("🐛 Error Details"):
                            st.exception(e)
    
    # Handle Post Analysis to Bug button
    if post_analysis_button:
        # Get the first bug number from the input
        bug_number_input = st.session_state.get('analysis_bug_number', '')
        
        if not bug_number_input:
            st.error("⚠️ Please enter a bug number first.")
        else:
            # Get the first bug number (in case multiple were entered)
            first_bug = bug_number_input.split(',')[0].strip()
            
            # Get the output content from conversation history
            if not st.session_state.conversation_history:
                st.error("⚠️ No analysis output found. Please run an analysis first.")
            else:
                # Get the last answer as the note body
                last_answer = st.session_state.conversation_history[-1]['answer']
                
                with st.spinner(f"📤 Posting analysis to bug {first_bug}..."):
                    try:
                        auth = create_auth()
                        response = create_note(
                            bug_number=first_bug,
                            note_title="AI-Analysis",
                            note_content=last_answer,
                            note_type="Other",
                            auth=auth
                        )
                        st.success(f"✅ Successfully posted analysis to bug {first_bug}!")
                        st.info(f"Response status: {response.status_code}")
                        
                        # Display bug link
                        bug_url = f"https://cdetsng.cisco.com/webui/#view={first_bug}"
                        st.markdown(f"🔗 **View Bug:** [{first_bug}]({bug_url})")
                        
                    except Exception as e:
                        st.error(f"❌ Error posting analysis to bug: {str(e)}")
                        with st.expander("🐛 Error Details"):
                            st.exception(e)
    
    # Handle Summarize button
    if summarize_button:
        if not rca_content.strip():
            st.error("⚠️ Please provide RCA content to summarize.")
        else:
            with st.spinner("📝 Generating summary..."):
                try:
                    # Store in session state
                    st.session_state.product_name = product_name
                    st.session_state.current_rca_content = rca_content
                    st.session_state.initial_analysis_done = True
                    
                    # Use the apply_prompt_file function with summarize.md
                    summary = apply_prompt_file("summarize.md", rca_content, product_name)
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        "question": "Summarize the bug/RCA content",
                        "answer": summary
                    })
                    
                    # Clear follow-up answer when new analysis is done
                    if 'last_followup_answer' in st.session_state:
                        del st.session_state.last_followup_answer
                    if 'last_followup_raw' in st.session_state:
                        del st.session_state.last_followup_raw
                    
                    st.success("✅ Summary generated!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generating summary: {str(e)}")
                    with st.expander("🐛 Error Details"):
                        st.exception(e)
    
    # Handle Clear button
    if clear_button:
        st.session_state.conversation_history = []
        st.session_state.initial_analysis_done = False
        st.session_state.current_rca_content = ""
        st.session_state.uploaded_file_content = ""
        # Clear follow-up answer display
        if 'last_followup_answer' in st.session_state:
            del st.session_state.last_followup_answer
        if 'last_followup_raw' in st.session_state:
            del st.session_state.last_followup_raw
        # Clear text area widgets by deleting their session state keys
        if 'analysis_rca_text_area' in st.session_state:
            del st.session_state.analysis_rca_text_area
        st.rerun()
    
def render_placeholder_page(title, icon):
    """Render a placeholder page for features not yet implemented"""
    st.header(f"{icon} {title}")
    st.markdown("---")
    st.info(f"🚧 The {title} page is coming soon! This will be implemented next.")

def render_settings_page():
    """Render the Settings page"""
    st.header("⚙️ Settings")
    st.markdown("---")
    
    st.markdown("### 👤 User Preferences")
    
    # Tester Name Setting
    st.markdown("#### Test Results Configuration")
    saved_tester_name = get_saved_tester_name()
    
    tester_name_input = st.text_input(
        "Default Tester Name",
        value=saved_tester_name,
        placeholder="Enter your name",
        help="This name will be used by default when submitting test results",
        key="settings_tester_name"
    )
    
    if st.button("💾 Save Tester Name", type="primary"):
        save_tester_name(tester_name_input)
        st.success(f"✅ Tester name saved: {tester_name_input}")
    
    st.markdown("---")
    
    # Product Preference Setting
    st.markdown("#### Default Product Selection")
    saved_product = get_saved_product()
    
    product_options = ["Cisco SD-WAN", "Cisco 9800", "ASR 9000", "Cisco 8000", "cisco_generic"]
    try:
        default_index = product_options.index(saved_product)
    except ValueError:
        default_index = 1
    
    product_selection = st.selectbox(
        "Default Product",
        options=product_options,
        index=default_index,
        help="This product will be selected by default on the Analysis & Summary page",
        key="settings_product"
    )
    
    if st.button("💾 Save Product Preference", type="primary"):
        save_product_preference(product_selection)
        st.success(f"✅ Default product saved: {product_selection}")
    
    st.markdown("---")
    
    # Configuration File Info
    st.markdown("### 📁 Configuration")
    st.caption(f"Settings are saved to: `{CONFIG_FILE}`")
    
    if st.button("🔍 View Current Configuration"):
        config = load_config()
        st.json(config)

# ==================== MAIN APP ====================

def main():
    """Main application logic with sidebar navigation"""
    
    # Initialize session state variables
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'initial_analysis_done' not in st.session_state:
        st.session_state.initial_analysis_done = False
    if 'context_window_size' not in st.session_state:
        st.session_state.context_window_size = 3  # Default: last 3 exchanges
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = 'gpt-4o'  # Default to gpt-4o
    
    # Initialize vector store in session state (only once)
    if 'vector_store_initialized' not in st.session_state:
        try:
            from vector_store_manager import initialize_vector_store, get_persistence_mode
            with st.spinner("🔄 Loading knowledge base..."):
                st.session_state.vector_store = initialize_vector_store()
                st.session_state.vector_store_initialized = True
                
                # Show info about persistence mode
                persistence_mode = get_persistence_mode()
                if persistence_mode == 'in-memory':
                    st.info("ℹ️ Running in-memory mode due to SQLite version. Data will not persist between restarts.")
        except Exception as e:
            st.error(f"❌ Error loading knowledge base: {e}")
            st.info("💡 Make sure knowledge_docs/ directory exists and contains files")
            st.session_state.vector_store_initialized = False
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🩺 Bug Doctor")
        st.markdown("*AI-Powered fixes for your bugs and RCA*")
        
        # Add a random funny quote about bug fixing and documentation
        import random
        quotes = [
            "💡 *\"The best documentation is the code itself... said no one ever.\"*",
            "🐛 *\"It's not a bug, it's an undocumented feature!\"*",
            "📝 *\"Writing documentation: Because future you will have no idea what past you was thinking.\"*",
            "🔧 *\"99 little bugs in the code, 99 bugs to fix... Take one down, patch it around, 127 bugs in the code.\"*",
            "📚 *\"Good documentation is like a love letter to your future self.\"*",
            "🎯 *\"Documentation: The fine art of explaining what you should have written clearly the first time.\"*",
            "⚡ *\"First we code, then we document, then we explain why we documented.\"*",
            "🚀 *\"If debugging is the process of removing bugs, then programming must be the process of putting them in.\"*",
            "📖 *\"Documentation is a love story between your code and everyone else.\"*",
            "🎨 *\"Writing docs: Where creativity meets procrastination.\"*",
            "🧩 *\"The code works perfectly... until someone reads the documentation.\"*",
            "🌟 *\"Behind every great feature is an even greater README.\"*",
            "🤖 *\"AI won't replace writers. It'll just become their extremely enthusiastic intern.\"*",
            "✍️ *\"Writers: AI can write docs, but can it understand the joy of perfectly placed semicolons?\"*",
            "🧠 *\"Fear not the AI, dear writer. It still can't make coffee or attend meetings for you.\"*",
            "📱 *\"AI writes fast, but writers write with soul. And occasional typos.\"*",
            "🌈 *\"Will AI replace writers? Only if robots start appreciating their own jokes.\"*",
            "🎪 *\"AI is the co-pilot, writers are still the captain. Mostly because AI can't argue with editors.\"*",
            "💼 *\"Writers + AI = Dream team. Writers - coffee = Different story.\"*",
            "🎬 *\"AI can generate text, but can it panic at 3 AM before a deadline? Didn't think so.\"*",
            "🏆 *\"AI: Your writing assistant that never judges your comma usage. Unlike humans.\"*",
            "😄 *\"AI tells bad jokes. Writers know which bad jokes to keep.\"*",
            "🎤 *\"AI makes puns. Writers think we know when to stop.\"*",
            "🎯 *\"AI can write a joke. Only writers can write the apology for it.\"*",
        ]
        st.caption(random.choice(quotes))
        
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigation",
            [
                "🔍 Analysis & Summary",
                "✍️ First Draft",
                "📊 Bulk Analysis",
                "🔧 Resolve Bug",
                "🎯 Hallucination Check",
                "⚙️ Settings"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Additional sidebar content
        with st.expander("ℹ️ About Bug Doctor"):
            st.caption("**Product:** Cisco Documentation Assistant")
            st.caption("**AI Engine:** GPT-4 + RAG")
            st.caption("**Version:** 2.0.0")
            st.caption("**Updated:** February 2026")
        
        # Features overview
        with st.expander("🎯 Key Features"):
            st.caption("""
            ✓ Analyze bugs & RCAs
            ✓ Generate documentation drafts
            ✓ Bulk processing (Excel)
            ✓ Bug resolution workflow
            ✓ Hallucination detection
            """)
        
        st.markdown("---")
        
        # Model selector - All available models
        st.markdown("### 🤖 Model Selection")
        
        all_models = [
            "gpt-4.1",
            "gpt-4o",
            "gpt-5",
            "gpt-5-2", 
            "gpt-5-chat",
            "gpt-5-mini",
            "gpt-4o-mini",
            "gpt-5-nano",
            "claude-sonnet-4",
            "gemini-2.5-pro",
            "gemini-2.5-flash"
        ]
        
        model_descriptions = {
            "gpt-4.1": "GPT-4.1 (Reliable, Full Features) ✅",
            "gpt-4o": "GPT-4o (Balanced, Full Features) ✅",
            "gpt-5": "GPT-5 (Latest) ⚠️",
            "gpt-5-2": "GPT-5-2 (Newest) ⚠️",
            "gpt-5-chat": "GPT-5 Chat ⚠️",
            "gpt-5-mini": "GPT-5 Mini (Fast) ⚠️",
            "gpt-4o-mini": "GPT-4o Mini (Very Fast) ⚠️",
            "gpt-5-nano": "GPT-5 Nano (Cheapest) ⚠️",
            "claude-sonnet-4": "Claude Sonnet 4 (Anthropic) ⚠️",
            "gemini-2.5-pro": "Gemini 2.5 Pro (Google) ⚠️",
            "gemini-2.5-flash": "Gemini 2.5 Flash (Google) ⚠️"
        }
        
        selected_model = st.selectbox(
            "Choose Model",
            options=all_models,
            format_func=lambda x: model_descriptions.get(x, x),
            index=all_models.index(st.session_state.selected_model) if st.session_state.selected_model in all_models else 0,
            key="model_selector",
            help="✅ = Full smart search support\n⚠️ = Uses fallback search (works but less intelligent query parsing)"
        )
        
        st.session_state.selected_model = selected_model
        
        # Show info about the selected model's capabilities
        if selected_model in ['gpt-4.1', 'gpt-4o']:
            st.caption("✅ Smart query parsing enabled")
        else:
            st.caption("⚠️ Using fallback search mode")
        
        st.markdown("---")
        st.caption("💡 Powered by Azure OpenAI")
    
    # Route to the selected page
    if page == "🔍 Analysis & Summary":
        render_analysis_summary_page()
    elif page == "✍️ First Draft":
        render_first_draft_page()
    elif page == "📊 Bulk Analysis":
        render_bulk_analysis_page()
    elif page == "🔧 Resolve Bug":
        render_resolve_bug_page()
    elif page == "🎯 Hallucination Check":
        render_hallucination_check_page()
    elif page == "⚙️ Settings":
        render_settings_page()

if __name__ == "__main__":
    main()
