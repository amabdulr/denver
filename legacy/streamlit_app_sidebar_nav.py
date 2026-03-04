"""
Streamlit App - Sidebar Navigation Demo
Demonstrates the best practice for navigation in Streamlit apps using sidebar navigation
This is superior to tab-based navigation for several reasons (see README below)
"""

import streamlit as st

# Set page config FIRST - must be the first Streamlit command
st.set_page_config(
    page_title="Cisco Documentation Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_why_sidebar_is_better():
    """Display information about why sidebar navigation is better than tabs"""
    with st.expander("ℹ️ Why Sidebar Navigation is Better Than Tabs", expanded=False):
        st.markdown("""
        ### **Advantages of Sidebar Navigation over Tabs:**
        
        1. **📱 Better Mobile Experience**
           - Sidebar collapses on mobile devices
           - Tabs can overflow and become hard to navigate on small screens
        
        2. **🎯 Persistent Navigation**
           - Sidebar stays visible while scrolling through content
           - Tabs scroll away with the page content
        
        3. **🔄 URL-Based Routing**
           - Can use query parameters for shareable links to specific sections
           - Tabs don't support deep linking natively
        
        4. **📊 More Space for Content**
           - Sidebar doesn't take up horizontal space in main area
           - Tabs consume vertical space at the top
        
        5. **🎨 Better Visual Hierarchy**
           - Clear separation between navigation and content
           - Sidebar can include additional context (filters, settings)
        
        6. **🔢 Handles More Sections**
           - Sidebar can accommodate many navigation items with scrolling
           - Too many tabs become cramped and hard to use
        
        7. **♿ Better Accessibility**
           - Screen readers handle sidebar navigation better
           - Keyboard navigation is more intuitive
        
        8. **🎭 Professional Look**
           - More enterprise-application feel
           - Standard pattern used by major web applications
        """)

def render_analysis_page():
    """Render the Analysis & Summary page"""
    st.header("🔍 Analysis & Summary")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Bug Information")
        bug_number = st.text_input("Enter Bug Number", key="analysis_bug")
        product = st.selectbox("Product", ["Cisco 9800", "ASR9000", "Cisco 8000", "SD-WAN"], key="analysis_product")
        
        if st.button("🔍 Analyze Bug", type="primary"):
            st.success(f"Analyzing bug {bug_number} for {product}...")
    
    with col2:
        st.subheader("Quick Actions")
        st.button("📋 View Bug Details")
        st.button("📝 Add Note")
        st.button("🔗 Copy Link")
    
    st.markdown("---")
    st.subheader("Analysis Results")
    st.info("Enter a bug number and click 'Analyze Bug' to see results here.")

def render_first_draft_page():
    """Render the First Draft page"""
    st.header("✍️ First Draft")
    st.markdown("---")
    
    st.subheader("Generate Documentation")
    
    template_type = st.selectbox(
        "Select Template Type",
        ["Concept", "Task", "Reference", "Troubleshooting"]
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.text_area("Bug Summary", height=150, placeholder="Paste bug summary here...")
    
    with col2:
        st.subheader("Options")
        st.checkbox("Include diagrams", value=True)
        st.checkbox("Add examples", value=True)
        st.checkbox("Include CLI commands", value=False)
    
    if st.button("✨ Generate First Draft", type="primary"):
        st.success("Generating first draft...")

def render_bulk_analysis_page():
    """Render the Bulk Analysis page"""
    st.header("📊 Bulk Analysis")
    st.markdown("---")
    
    st.subheader("Analyze Multiple Bugs")
    
    bugs_input = st.text_area(
        "Enter bug numbers (one per line)",
        height=150,
        placeholder="CSCaa11111\nCSCbb22222\nCSCcc33333"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Bugs to Process", "0")
    with col2:
        st.metric("Processed", "0")
    with col3:
        st.metric("Failed", "0")
    
    if st.button("🚀 Start Bulk Analysis", type="primary"):
        st.success("Starting bulk analysis...")

def render_resolve_bug_page():
    """Render the Resolve Bug page"""
    st.header("🔧 Resolve Bug")
    st.markdown("---")
    
    st.subheader("Bug Resolution Workflow")
    
    bug_number = st.text_input("Bug Number", key="resolve_bug")
    
    resolution_type = st.selectbox(
        "Resolution Type",
        ["Fixed", "Duplicate", "Won't Fix", "Cannot Reproduce", "By Design"]
    )
    
    resolution_notes = st.text_area(
        "Resolution Notes",
        height=200,
        placeholder="Describe the resolution..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Submit Resolution", type="primary"):
            st.success("Bug resolved successfully!")
    
    with col2:
        if st.button("📧 Send Email Notification"):
            st.info("Email sent to submitter")

def render_settings_page():
    """Render the Settings page"""
    st.header("⚙️ Settings")
    st.markdown("---")
    
    st.subheader("Application Settings")
    
    with st.expander("🔐 API Configuration", expanded=True):
        st.text_input("OpenAI API Key", type="password", value="sk-...")
        st.text_input("Cisco API Token", type="password")
    
    with st.expander("📁 Knowledge Base"):
        st.text_input("Knowledge Base Path", value="./knowledge_docs")
        st.button("🔄 Reload Knowledge Base")
    
    with st.expander("🎨 Display Options"):
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.slider("Font Size", 10, 20, 14)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# ==================== MAIN APP ====================

def main():
    """Main application logic with sidebar navigation"""
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("📚 Cisco Doc Assistant")
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigation",
            ["🔍 Analysis & Summary", "✍️ First Draft", "📊 Bulk Analysis", "🔧 Resolve Bug", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Additional sidebar content
        with st.expander("ℹ️ Quick Info"):
            st.caption("**User:** Admin")
            st.caption("**Version:** 2.0.0")
            st.caption("**Last Updated:** Feb 2026")
        
        # Show comparison info at bottom of sidebar
        st.markdown("---")
        st.caption("💡 Using sidebar navigation instead of tabs")
    
    # Show the comparison info at the top
    show_why_sidebar_is_better()
    
    # Route to the selected page
    if page == "🔍 Analysis & Summary":
        render_analysis_page()
    elif page == "✍️ First Draft":
        render_first_draft_page()
    elif page == "📊 Bulk Analysis":
        render_bulk_analysis_page()
    elif page == "🔧 Resolve Bug":
        render_resolve_bug_page()
    elif page == "⚙️ Settings":
        render_settings_page()

if __name__ == "__main__":
    main()
