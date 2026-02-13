"""
Helper functions for the Streamlit app
Contains all the business logic and agent operations

ANALOGY: Think of this module as the "ENGINE ROOM" of a ship 🚢
- streamlit_app.py is the BRIDGE (controls and displays)
- app_functions.py is the ENGINE ROOM (does all the heavy work)
- first_draft_tab.py is a SPECIALIZED DECK (handles specific operations)

The captain (user) gives orders on the bridge, but all the power and processing
happens down in the engine room where the real work gets done.

FUNCTIONS OVERVIEW:
├── get_product_info()      : 🔍 RAG search tool - Queries vector database for product documentation
├── run_agent()             : 🤖 AI Agent orchestrator - Runs LangChain agent with tools and prompts
├── format_output()         : 📋 Output formatter - Converts agent responses to readable markdown
└── apply_prompt_file()     : 📝 Prompt template engine - Reads .md files and populates placeholders

This module handles:
- Vector database queries (Chroma + HuggingFace embeddings)
- LangChain agent execution (OpenAI Functions Agent)
- LLM invocations (via utils.get_llm())
- Template-based prompt generation
"""

from typing import List
import time
from langchain.agents import (
    AgentExecutor,
    OpenAIFunctionsAgent,
    create_openai_functions_agent,
)
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from utils import get_llm
import streamlit as st

# Rate limiting: Track last call time to avoid API throttling
_last_tool_call_time = 0
_min_call_interval = 4.5  # Minimum 4.5 seconds between calls (15 calls per 60 seconds = ~4s each)


@tool
def get_product_info(product: str, query: str) -> str:
    """given a Cisco product name and a query, return the product context with metadata
    Args:
        product: Cisco product name. Valid products are: "sdwan", "cisco_generic", "9800", "ASR9000", "Cisco8000"
        query: user query about the product
    Returns:
        Formatted string with content and metadata (page, section) for each chunk
    
    Note: If guides have been selected by the user, results will be automatically filtered to those guides
    """
    global _last_tool_call_time
    
    # Rate limiting: Ensure minimum interval between calls
    current_time = time.time()
    time_since_last_call = current_time - _last_tool_call_time
    if time_since_last_call < _min_call_interval:
        sleep_time = _min_call_interval - time_since_last_call
        print(f"⏱️ Rate limiting: Waiting {sleep_time:.1f}s before next API call...")
        time.sleep(sleep_time)
    
    _last_tool_call_time = time.time()
    
    # Get selected guides from session state if available
    guides = None
    try:
        import streamlit as st
        guides = st.session_state.get('selected_guides_for_search', None)
    except:
        pass  # Session state not available, search all guides
    
    metadata_field_info = [
        AttributeInfo(
            name="source",
            description="The source file the information came from",
            type="string",
        ),
        AttributeInfo(
            name="product",
            description='Cisco product name. Valid products are: "sdwan", "cisco_generic", "9800", "ASR9000", "Cisco8000"',
            type="string",
        ),
    ]
    document_content_description = "Cisco Product information"
    llm = get_llm()
    
    # IMPORTANT: Using shared in-memory ChromaDB due to SQLite 3.26.0 constraint
    # Vector store is initialized at app startup via vector_store_manager
    from vector_store_manager import get_vector_store, initialize_vector_store
    
    try:
        vectorstore = get_vector_store()
    except RuntimeError:
        # Fallback: Initialize if not already done
        # This shouldn't happen if startup initialization worked
        import streamlit as st
        if st.session_state.get('vector_store_init_attempted', False):
            # Don't show warning again if we already tried at startup
            vectorstore = initialize_vector_store()
        else:
            st.warning("⚠️ Vector store not initialized. Initializing now...")
            vectorstore = initialize_vector_store()
            st.session_state.vector_store_init_attempted = True
    
    # If guides are selected, use direct similarity search instead of SelfQueryRetriever
    # SelfQueryRetriever doesn't work well with source file filtering
    if guides and len(guides) > 0:
        # Build filter for selected guides
        guide_paths = [f"knowledge_docs/{product.lower()}/{guide}" if '/' not in guide else guide 
                      for guide in guides]
        
        # Map UI product names to internal codes if needed
        product_mapping = {
            "Cisco SD-WAN": "sdwan",
            "Cisco 9800": "9800",
            "ASR 9000": "ASR9000",
            "Cisco 8000": "Cisco8000",
            "cisco_generic": "cisco_generic"
        }
        product_code = product_mapping.get(product, product)
        
        # Update paths with correct product code
        guide_paths = [f"knowledge_docs/{product_code}/{guide}" for guide in guides]
        
        # For single guide, use direct filter
        if len(guides) == 1:
            search_filter = {
                "$and": [
                    {"product": product_code},
                    {"source": guide_paths[0]}
                ]
            }
        else:
            # For multiple guides, use $or
            search_filter = {
                "$and": [
                    {"product": product_code},
                    {"$or": [{"source": path} for path in guide_paths]}
                ]
            }
        
        # Use direct similarity search with metadata filter
        result = vectorstore.similarity_search(
            query=query,
            k=10,
            filter=search_filter
        )
    else:
        # Use SelfQueryRetriever for normal searches without guide filtering
        retriever = SelfQueryRetriever.from_llm(
            llm,
            vectorstore,
            document_content_description,
            metadata_field_info,
            enable_limit=True,
            verbose=True,
        )
        
        result = retriever.invoke(f"Product: {product}\nQuery: {query}")
    
    # Filter out unwanted content (e.g., Cisco Bug Search Tool references)
    excluded_keywords = [
        "cisco bug search tool",
        "bug search tool",
        "bst",
        "cisco bug tracker"
    ]
    
    filtered_result = []
    for doc in result:
        content_lower = doc.page_content.lower()
        section_lower = doc.metadata.get('section', '').lower()
        
        # Skip if any excluded keyword is found in content or section
        if any(keyword in content_lower or keyword in section_lower for keyword in excluded_keywords):
            continue
        
        filtered_result.append(doc)
    
    # Use filtered results
    result = filtered_result
    
    # Check if we got any results
    if not result or len(result) == 0:
        return f"""
❌ NO DOCUMENTS FOUND ❌

The search for "{query}" in product "{product}" returned ZERO results.

POSSIBLE REASONS:
1. The product name might be incorrect. Available products: "sdwan", "cisco_generic", "9800", "ASR9000", "Cisco8000"
2. The search query might be too specific or use terms not in the documentation
3. The relevant documentation might not be loaded into the database

⚠️ CRITICAL INSTRUCTION: Do NOT invent or fabricate any documents, sections, page numbers, or quotes.
You MUST tell the user that no documents were found and cannot provide recommendations without actual source material.
"""
    
    # Format the result to include metadata explicitly
    formatted_chunks = []
    for i, doc in enumerate(result, 1):
        chunk_info = f"\n--- CHUNK {i} ---"
        chunk_info += f"\nSource: {doc.metadata.get('source', 'Unknown')}"
        
        # Prefer page_label (printed page number) over page (file index)
        page_num = doc.metadata.get('page_label') or doc.metadata.get('page')
        chunk_info += f"\nPage: {page_num if page_num is not None else 'Not available'}"
        
        chunk_info += f"\nSection: {doc.metadata.get('section', 'Not available')}"
        chunk_info += f"\n\nCONTENT:\n{doc.page_content}\n"
        formatted_chunks.append(chunk_info)
    
    return "\n".join(formatted_chunks)


