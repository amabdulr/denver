#!/usr/bin/env python3
"""
Incremental Ingestion for Vector Store
Only processes new or modified files, preserving existing embeddings

This script:
1. Tracks file metadata (path, timestamp) in a JSON file
2. Compares current files against tracked files
3. Only ingests files that are new or modified
4. Removes embeddings for deleted files
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Set, Tuple
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from ingestion import load_documents_from_path, get_all_document_paths

# Metadata file to track ingested files
METADATA_FILE = "data/ingestion_metadata.json"
PERSIST_DIRECTORY = "data/cisco_products_custom_loader"


def load_ingestion_metadata() -> Dict[str, dict]:
    """
    Load metadata about previously ingested files
    
    Returns:
        Dictionary mapping file paths to metadata (timestamp, size)
    """
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_ingestion_metadata(metadata: Dict[str, dict]):
    """Save ingestion metadata to file"""
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)


def get_file_info(file_path: str) -> dict:
    """Get file metadata for change detection"""
    stat = os.stat(file_path)
    return {
        'modified_time': stat.st_mtime,
        'size': stat.st_size,
        'last_check': datetime.now().isoformat()
    }


def detect_changes(current_files: Set[str], metadata: Dict[str, dict]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Detect which files are new, modified, or deleted
    
    Args:
        current_files: Set of current file paths
        metadata: Previously ingested file metadata
        
    Returns:
        Tuple of (new_files, modified_files, deleted_files)
    """
    previous_files = set(metadata.keys())
    
    # New files: in current but not in metadata
    new_files = current_files - previous_files
    
    # Deleted files: in metadata but not in current
    deleted_files = previous_files - current_files
    
    # Modified files: in both, but metadata changed
    modified_files = set()
    for file_path in current_files & previous_files:
        current_info = get_file_info(file_path)
        previous_info = metadata[file_path]
        
        # Check if modified time or size changed
        if (current_info['modified_time'] != previous_info['modified_time'] or
            current_info['size'] != previous_info['size']):
            modified_files.add(file_path)
    
    return new_files, modified_files, deleted_files


def remove_documents_by_source(vectorstore: Chroma, source_paths: List[str]):
    """
    Remove all documents from specific source files
    
    Args:
        vectorstore: The Chroma vector store
        source_paths: List of source file paths to remove
    """
    if not source_paths:
        return
    
    print(f"   🗑️  Removing documents from {len(source_paths)} files...")
    
    for source_path in source_paths:
        # Get the relative path as stored in metadata
        rel_path = os.path.relpath(source_path)
        
        # Query for documents with this source
        try:
            # Get all document IDs with this source
            collection = vectorstore._collection
            results = collection.get(
                where={"source": {"$eq": rel_path}}
            )
            
            if results and results['ids']:
                collection.delete(ids=results['ids'])
                print(f"      Removed {len(results['ids'])} chunks from {os.path.basename(source_path)}")
        except Exception as e:
            print(f"      ⚠️  Warning: Could not remove {source_path}: {e}")


