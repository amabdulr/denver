"""
Convert Tab Component
Handles conversion of content to different XML formats
"""

import streamlit as st
import re
import os
from app_functions import apply_prompt_file


def strip_markdown_elements(text):
    """Strip markdown code blocks and formatting from text"""
    # Remove markdown code blocks (```xml ... ```)
    text = re.sub(r'```xml\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    
    # Remove markdown headers at start of lines
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    return text.strip()


def convert_to_xml(raw_content, conversion_type, prompt_file_name):
    """
    Convert raw content to XML format using AI prompt and template
    
    Args:
        raw_content: The raw text content to convert
        conversion_type: The type of XML format (ct-concept, ct-task, etc.)
        prompt_file_name: The name of the prompt file to use
    
    Returns:
        tuple: (xml_output, error_message)
    """
    try:
        # Read the template XML file
        template_path = f"templates/{conversion_type}.xml"
        if not os.path.exists(template_path):
            return None, f"Template file not found: {template_path}"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_xml = f.read()
        
        # Build context with raw content and template
        context = f"Raw Content to Convert:\n{raw_content}\n\n"
        context += "=" * 80 + "\n"
        context += "XML TEMPLATE STRUCTURE:\n"
        context += "=" * 80 + "\n"
        context += template_xml + "\n"
        context += "=" * 80 + "\n\n"
        context += "INSTRUCTIONS: Convert the raw content above into properly formatted XML following the template structure. "
        context += "Fill in all placeholders with appropriate content from the raw text. "
        context += "Maintain valid XML syntax and structure. Return only the XML without any markdown formatting.\n\n"
        
        # Use apply_prompt_file to generate the XML
        # Using empty product_name since it's not needed for conversion
        xml_result = apply_prompt_file(prompt_file_name, context, "")
        
        # Strip any markdown elements from the result
        cleaned_xml = strip_markdown_elements(xml_result)
        
        return cleaned_xml, None
        
    except Exception as e:
        return None, f"Error during conversion: {str(e)}"


def render_convert_tab():
    """Render the Convert tab content"""
    st.markdown("""
        <style>
        .convert-header {
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for XML output
    if 'xml_output' not in st.session_state:
        st.session_state.xml_output = ""
    
    # Create two columns for input and output
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="convert-header">📝 Input</p>', unsafe_allow_html=True)
        
        # Text area for raw content input
        raw_content = st.text_area(
            "Raw Content",
            height=400,
            placeholder="Paste your raw content here...",
            help="Paste the content you want to convert to XML format",
            key="convert_raw_content"
        )
        
        # Dropdown for selecting conversion type
        conversion_type = st.selectbox(
            "Conversion Type",
            options=[
                "ct-concept",
                "ct-task",
                "ct-reference",
                "ct-process",
                "ct-principle",
                "chaptermap"
            ],
            help="Select the type of XML format to convert to"
        )
        
        # Convert button
        convert_button = st.button(
            "🔄 Convert to XML",
            type="primary",
            use_container_width=True,
            help="Convert the raw content to the selected XML format"
        )
    
    with col2:
        st.markdown('<p class="convert-header">📄 Output</p>', unsafe_allow_html=True)
        
        # Text area for XML output - no key to avoid state conflicts
        xml_output = st.text_area(
            "XML Output",
            value=st.session_state.xml_output,
            height=400,
            placeholder="Converted XML will appear here...",
            help="The converted XML content",
            label_visibility="collapsed"
        )
        
        # Download button
        if st.session_state.xml_output:
            st.download_button(
                label="📥 Download XML",
                data=st.session_state.xml_output,
                file_name=f"{conversion_type}.xml",
                mime="application/xml",
                use_container_width=True
            )
        else:
            st.button(
                "📥 Download XML",
                use_container_width=True,
                disabled=True,
                help="Convert content first to enable download"
            )
    
    return convert_button, raw_content, conversion_type
