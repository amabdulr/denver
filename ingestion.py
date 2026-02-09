import os
import re
from typing import List, Set, Dict, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document

def build_pdf_section_map(pdf_path: str) -> Dict[int, str]:
    """
    Pre-process a PDF to build a page-to-section mapping.
    Scans the entire PDF to find section headers and maps them to page ranges.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary mapping page numbers to section hierarchies
    """
    print(f"   Building section map for PDF...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    page_to_section = {}
    current_sections = {"part": "", "chapter": "", "section": ""}
    
    for page_doc in pages:
        page_num = page_doc.metadata.get("page", 0)
        content = page_doc.page_content
        lines = content.split('\n')
        
        # Look for section headers in the first portion of the page
        for i, line in enumerate(lines[:30]):  # Check first 30 lines of each page
            line = line.strip()
            
            if len(line) < 3:
                continue
            
            # Part detection (highest level)
            part_match = re.match(r'^(Part\s+[IVX\d]+)[:\s\-]?\s*(.+)?$', line, re.IGNORECASE)
            if part_match:
                part_text = part_match.group(1)
                if part_match.group(2):
                    part_text += " " + part_match.group(2)
                current_sections["part"] = part_text.strip()
                current_sections["chapter"] = ""
                current_sections["section"] = ""
                continue
            
            # Chapter detection with lookahead for title on next line
            chapter_match = re.match(r'^(Chapter\s+\d+)[:\s\-]?\s*(.+)?$', line, re.IGNORECASE)
            if chapter_match:
                chapter_text = chapter_match.group(1)
                if chapter_match.group(2):
                    chapter_text += " " + chapter_match.group(2)
                else:
                    # Look at next line for title
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        # If next line looks like a title (starts with capital, reasonable length)
                        if next_line and 3 < len(next_line) < 100 and next_line[0].isupper():
                            chapter_text += " " + next_line
                current_sections["chapter"] = chapter_text.strip()
                current_sections["section"] = ""
                continue
            
            # Section/subsection detection with lookahead
            section_patterns = [
                (r'^(Section\s+[\d\.]+)[:\s\-]?\s*(.+)?$', re.IGNORECASE),
                (r'^(\d+\.\d+\.?\d*)\s+([A-Z][^\n]{5,60})$', 0),  # Numbered headings
                (r'^([A-Z][A-Z\s]{8,60})\s*$', 0),  # ALL CAPS HEADINGS
            ]
            
            for pattern, flags in section_patterns:
                match = re.match(pattern, line, flags)
                if match:
                    section_text = ' '.join(g.strip() for g in match.groups() if g)
                    # If section text is just a number/identifier, try next line for title
                    if not any(c.isalpha() and c.islower() for c in section_text) and i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and 3 < len(next_line) < 100 and next_line[0].isupper():
                            section_text += " " + next_line
                    current_sections["section"] = section_text
                    break
        
        # Build hierarchical section string for this page
        hierarchy = []
        if current_sections["part"]:
            hierarchy.append(current_sections["part"])
        if current_sections["chapter"]:
            hierarchy.append(current_sections["chapter"])
        if current_sections["section"]:
            hierarchy.append(current_sections["section"])
        
        page_to_section[page_num] = " > ".join(hierarchy) if hierarchy else ""
    
    print(f"   Mapped {len([v for v in page_to_section.values() if v])} pages with section info")
    return page_to_section

def extract_sections_from_content(content: str) -> str:
    """
    Extract section/chapter information from the actual chunk content
    Works for both markdown and PDF by looking for headers in the text
    """
    lines = content.split('\n')
    sections = []
    
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        line = line.strip()
        
        # Skip very short lines or lines that look like table content
        if len(line) < 3 or line.startswith('•') or line.startswith('-'):
            continue
        
        # Markdown headers
        md_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if md_match:
            title = md_match.group(2).strip()
            sections.append(title)
            continue
        
        # Common section patterns (PDF and formatted text)
        patterns = [
            (r'^(Part\s+[IVX\d]+)[:\s\-]?\s*(.+)?$', 1, 2),  # Part I, Part 1
            (r'^(Chapter\s+\d+)[:\s\-]?\s*(.+)?$', 1, 2),  # Chapter 1, Chapter 12
            (r'^(Section\s+[\d\.]+)[:\s\-]?\s*(.+)?$', 1, 2),  # Section 1.2.3
            (r'^(Appendix\s+[A-Z\d]+)[:\s\-]?\s*(.+)?$', 1, 2),  # Appendix A, Appendix 1
            (r'^(\d+\.\d+\.?\d*)\s+([A-Z][^\n]{5,50})$', 1, 2),  # Numbered headings: "1.2.3 Configuration"
            (r'^([A-Z][A-Z\s]{5,50})\s*$', 1, None),  # ALL CAPS HEADINGS (at least 6 chars)
            (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,})\s*$', 1, None),  # Title Case: "Rogue Detection Security Level" (3+ capitalized words)
        ]
        
        for pattern, *groups in patterns:
            # Use case-insensitive for Part/Chapter/Section, case-sensitive for others
            flags = re.IGNORECASE if any(x in pattern for x in ['Part', 'Chapter', 'Section', 'Appendix']) else 0
            match = re.match(pattern, line, flags)
            if match:
                parts = []
                for g in groups:
                    if g and match.group(g):
                        parts.append(match.group(g).strip())
                if parts:
                    sections.append(' '.join(parts))
                    break
                elif match.group(1):  # If only one group captured
                    sections.append(match.group(1).strip())
                    break
    
    if sections:
        # Return up to 3 levels of hierarchy
        return " > ".join(sections[:3])
    
    return ""


