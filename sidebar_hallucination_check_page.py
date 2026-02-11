"""
Hallucination Check Sidebar Page Component
Handles the Hallucination Check workflow for sidebar navigation app
"""

import streamlit as st
from app_functions import apply_prompt_file, run_agent


def render_hallucination_check_page():
    """Render the Hallucination Check page with full functionality for sidebar navigation"""
    st.header("🔍 Hallucination Check")
    st.markdown("Compare original source content with AI-generated modified content to identify hallucinations")
    
    # Step-by-step instructions
    with st.expander("📖 How to Use This Page", expanded=False):
        st.markdown("""
        #### Verify AI-Generated Content Accuracy
        
        **Step 1: Provide Original Content**
        1. **Upload Source Document(s)**: Upload original source files (.txt, .md, .pdf, .docx) in the left column
           - Uploaded files will automatically populate the text area
        2. **Or Paste Content**: Manually paste the original source content into the "Original Source Content" text area
        
        **Step 2: Provide Modified Content**
        1. **Paste AI-Generated Content**: In the right column, paste the AI-generated or modified content you want to verify
        2. **Ensure Completeness**: Make sure you've pasted all the content you want to check
        
        **Step 3: Run Analysis**
        1. **Click Check Button**: Click "🔍 Check for Hallucinations" in the center
        2. **Wait for Analysis**: The AI will compare both versions and identify:
           - Added information not present in the original
           - Modified facts or statements
           - Removed important information
           - Potential hallucinations or fabrications
        
        **Step 4: Review Results**
        1. **Read Analysis Report**: Review the detailed analysis in the "Analysis Results" section
        2. **Check Findings**: Look for highlighted hallucinations and inaccuracies
        3. **Ask Follow-ups** (optional): Use the follow-up question field to clarify specific findings
        4. **Copy Output**: Use the copy button to save the analysis report
        
        **Tips**:
        - More complete original content = more accurate hallucination detection
        - The tool identifies both additions and omissions
        - Follow-up questions can help investigate specific concerns
        """)
    
    # Create three-column layout for better organization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Original Content")
        st.markdown("Upload a document or paste the original source content")
        
        # File upload section
        uploaded_files_hal = st.file_uploader(
            "Upload source document(s)",
            type=["txt", "md", "pdf", "docx"],
            accept_multiple_files=True,
            key="sidebar_hal_upload",
            help="Upload one or more source documents"
        )
        
        # Initialize original content from upload or session state
        original_content = ""
        if uploaded_files_hal:
            file_contents = []
            for uploaded_file in uploaded_files_hal:
                file_content = uploaded_file.read().decode("utf-8", errors="ignore")
                file_contents.append(f"\n{'='*80}\n FILE: {uploaded_file.name}\n{'='*80}\n{file_content}")
            original_content = "\n".join(file_contents)
            st.session_state.hal_original_content = original_content
        elif 'hal_original_content' in st.session_state:
            original_content = st.session_state.hal_original_content
        
        # Original content text area
        original_text = st.text_area(
            "Original Source Content",
            value=original_content,
            height=400,
            key="sidebar_hal_original_text",
            help="The original source content that should be the basis for the modified content",
            placeholder="Upload documents above or paste original content here..."
        )
    
    with col2:
        st.subheader("✨ Modified Content")
        st.markdown("Paste the AI-generated or modified content to check")
        
        # Modified content text area
        modified_text = st.text_area(
            "AI-Generated/Modified Content",
            height=400,
            key="sidebar_hal_modified_text",
            help="The AI-generated or modified content to check for hallucinations",
            placeholder="Paste the AI-generated or modified content here..."
        )
    
    # Compare button and output section
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    
    with col_btn2:
        compare_button = st.button(
            "🔍 Check for Hallucinations",
            type="primary",
            use_container_width=True,
            help="Analyze the modified content for hallucinations",
            key="sidebar_hal_compare"
        )
    
    # Output section
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    output_container = st.container()
    
    # Display last analysis if available
    if 'hal_conversation_history' in st.session_state and st.session_state.hal_conversation_history:
        with output_container:
            # Show the most recent analysis
            last_exchange = st.session_state.hal_conversation_history[-1]
            if last_exchange.get('question') == 'Hallucination Check':
                st.markdown("## 🔍 Hallucination Analysis Report")
                st.markdown(last_exchange['answer'])
            else:
                # Follow-up answer
                st.markdown("## 💬 Follow-up Response")
                st.markdown(last_exchange['answer'])
    
    # Handle compare button
    if compare_button:
        handle_hallucination_check(original_text, modified_text, output_container)
    
    # Follow-up questions section
    if 'hal_conversation_history' in st.session_state and st.session_state.hal_conversation_history:
        st.markdown("---")
        st.subheader("💬 Follow-up Questions")
        st.info("Ask questions about the hallucination analysis, request clarification, or ask for more details.")
        
        # Display conversation history
        with st.expander("📜 View Conversation History", expanded=False):
            for idx, exchange in enumerate(st.session_state.hal_conversation_history, 1):
                st.markdown(f"**Q{idx}:** {exchange['question']}")
                st.markdown(f"**A{idx}:** {exchange['answer'][:500]}..." if len(exchange['answer']) > 500 else f"**A{idx}:** {exchange['answer']}")
                st.markdown("---")
        
        # Follow-up question input
        followup_question = st.text_area(
            "Ask a follow-up question",
            placeholder="e.g., Can you provide more details about hallucination #2?",
            height=100,
            key="sidebar_hal_followup_input"
        )
        
        submit_followup = st.button(
            "📤 Ask Follow-up",
            type="secondary",
            use_container_width=True,
            key="sidebar_hal_followup_btn"
        )
        
        if submit_followup:
            if not followup_question.strip():
                st.warning("⚠️ Please enter a follow-up question.")
            else:
                with st.spinner("🔍 Processing your follow-up question..."):
                    try:
                        # Build context from conversation history
                        context = "\n\nPrevious conversation:\n"
                        for idx, exchange in enumerate(st.session_state.hal_conversation_history, 1):
                            context += f"Q{idx}: {exchange['question']}\nA{idx}: {exchange['answer']}\n\n"
                        
                        # Add follow-up question with context
                        full_followup = context + f"\nFollow-up question: {followup_question}"
                        
                        # Use the stored content for context
                        content_to_use = st.session_state.get('hal_analysis_context', '')
                        
                        # Run the agent with follow-up question
                        result = run_agent(
                            "", 
                            full_followup, 
                            content_to_use
                        )
                        
                        followup_answer = result['output'] if 'output' in result else str(result)
                        
                        # Add to conversation history
                        st.session_state.hal_conversation_history.append({
                            "question": followup_question,
                            "answer": followup_answer
                        })
                        
                        st.success("✅ Follow-up answered! Check the Analysis Results section above.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing follow-up: {str(e)}")
                        with st.expander("🐛 Error Details"):
                            st.exception(e)