def incremental_ingest(force_full: bool = False):
    """
    Perform incremental ingestion of documents
    
    Args:
        force_full: If True, re-ingest everything (ignore metadata)
    """
    print("="*70)
    print("📚 Incremental Document Ingestion")
    print("="*70)
    
    # Get current files
    print("\n🔍 Scanning for documents...")
    current_files = get_all_document_paths()
    print(f"   Found {len(current_files)} files in knowledge_docs/")
    
    # Load metadata
    metadata = load_ingestion_metadata() if not force_full else {}
    
    if force_full:
        print("\n⚠️  FORCE FULL INGESTION - Rebuilding entire vector store")
        if os.path.exists(PERSIST_DIRECTORY):
            shutil.rmtree(PERSIST_DIRECTORY)
        new_files = current_files
        modified_files = set()
        deleted_files = set()
    else:
        # Detect changes
        print("\n🔄 Detecting changes...")
        new_files, modified_files, deleted_files = detect_changes(current_files, metadata)
        
        print(f"   New files: {len(new_files)}")
        print(f"   Modified files: {len(modified_files)}")
        print(f"   Deleted files: {len(deleted_files)}")
    
    # Check if any work to do
    if not new_files and not modified_files and not deleted_files:
        print("\n✅ No changes detected - vector store is up to date!")
        return
    
    # Initialize embeddings
    print("\n🔧 Initializing embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Load or create vector store
    if os.path.exists(PERSIST_DIRECTORY) and not force_full:
        print(f"\n📂 Loading existing vector store from {PERSIST_DIRECTORY}...")
        vectorstore = Chroma(
            collection_name="cisco_products_custom_loader",
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings,
        )
        initial_count = vectorstore._collection.count()
        print(f"   Current document count: {initial_count}")
    else:
        print("\n🆕 Creating new vector store...")
        vectorstore = None
        initial_count = 0
    
    # Remove deleted files
    if deleted_files and vectorstore:
        print(f"\n🗑️  Processing {len(deleted_files)} deleted files...")
        remove_documents_by_source(vectorstore, list(deleted_files))
        for file_path in deleted_files:
            del metadata[file_path]
    
    # Process modified files (remove old, will re-add new)
    if modified_files and vectorstore:
        print(f"\n♻️  Processing {len(modified_files)} modified files...")
        remove_documents_by_source(vectorstore, list(modified_files))
    
    # Combine new and modified files to ingest
    files_to_ingest = new_files | modified_files
    
    if files_to_ingest:
        print(f"\n📥 Ingesting {len(files_to_ingest)} files...")
        
        # Load documents from files
        all_new_docs = []
        for file_path in sorted(files_to_ingest):
            print(f"\n   Processing: {os.path.basename(file_path)}")
            try:
                docs = load_documents_from_path(file_path)
                all_new_docs.extend(docs)
                print(f"      ✅ Loaded {len(docs)} chunks")
                
                # Update metadata
                metadata[file_path] = get_file_info(file_path)
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        # Add to vector store (in batches to avoid ChromaDB limit)
        if all_new_docs:
            BATCH_SIZE = 5000  # ChromaDB has a limit of ~5461, use 5000 to be safe
            print(f"\n➕ Adding {len(all_new_docs)} chunks to vector store...")
            
            if vectorstore is None:
                # Create new vector store with first batch
                first_batch = all_new_docs[:BATCH_SIZE]
                vectorstore = Chroma.from_documents(
                    collection_name="cisco_products_custom_loader",
                    persist_directory=PERSIST_DIRECTORY,
                    embedding=embeddings,
                    documents=first_batch,
                )
                print(f"   ✅ Created vector store with {len(first_batch)} chunks")
                
                # Add remaining batches
                remaining_docs = all_new_docs[BATCH_SIZE:]
                if remaining_docs:
                    print(f"   Adding remaining {len(remaining_docs)} chunks in batches...")
                    for i in range(0, len(remaining_docs), BATCH_SIZE):
                        batch = remaining_docs[i:i + BATCH_SIZE]
                        vectorstore.add_documents(batch)
                        print(f"   ✅ Added batch {i//BATCH_SIZE + 2}: {len(batch)} chunks")
            else:
                # Add to existing vector store in batches
                num_batches = (len(all_new_docs) + BATCH_SIZE - 1) // BATCH_SIZE
                print(f"   Processing {num_batches} batch(es)...")
                
                for i in range(0, len(all_new_docs), BATCH_SIZE):
                    batch = all_new_docs[i:i + BATCH_SIZE]
                    batch_num = i // BATCH_SIZE + 1
                    vectorstore.add_documents(batch)
                    print(f"   ✅ Batch {batch_num}/{num_batches}: Added {len(batch)} chunks")
    
    # Save metadata
    save_ingestion_metadata(metadata)
    
    # Final count
    if vectorstore:
        final_count = vectorstore._collection.count()
        print(f"\n✅ Ingestion complete!")
        print(f"   Previous count: {initial_count}")
        print(f"   Final count: {final_count}")
        print(f"   Change: {final_count - initial_count:+d}")
    
    print("\n" + "="*70)


def main():
    """Main entry point"""
    import sys
    
    # Check for --force flag
    force_full = "--force" in sys.argv or "-f" in sys.argv
    
    if force_full:
        print("\n⚠️  Force full ingestion requested")
        response = input("This will delete the existing vector store. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    incremental_ingest(force_full=force_full)


if __name__ == "__main__":
    main()