def load_documents(base_directory: str = "knowledge_docs") -> List[Document]:
    """
    Load and process all documents from the knowledge base directory.
    
    Args:
        base_directory: Path to the directory containing product subdirectories
        
    Returns:
        List of processed Document objects ready for embedding
    """
    print(f"📚 Loading documents from {base_directory}...")
    total_docs = 0
    total_files = 0
    documents: List[Document] = []

    for root, dirs, files in os.walk(base_directory):
        # loop through dirs, each dir is a product, add that as metadata label for product then loop through files
        for dir in dirs:
            product = dir
            product_dir = os.path.join(base_directory, dir)
            for product_root, product_dirs, product_files in os.walk(product_dir):
                for file in product_files:
                    if file.endswith(".md") or file.endswith(".pdf"):
                        total_files += 1
                        full_path = os.path.join(product_root, file)
                        
                        # Process all files (no persistence in in-memory mode)
                        print(f"Reading file: {full_path}")
                        
                        # For PDFs, build section map first
                        pdf_section_map = None
                        if file.endswith(".pdf"):
                            pdf_section_map = build_pdf_section_map(full_path)
                            loader = PyPDFLoader(full_path)
                        else:
                            loader = TextLoader(full_path)
                        
                        docs = loader.load()
                        print("Chunking it...")
                        # Larger chunks to capture more context including section headers
                        # 2000 chars ≈ 500 words, enough to include headers and meaningful content
                        text_splitter = CharacterTextSplitter(
                            chunk_size=2000, chunk_overlap=200
                        )
                        texts = text_splitter.split_documents(docs)
                        print(f"created {len(texts)} chunks")
                        # add metadata to each document (preserve existing metadata like page numbers)
                        for doc in texts:  # Changed from 'docs' to 'texts' to update the split chunks
                            doc.metadata["product"] = product
                            doc.metadata["source"] = full_path
                            # Page number is automatically added by PyPDFLoader for PDFs
                            
                            # Add section/part information
                            if pdf_section_map is not None and "page" in doc.metadata:
                                # For PDFs, use the pre-built section map
                                page_num = doc.metadata["page"]
                                section = pdf_section_map.get(page_num, "")
                            else:
                                # For markdown or if page mapping fails, analyze chunk content
                                section = extract_sections_from_content(doc.page_content)
                            
                            doc.metadata["section"] = section if section else "Section information not available"

                        total_docs += len(texts)  # Changed from 'docs' to 'texts'
                        documents.extend(texts)  # Changed from 'docs' to 'texts' to store the split chunks

    print(f"\n✅ Document loading complete:")
    print(f"   Files processed: {total_files}")
    print(f"   Documents created: {total_docs}")
    
    return documents


if __name__ == "__main__":
    print("="*70)
    print("🔄 ChromaDB In-Memory Ingestion")
    print("="*70)
    print("\n⚠️  WARNING: Running in IN-MEMORY mode - data will NOT persist")
    print("   SQLite 3.26.0 compatibility mode (ChromaDB requires 3.35+)")
    print("   Use start.py or vector_store_manager.py for proper initialization\n")
    
    base_directory = "knowledge_docs"
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Load documents using the reusable function
    documents = load_documents(base_directory)
    
    if not documents:
        print("\n❌ No documents found! Check knowledge_docs/ directory")
        exit(1)

    print("\n📊 Embedding documents...")
    print("   Creating IN-MEMORY vector store...")
    
    # Create in-memory vector store (no persist_directory)
    vector_store = Chroma.from_documents(
        collection_name="cisco_products_custom_loader",
        embedding=embeddings,
        documents=documents,
    )
    
    print(f"\n✅ Vector store created successfully!")
    print(f"   Total documents: {len(documents)}")
    print(f"\n⚠️  IMPORTANT: Data is IN-MEMORY ONLY")
    print(f"   - Will be LOST when this process ends")
    print(f"   - Use start.py to keep vector store alive during app runtime")
    print(f"   - Or use vector_store_manager.py for shared access")
    print("="*70)