def handle_hallucination_check(original_text: str, modified_text: str, output_container):
    """Handle the hallucination check comparison"""
    if not original_text.strip():
        st.error("⚠️ Please provide original source content.")
    elif not modified_text.strip():
        st.error("⚠️ Please provide modified content to check.")
    else:
        with st.spinner("🔍 Analyzing for hallucinations..."):
            try:
                # Build context for hallucination check
                context = f"""# Original Source Content

{original_text}

{'='*80}

# Modified/AI-Generated Content to Check

{modified_text}

{'='*80}
"""
                
                # Initialize conversation history for hal-check if not exists
                if 'hal_conversation_history' not in st.session_state:
                    st.session_state.hal_conversation_history = []
                
                # Store the context for follow-up questions
                st.session_state.hal_analysis_context = context
                
                # Use the apply_prompt_file function with HallucinationCheck.md
                analysis = apply_prompt_file("HallucinationCheck.md", context, "")
                
                # Add to conversation history
                st.session_state.hal_conversation_history.append({
                    "question": "Hallucination Check",
                    "answer": analysis
                })
                
                with output_container:
                    st.markdown("## 🔍 Hallucination Analysis Report")
                    st.markdown(analysis)
                    st.info("💡 Review the analysis above to understand which parts of the modified content are properly sourced and which may be hallucinated. You can ask follow-up questions below.")
                
                st.success("✅ Hallucination check complete!")
                
            except Exception as e:
                st.error(f"❌ Error performing hallucination check: {str(e)}")
                with st.expander("🐛 Error Details"):
                    st.exception(e)
