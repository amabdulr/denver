"""
Streamlit App - Cisco Documentation Assistant (Sidebar Navigation)
Main application file with sidebar-based navigation
Analysis & Summary - Full Implementation
"""

import streamlit as st
from dotenv import load_dotenv
from bug2 import create_auth, get_bug_summary, get_file_content, get_note_content, get_all_notes, create_note, get_bug_field_values
import xml.etree.ElementTree as ET
import requests
import json
import os
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook, Workbook

# Import helper functions
from app_functions import run_agent, format_output, apply_prompt_file
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
    st.markdown("---")
    
    # Step-by-step instructions
    with st.expander("📖 How to Use This Page", expanded=False):
        st.markdown("""
        #### Fetch Bug from CDETS  
        1. **Select Note Extraction**: Check the box to extract all notes, or leave unchecked for default (Behavior-changed + Release-note)
        2. **Enter Bug Number(s)**: Type bug numbers (If you have a related bug, enter with comma separation CSCwp05354, CSCwp12345)
        3. **Choose Product Name**: Select the Cisco product (e.g., Cisco 9800)            
        3. **Fetch Bug**: Click "🔍 Fetch Bug(s)"
        The notes from CDETS are populated in the Bug Report / RCA Content field. 
        
        #### Input RCA content.
        1.. **Paste Content**: Enter Root Cause Analysis (RCA) of a doc SR from Case Insights. 

        #### Bottom Section: Analysis & Summary Tools
        2. **Choose Analysis Tool**: Click one of the available analysis buttons:
           - **Summarize**: Condense bug content into a concise summary
           - **BugAnalyze**: Determine where the bug should be documented
        3. **Review Results**: Analysis results appear on the output area on the righ.
        4. **Ask Follow-ups** (optional): Use the "Ask a follow-up question" field to get clarifications
        5. **Clear button**: Clears conversation history and input fields for a fresh start
        
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ===== FETCH BUG FROM CDETS SECTION =====
        st.subheader("🐛 Fetch Bug from CDETS")
        
        # Add checkbox for extracting all notes
        extract_all_notes = st.checkbox(
            "📋 Extract all notes (default: Behavior-changed + Release-note)",
            value=False,
            help="Check this to extract all notes from the bug. By default, only 'Behavior-changed' and 'Release-note' notes are extracted along with the bug summary.",
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
            fetch_bug_button = st.button("🔍 Fetch Bug(s)", use_container_width=True, key="analysis_fetch_bug")
        
        # Show success message after fetch
        if 'bug_fetched' in st.session_state and st.session_state.bug_fetched:
            st.success(f"✅ Successfully fetched bug data!")
            st.session_state.bug_fetched = False  # Clear the flag
        
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
                        summary_root = ET.fromstring(summary_response.content)
                        
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
        
        # Load default prompt from BugAnalyze.md
        try:
            with open("BugAnalyze.md", "r") as f:
                default_prompt = f.read()
        except FileNotFoundError:
            default_prompt = "Analyze the Bug/RCA content"
        
        # Question input for Analysis
        question = st.text_area(
            "Question/Task",
            value=default_prompt,
            key="analysis_question",
            height=200
        )
        
        st.markdown("---")
        
        # Display notes summary if available (persistent display after fetch)
        if 'fetched_notes_summary' in st.session_state and st.session_state.fetched_notes_summary:
            all_notes_summary = st.session_state.fetched_notes_summary
            total_notes = sum(len(notes) for notes in all_notes_summary.values())
            
            with st.expander(f"📋 Extracted Notes Summary ({total_notes} total notes)", expanded=False):
                for bug_num, notes in all_notes_summary.items():
                    st.markdown(f"**Bug {bug_num}** ({len(notes)} notes):")
                    for idx, note_title in enumerate(notes, 1):
                        st.markdown(f"  {idx}. {note_title}")
                    if bug_num != list(all_notes_summary.keys())[-1]:  # Not the last bug
                        st.markdown("---")
        
        # RCA content input
        rca_content = st.text_area(
            "Bug Report / RCA Content",
            height=300,
            placeholder="Paste your bug report, root cause analysis, or case notes here...",
            help="Paste the content of your RCA",
            key="analysis_rca_text_area"
        )
    
    with col2:
        st.subheader("📊 Output")
        
        # Add "Post Analysis to Bug" button above output
        post_analysis_button = st.button("📤 Post Analysis to Bug", type="secondary", use_container_width=True, key="analysis_post_to_bug")
        
        output_container = st.container()
        
        # Display the last analysis output if available
        if st.session_state.conversation_history:
            with output_container:
                # Display the most recent answer
                last_exchange = st.session_state.conversation_history[-1]
                st.markdown(last_exchange['answer'])
        
        # Display follow-up answer if available
        if 'last_followup_answer' in st.session_state and st.session_state.last_followup_answer:
            with output_container:
                st.markdown("---")
                st.markdown("## 💬 Follow-up Answer")
                st.markdown(st.session_state.last_followup_answer)
                
                # Show raw output in expander
                if 'last_followup_raw' in st.session_state:
                    with st.expander("🔍 View Raw Response"):
                        st.json(st.session_state.last_followup_raw)
        
        # ===== FOLLOW-UP SECTION - Placed after output display =====
        if st.session_state.initial_analysis_done and st.session_state.conversation_history:
            st.markdown("---")
            st.markdown("### 💬 Have a question about the output above?")
            st.caption("Ask follow-up questions to clarify, expand, or get more details")
            
            # Compact settings
            with st.expander("⚙️ Follow-up Settings", expanded=False):
                context_window = st.slider(
                    "Context Window (number of recent exchanges to include)",
                    min_value=1,
                    max_value=10,
                    value=st.session_state.context_window_size,
                    help="Controls how many recent Q&A exchanges are included in follow-up context. Lower = faster, higher = more context.",
                    key="analysis_context_window"
                )
                st.session_state.context_window_size = context_window
                
                use_rag_followup = st.checkbox(
                    "🔍 Use RAG Search for Follow-ups",
                    value=True,
                    help="When enabled, follow-up questions will search the documentation database. When disabled, uses only conversation context.",
                    key="analysis_use_rag"
                )
                
                # Display conversation history
                st.markdown("**📜 Conversation History**")
                for idx, exchange in enumerate(st.session_state.conversation_history, 1):
                    with st.expander(f"Exchange {idx}: {exchange['question'][:80]}...", expanded=False):
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
            
            col_followup1, col_followup2 = st.columns([3, 1])
            with col_followup1:
                ask_followup_button = st.button(
                    "💬 Ask Follow-up", 
                    type="primary", 
                    use_container_width=True, 
                    key="analysis_ask_followup"
                )
            with col_followup2:
                if st.button("📜 History", use_container_width=True, key="toggle_history_analysis"):
                    st.session_state.show_history_analysis = not st.session_state.get('show_history_analysis', False)
            
            # Handle follow-up button
            if ask_followup_button and followup_question.strip():
                with st.spinner("💭 Thinking..."):
                    try:
                        # Get conversation context
                        context = get_relevant_context(
                            st.session_state.conversation_history,
                            window_size=context_window
                        )
                        
                        # Build the follow-up prompt
                        full_prompt = build_followup_prompt(
                            followup_question,
                            context,
                            use_rag_followup
                        )
                        
                        # Get product name and RCA content from session state
                        product_name_state = st.session_state.get('product_name', product_name)
                        rca_content_state = st.session_state.get('current_rca_content', rca_content)
                        
                        # Run the agent with the follow-up prompt
                        if use_rag_followup:
                            result = run_agent(product_name_state, full_prompt, rca_content_state)
                        else:
                            # For non-RAG, just use the LLM directly
                            from openai import OpenAI
                            client = OpenAI()
                            response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "You are a helpful Cisco documentation assistant."},
                                    {"role": "user", "content": full_prompt}
                                ]
                            )
                            result = {
                                'output': response.choices[0].message.content,
                                'raw': response
                            }
                        
                        # Extract answer
                        answer = result.get('output', str(result))
                        
                        # Add to conversation history
                        st.session_state.conversation_history.append({
                            "question": followup_question,
                            "answer": answer
                        })
                        
                        # Store for display
                        st.session_state.last_followup_answer = answer
                        st.session_state.last_followup_raw = result
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing follow-up: {str(e)}")
                        with st.expander("🐛 Error Details"):
                            st.exception(e)
    
    # Test Section
    st.markdown("---")
    st.subheader("🧪 Capture your test results!")
    
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
        tester_name = st.text_input(
            "Name of tester",
            placeholder="Enter your name",
            help="Name of the person performing the test",
            key="tester_name"
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
    
    st.divider()
    st.markdown("### 🔍 Analysis & Summary Tools")
    
    # Analysis and Summary buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

    with col_btn1:
        summarize_button = st.button("📝 Summarize", type="primary", use_container_width=True, key="analysis_summarize")

    with col_btn2:
        analyze_button = st.button("🚀 Analyze", use_container_width=True, key="analysis_analyze")

    with col_btn3:
        clear_button = st.button("🗑️ Clear", use_container_width=True, key="analysis_clear")
    
    # ===== HANDLE BUTTON CLICKS =====
    
    # Handle Analyze button
    if analyze_button:
        if not rca_content.strip():
            st.error("⚠️ Please provide RCA content to analyze.")
        elif not product_name.strip():
            st.error("⚠️ Please provide a product name.")
        elif not question.strip():
            st.error("⚠️ Please provide a question or task description.")
        else:
            with st.spinner("🔍 Analyzing documentation and generating recommendations..."):
                try:
                    # Store in session state
                    st.session_state.product_name = product_name
                    st.session_state.current_rca_content = rca_content
                    st.session_state.initial_analysis_done = True
                    
                    # Run the agent
                    result = run_agent(product_name, question, rca_content)
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        "question": question,
                        "answer": result['output'] if 'output' in result else str(result)
                    })
                    
                    # Clear follow-up answer when new analysis is done
                    if 'last_followup_answer' in st.session_state:
                        del st.session_state.last_followup_answer
                    if 'last_followup_raw' in st.session_state:
                        del st.session_state.last_followup_raw
                    
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
        render_placeholder_page("Settings", "⚙️")

if __name__ == "__main__":
    main()
