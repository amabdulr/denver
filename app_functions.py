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
    from vector_store_manager import get_vector_store
    
    try:
        vectorstore = get_vector_store()
    except RuntimeError as e:
        # Fallback: Initialize if not already done (shouldn't happen in production)
        st.warning("⚠️ Vector store not initialized. Initializing now...")
        from vector_store_manager import initialize_vector_store
        vectorstore = initialize_vector_store()
    
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


def run_agent(product_name: str, question: str, rca_content: str):
    """Run the agent with the given inputs"""
    
    # Append RCA content to the question
    full_question = question + rca_content
    
    product_version_prompt_template = """
    given a Cisco product name and a question from a user, return the answer.
    Use your tools to fetch context to answer the question to provide a more accurate answer.
    
    Cisco product: {product_name}
    question: {question}
    
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