def run_agent(product_name: str, question: str, rca_content: str, selected_guides: List[str] = None):
    """Run the agent with the given inputs
    
    Args:
        product_name: Cisco product name
        question: User's question/task
        rca_content: Bug report or RCA content
        selected_guides: Optional list of guide filenames to limit search scope
    """
    
    # Store selected guides in session state for tool access
    if selected_guides:
        import streamlit as st
        st.session_state.selected_guides_for_search = selected_guides
    
    # Append RCA content to the question
    full_question = question + rca_content
    
    # Build guide filter message for prompt
    guide_filter_message = ""
    if selected_guides and len(selected_guides) > 0:
        guides_list = ', '.join(selected_guides)
        guide_filter_message = f"""
    
    🎯 SEARCH SCOPE LIMITATION:
    The user has selected specific guides to search. You MUST limit your search to these guides only:
    {guides_list}
    
    When calling get_product_info, the results will automatically be filtered to these guides.
    """
    
    product_version_prompt_template = f"""
    given a Cisco product name and a question from a user, return the answer.
    Use your tools to fetch context to answer the question to provide a more accurate answer.
    
    Cisco product: {{product_name}}
    question: {{question}}
    {guide_filter_message}
    ⚠️ CRITICAL ANTI-HALLUCINATION RULES:
    1. ONLY use information that the get_product_info tool actually returned
    2. If the tool returns "❌ NO DOCUMENTS FOUND ❌", you MUST tell the user no documentation was found
    3. DO NOT invent document names, page numbers, sections, or quotes
    4. DO NOT make up plausible-sounding information
    5. When referencing content, quote EXACT text from the retrieved chunks
    6. When stating page numbers or sections, copy EXACTLY from the chunk metadata
    7. If metadata is "Not available", say so - don't guess or invent
    
    ⚠️ IMPORTANT: Be efficient with tool calls to avoid rate limiting (max 15 calls per minute)
    - Call get_product_info only when you need NEW information
    - Don't repeat searches with similar queries
    - Use the information from previous tool calls when possible
    
    answer:
    """

    product_prompt_template = PromptTemplate(
        input_variables=["product_name", "question"],
        template=product_version_prompt_template,
    )

    llm = get_llm()

    prompt = OpenAIFunctionsAgent.create_prompt()
    agent = create_openai_functions_agent(
        llm=llm, tools=[get_product_info], prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent, tools=[get_product_info], verbose=False, stream_runnable=False
    )
    
    res = agent_executor.invoke(
        input={
            "input": product_prompt_template.format_prompt(
                product_name=product_name,
                question=full_question,
            )
        }
    )

    return res


