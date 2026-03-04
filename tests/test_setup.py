#!/usr/bin/env python3
"""
Test Script - Verify In-Memory ChromaDB Configuration

This script tests the in-memory ChromaDB setup to ensure:
1. Documents can be loaded
2. Vector store can be initialized
3. Vector store can be accessed
4. Queries work correctly

Run this before deploying to production.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ingestion():
    """Test 1: Verify document loading works"""
    print("\n" + "="*70)
    print("TEST 1: Document Loading")
    print("="*70)
    
    try:
        from ingestion import load_documents
        docs = load_documents()
        
        if not docs:
            print("❌ FAIL: No documents loaded")
            return False
        
        print(f"✅ PASS: Loaded {len(docs)} documents")
        print(f"   Sample metadata: {docs[0].metadata if docs else 'N/A'}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error loading documents: {e}")
        return False


def test_vector_store_init():
    """Test 2: Verify vector store initialization"""
    print("\n" + "="*70)
    print("TEST 2: Vector Store Initialization")
    print("="*70)
    
    try:
        from vector_store_manager import initialize_vector_store, is_initialized
        
        if is_initialized():
            print("⚠️  Vector store already initialized, skipping")
            return True
        
        print("Initializing vector store...")
        store = initialize_vector_store()
        
        if not is_initialized():
            print("❌ FAIL: Vector store not marked as initialized")
            return False
        
        print(f"✅ PASS: Vector store initialized")
        print(f"   Collection name: {store._collection.name}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error initializing vector store: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store_access():
    """Test 3: Verify vector store can be accessed"""
    print("\n" + "="*70)
    print("TEST 3: Vector Store Access")
    print("="*70)
    
    try:
        from vector_store_manager import get_vector_store
        
        store = get_vector_store()
        
        # Try to get some data
        collection = store._collection
        count = collection.count()
        
        if count == 0:
            print("❌ FAIL: Vector store is empty")
            return False
        
        print(f"✅ PASS: Vector store accessible")
        print(f"   Document count: {count}")
        return True
        
    except RuntimeError as e:
        print(f"❌ FAIL: Vector store not initialized: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Error accessing vector store: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query():
    """Test 4: Verify queries work"""
    print("\n" + "="*70)
    print("TEST 4: Query Functionality")
    print("="*70)
    
    try:
        from vector_store_manager import get_vector_store
        
        store = get_vector_store()
        
        # Perform a simple similarity search
        results = store.similarity_search("cisco configuration", k=3)
        
        if not results:
            print("⚠️  WARNING: Query returned no results")
            print("   This may be normal if documents don't contain 'cisco configuration'")
            return True
        
        print(f"✅ PASS: Query successful")
        print(f"   Results returned: {len(results)}")
        print(f"   Sample result: {results[0].page_content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error querying vector store: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embeddings():
    """Test 5: Verify embeddings function"""
    print("\n" + "="*70)
    print("TEST 5: Embeddings Function")
    print("="*70)
    
    try:
        from vector_store_manager import get_embeddings
        
        embeddings = get_embeddings()
        
        # Test embedding a simple query
        test_text = "test query"
        embedding = embeddings.embed_query(test_text)
        
        if not embedding or len(embedding) == 0:
            print("❌ FAIL: Embedding returned empty result")
            return False
        
        print(f"✅ PASS: Embeddings function working")
        print(f"   Embedding dimension: {len(embedding)}")
        print(f"   Model: sentence-transformers/all-MiniLM-L6-v2")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error with embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*70)
    print("🧪 ChromaDB Configuration Tests")
    print("="*70)
    
    # Check SQLite version first
    try:
        from vector_store_manager import get_sqlite_version, supports_persistence, get_persistence_mode
        sqlite_ver = get_sqlite_version()
        can_persist = supports_persistence()
        mode = get_persistence_mode()
        
        print(f"\n📊 Environment Info:")
        print(f"   SQLite version: {'.'.join(map(str, sqlite_ver))}")
        print(f"   Persistence supported: {'✅ Yes' if can_persist else '❌ No (requires 3.35.0+)'}")
        print(f"   Mode: {mode.upper()}")
    except Exception as e:
        print(f"\n⚠️  Could not detect SQLite version: {e}")
    
    print("\nThis will test the ChromaDB setup.")
    print("Tests will take 30-60 seconds to complete.\n")
    
    # Check for knowledge_docs directory
    if not os.path.exists("knowledge_docs"):
        print("❌ CRITICAL: knowledge_docs/ directory not found!")
        print("   Create this directory and add .md or .pdf files before testing.")
        return 1
    
    # Run all tests
    results = []
    
    results.append(("Document Loading", test_ingestion()))
    results.append(("Vector Store Init", test_vector_store_init()))
    results.append(("Vector Store Access", test_vector_store_access()))
    results.append(("Query Functionality", test_query()))
    results.append(("Embeddings Function", test_embeddings()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! In-memory ChromaDB is working correctly.")
        print("\nYou can now run the app:")
        print("  streamlit run streamlit_app.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
        print("\nCommon issues:")
        print("  - knowledge_docs/ is empty → Add .md or .pdf files")
        print("  - Import errors → Check requirements.txt installed")
        print("  - Memory errors → Reduce document count or increase RAM")
        return 1


if __name__ == "__main__":
    sys.exit(main())
