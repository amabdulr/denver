"""
Shared Vector Store Module
Provides singleton access to the ChromaDB vector store

This module automatically detects SQLite version and uses:
- Persistent mode (disk-backed) if SQLite >= 3.35.0
- In-memory mode if SQLite < 3.35.0

Usage:
    from vector_store_manager import get_vector_store, initialize_vector_store
    
    # Initialize once at startup
    initialize_vector_store()
    
    # Access anywhere in the app
    vectorstore = get_vector_store()
"""

import os
import sqlite3
from typing import Optional, Tuple
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Global singleton instance
_vector_store: Optional[Chroma] = None
_embeddings: Optional[HuggingFaceEmbeddings] = None
_persistence_mode: Optional[str] = None  # 'persistent' or 'in-memory'

# Configuration
PERSIST_DIRECTORY = "data/cisco_products_custom_loader"
MIN_SQLITE_VERSION = (3, 35, 0)


def get_sqlite_version() -> Tuple[int, int, int]:
    """
    Get the SQLite version as a tuple of (major, minor, patch).
    
    Returns:
        Tuple of (major, minor, patch) version numbers
    """
    version_string = sqlite3.sqlite_version
    parts = version_string.split('.')
    return tuple(int(p) for p in parts[:3])


def supports_persistence() -> bool:
    """
    Check if the current SQLite version supports ChromaDB persistence.
    
    Returns:
        True if SQLite >= 3.35.0, False otherwise
    """
    current_version = get_sqlite_version()
    return current_version >= MIN_SQLITE_VERSION


def get_persistence_mode() -> str:
    """
    Get the current persistence mode.
    
    Returns:
        'persistent' if using disk-backed storage, 'in-memory' otherwise
    """
    global _persistence_mode
    if _persistence_mode is None:
        _persistence_mode = 'persistent' if supports_persistence() else 'in-memory'
    return _persistence_mode


def get_embeddings() -> HuggingFaceEmbeddings:
    """Get or create the embeddings function"""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings


def initialize_vector_store() -> Chroma:
    """
    Initialize the vector store with knowledge documents.
    Automatically uses persistent or in-memory mode based on SQLite version.
    Should be called once at application startup.
    
    Returns:
        The initialized Chroma vector store
    """
    global _vector_store, _persistence_mode
    
    if _vector_store is not None:
        print("⚠️  Vector store already initialized, skipping re-initialization")
        return _vector_store
    
    # Check SQLite version and determine mode
    sqlite_version = get_sqlite_version()
    use_persistence = supports_persistence()
    mode = 'persistent' if use_persistence else 'in-memory'
    _persistence_mode = mode
    
    print(f"🔄 Initializing vector store...")
    print(f"   SQLite version: {'.'.join(map(str, sqlite_version))}")
    print(f"   Mode: {mode.upper()}")
    
    if not use_persistence:
        print(f"   ⚠️  SQLite < 3.35.0 - persistence disabled")
    
    embeddings = get_embeddings()
    
    # Check if we can load from existing persistent store
    if use_persistence and os.path.exists(PERSIST_DIRECTORY):
        print(f"   📂 Loading existing vector store from {PERSIST_DIRECTORY}...")
        try:
            _vector_store = Chroma(
                collection_name="cisco_products_custom_loader",
                persist_directory=PERSIST_DIRECTORY,
                embedding_function=embeddings,
            )
            doc_count = _vector_store._collection.count()
            print(f"✅ Loaded existing vector store with {doc_count} documents")
            return _vector_store
        except Exception as e:
            print(f"   ⚠️  Could not load existing store: {e}")
            print(f"   🗑️  Removing corrupted store and creating new one...")
            # Remove corrupted directory
            import shutil
            try:
                shutil.rmtree(PERSIST_DIRECTORY)
            except:
                pass
    
    # Load documents and create new vector store
    from ingestion import load_documents
    documents = load_documents()
    
    # Create vector store in batches to avoid ChromaDB limit (max ~5461)
    BATCH_SIZE = 5000
    
    if len(documents) > BATCH_SIZE:
        print(f"   Processing {len(documents)} documents in batches of {BATCH_SIZE}...")
        
        # Create with first batch
        first_batch = documents[:BATCH_SIZE]
        
        if use_persistence:
            _vector_store = Chroma.from_documents(
                collection_name="cisco_products_custom_loader",
                persist_directory=PERSIST_DIRECTORY,
                embedding=embeddings,
                documents=first_batch,
            )
        else:
            _vector_store = Chroma.from_documents(
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
            _vector_store.add_documents(batch)
            print(f"   ✅ Batch {batch_num}/{num_batches + 1}: Added {len(batch)} chunks")
        
        if use_persistence:
            print(f"✅ Created persistent vector store at {PERSIST_DIRECTORY}")
        else:
            print(f"✅ Created in-memory vector store")
    else:
        # Small dataset, no batching needed
        if use_persistence:
            _vector_store = Chroma.from_documents(
                collection_name="cisco_products_custom_loader",
                persist_directory=PERSIST_DIRECTORY,
                embedding=embeddings,
                documents=documents,
            )
            print(f"✅ Created persistent vector store at {PERSIST_DIRECTORY}")
        else:
            _vector_store = Chroma.from_documents(
                collection_name="cisco_products_custom_loader",
                embedding=embeddings,
                documents=documents,
            )
            print(f"✅ Created in-memory vector store")
    
    print(f"   Total documents: {len(documents)}")
    return _vector_store


def get_vector_store() -> Chroma:
    """
    Get the shared in-memory vector store.
    
    Returns:
        The Chroma vector store instance
        
    Raises:
        RuntimeError: If vector store hasn't been initialized yet
    """
    global _vector_store
    
    if _vector_store is None:
        raise RuntimeError(
            "Vector store not initialized! "
            "Call initialize_vector_store() first, typically at app startup."
        )
    
    return _vector_store


def is_initialized() -> bool:
    """Check if the vector store has been initialized"""
    return _vector_store is not None
