import os
import re
from typing import List, Set, Dict, Optional
from paths import KNOWLEDGE_DOCS_DIR

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
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


def load_documents(base_directory: str = None) -> List[Document]:
    """
    Load and process all documents from the knowledge base directory.
    
    Args:
        base_directory: Path to the directory containing product subdirectories.
                        Defaults to KNOWLEDGE_DOCS_DIR.
        
    Returns:
        List of processed Document objects ready for embedding
    """
    if base_directory is None:
        base_directory = KNOWLEDGE_DOCS_DIR
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
                    if file.endswith((".md", ".pdf", ".txt")):
                        total_files += 1
                        full_path = os.path.join(product_root, file)
                        
                        # Process all files (no persistence in in-memory mode)
                        print(f"Reading file: {full_path}")
                        
                        # For PDFs, build section map first
                        pdf_section_map = None
                        try:
                            if file.endswith(".pdf"):
                                pdf_section_map = build_pdf_section_map(full_path)
                                loader = PyPDFLoader(full_path)
                            else:
                                loader = TextLoader(full_path)
                        
                            docs = loader.load()
                        except Exception as e:
                            print(f"⚠️  Skipping {file}: {e}")
                            continue
                        print("Chunking it...")
                        # 800 chars ≈ 200 words — small enough to give granular
                        # search results from .txt chapter files while still
                        # capturing meaningful context from larger PDFs.
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=800, chunk_overlap=100
                        )
                        texts = text_splitter.split_documents(docs)
                        print(f"created {len(texts)} chunks")

                        # Derive 'book' metadata from directory structure.
                        # For a .txt/.md file in  knowledge_docs/<product>/<book-slug>/chapter.md
                        # the book is the parent directory name (e.g. 'appqoe-book-xe')
                        # and the chapter is the filename without extension (e.g. 'etherchann').
                        # For a .pdf file directly under knowledge_docs/<product>/,
                        # the book is the filename without extension.
                        rel_from_product = os.path.relpath(full_path, product_dir)
                        rel_parts = rel_from_product.replace(os.sep, '/').split('/')
                        if len(rel_parts) >= 2:
                            book_name = rel_parts[0]  # directory name
                            chapter_name = os.path.splitext(rel_parts[-1])[0]  # filename without ext
                        else:
                            book_name = os.path.splitext(file)[0]  # filename without ext
                            chapter_name = ""

                        # add metadata to each document (preserve existing metadata like page numbers)
                        for doc in texts:  # Changed from 'docs' to 'texts' to update the split chunks
                            doc.metadata["product"] = product
                            doc.metadata["source"] = full_path
                            doc.metadata["book"] = book_name
                            doc.metadata["chapter"] = chapter_name
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


def get_all_document_paths(base_directory: str = None) -> Set[str]:
    if base_directory is None:
        base_directory = KNOWLEDGE_DOCS_DIR
    """
    Get all document file paths without loading them
    
    Args:
        base_directory: Base directory containing knowledge documents
        
    Returns:
        Set of absolute file paths
    """
    file_paths = set()
    
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith(('.pdf', '.txt', '.md')):
                full_path = os.path.abspath(os.path.join(root, file))
                file_paths.add(full_path)
    
    return file_paths


def load_documents_from_path(file_path: str) -> List[Document]:
    """
    Load and process documents from a single file path
    
    Args:
        file_path: Path to a single document file
        
    Returns:
        List of processed Document objects with metadata
    """
    documents = []
    
    # Determine product from path
    path_parts = file_path.split(os.sep)
    product = "unknown"
    for part in path_parts:
        if part in ["sdwan", "9800", "ASR9000", "Cisco8000", "cisco_generic"]:
            product = part
            break
    
    filename = os.path.basename(file_path)
    print(f"   Loading: {filename}")
    
    try:
        # Load based on file type
        if file_path.endswith('.pdf'):
            # Build section map first
            pdf_section_map = build_pdf_section_map(file_path)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
        else:
            # Text or markdown file
            loader = TextLoader(file_path)
            docs = loader.load()
            pdf_section_map = None
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, chunk_overlap=100
        )
        texts = text_splitter.split_documents(docs)
        
        # Derive 'book' metadata from directory structure
        rel = os.path.relpath(file_path)
        rel_parts = rel.replace(os.sep, '/').split('/')
        # e.g. knowledge_docs/sdwan/appqoe-book-xe/chapter.txt → book = appqoe-book-xe
        # e.g. knowledge_docs/sdwan/qos-book-xe.pdf → book = qos-book-xe
        book_name = None
        for i, part in enumerate(rel_parts):
            if part in ['sdwan', '9800', 'ASR9000', 'Cisco8000', 'cisco_generic']:
                if i + 1 < len(rel_parts):
                    next_part = rel_parts[i + 1]
                    if '.' in next_part and i + 1 == len(rel_parts) - 1:
                        book_name = os.path.splitext(next_part)[0]
                    else:
                        book_name = next_part
                break
        if not book_name:
            book_name = os.path.splitext(os.path.basename(file_path))[0]

        # Add metadata
        for doc in texts:
            doc.metadata["product"] = product
            doc.metadata["source"] = os.path.relpath(file_path)
            doc.metadata["book"] = book_name
            
            # Add section information
            if pdf_section_map is not None and "page" in doc.metadata:
                page_num = doc.metadata["page"]
                section = pdf_section_map.get(page_num, "")
            else:
                section = extract_sections_from_content(doc.page_content)
            
            doc.metadata["section"] = section if section else "Section information not available"
        
        documents.extend(texts)
        
    except Exception as e:
        print(f"      ❌ Error loading {filename}: {e}")
    
    return documents


if __name__ == "__main__":
    print("="*70)
    print("🔄 ChromaDB In-Memory Ingestion")
    print("="*70)
    print("\n⚠️  WARNING: Running in IN-MEMORY mode - data will NOT persist")
    print("   SQLite 3.26.0 compatibility mode (ChromaDB requires 3.35+)")
    print("   Use start.py or vector_store_manager.py for proper initialization\n")
    
    base_directory = KNOWLEDGE_DOCS_DIR
    
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
    
    # Create vector store in batches to avoid ChromaDB limit (max ~5461)
    BATCH_SIZE = 5000
    
    if len(documents) > BATCH_SIZE:
        print(f"   Processing {len(documents)} documents in batches of {BATCH_SIZE}...")
        
        # Create with first batch
        first_batch = documents[:BATCH_SIZE]
        vector_store = Chroma.from_documents(
            collection_name="cisco_products_custom_loader",
            embedding=embeddings,
            documents=first_batch,
        )
        print(f"   ✅ Created vector store with {len(first_batch)} chunks")
        
        # Add remaining batches
        remaining = documents[BATCH_SIZE:]
        num_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
        for i in range(0, len(remaining), BATCH_SIZE):
            batch = remaining[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 2
            vector_store.add_documents(batch)
            print(f"   ✅ Batch {batch_num}/{num_batches + 1}: Added {len(batch)} chunks")
    else:
        # Small dataset, no batching needed
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