def format_output(result: dict) -> str:
    """Format the agent output in a readable way"""
    if 'output' in result:
        output_text = result['output']
        
        # Format the output with markdown
        formatted = f"""## 📋 Documentation Recommendation

{output_text}

---
### 🔍 Query Details
**Product:** {st.session_state.product_name}
**Status:** ✅ Analysis Complete
"""
        return formatted
    return "No output received from agent."


def apply_prompt_file(prompt_file_path: str, rca_content: str, product_name: str = "") -> str:
    """
    Apply a prompt from a markdown file to the RCA content
    
    Args:
        prompt_file_path: Path to the prompt.md file
        rca_content: The RCA/bug content to analyze
        product_name: Optional product name for context
    
    Returns:
        LLM response as string
    """
    # Read the prompt file
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Replace placeholders with actual content
    full_prompt = prompt_template.replace("{rca_content}", rca_content)
    full_prompt = full_prompt.replace("{extracted_text}", rca_content)
    full_prompt = full_prompt.replace("{product_name}", product_name)
    full_prompt = full_prompt.replace("{product}", product_name)
    
    # Get LLM and invoke
    llm = get_llm()
    result = llm.invoke(full_prompt)
    
    return result.content if hasattr(result, 'content') else str(result)


def run_agent_with_prompt_file(prompt_file_path: str, rca_content: str, product_name: str) -> str:
    """
    Run the agent with a custom prompt file and RAG capabilities
    
    This function is similar to run_agent() but allows using custom prompt files
    like ChapterFinder.md and ContentWriter.md while maintaining RAG functionality.
    
    Args:
        prompt_file_path: Path to the prompt.md file (e.g., "ChapterFinder.md")
        rca_content: The RCA/bug content to analyze
        product_name: Cisco product name for context
    
    Returns:
        Agent's response as string
    """
    # Read the prompt file
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Build the full question with RCA content
    full_question = f"""
{prompt_template}

---

### BUG/RCA CONTENT TO ANALYZE:

{rca_content}

---

Cisco Product: {product_name}
"""
    
    # Create the agent prompt template
    agent_prompt_template = """
    Given a Cisco product name and analysis instructions, provide the requested analysis.
    Use your tools to fetch context from documentation to provide accurate recommendations.
    
    Cisco product: {product_name}
    
    Analysis request and content:
    {question}
    
    ⚠️ CRITICAL ANTI-HALLUCINATION RULES:
    1. ONLY use information that the get_product_info tool actually returned
    2. If the tool returns "❌ NO DOCUMENTS FOUND ❌", you MUST tell the user no documentation was found
    3. DO NOT invent document names, page numbers, sections, or quotes
    4. DO NOT make up plausible-sounding information
    5. When referencing content, quote EXACT text from the retrieved chunks
    6. When stating page numbers or sections, copy EXACTLY from the chunk metadata
    7. If metadata is "Not available", say so - don't guess or invent
    
    ⚠️ IMPORTANT: Be efficient with tool calls to avoid rate limiting (max 15 calls per minute)
    - Call get_product_info only when you need NEW information
    - Don't repeat searches with similar queries
    - Use the information from previous tool calls when possible
    
    analysis:
    """
    
    product_prompt_template = PromptTemplate(
        input_variables=["product_name", "question"],
        template=agent_prompt_template,
    )
    
    llm = get_llm()
    
    prompt = OpenAIFunctionsAgent.create_prompt()
    agent = create_openai_functions_agent(
        llm=llm, tools=[get_product_info], prompt=prompt
    )
    
    agent_executor = AgentExecutor(
        agent=agent, tools=[get_product_info], verbose=False, stream_runnable=False
    )
    
    res = agent_executor.invoke(
        input={
            "input": product_prompt_template.format_prompt(
                product_name=product_name,
                question=full_question,
            )
        }
    )
    
    # Extract the output
    if isinstance(res, dict) and 'output' in res:
        return res['output']
    return str(res)
