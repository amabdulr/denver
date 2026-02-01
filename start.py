#!/usr/bin/env python3
"""
Unified Startup Script for Denver App
Handles in-memory ChromaDB initialization and Streamlit launch

This script solves the SQLite 3.26.0 limitation by:
1. Pre-initializing the vector store before Streamlit starts
2. Keeping the vector store in memory via vector_store_manager
3. Starting Streamlit in the same process

Usage:
    python start.py
    
Note: The streamlit_app.py will also auto-initialize the vector store
      if it hasn't been initialized yet, so this script is optional but
      provides better startup feedback and error handling.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("="*70)
    print("🚀 Denver App - Unified Startup")
    print("="*70)
    print("\n⚠️  Running in IN-MEMORY mode (SQLite 3.26.0 compatibility)")
    print("   Vector store will be populated and kept in memory\n")
    
    # Step 1: Pre-initialize vector store (optional but provides better feedback)
    print("📚 Step 1: Pre-loading knowledge base...")
    print("-"*70)
    try:
        from vector_store_manager import initialize_vector_store, is_initialized
        if not is_initialized():
            initialize_vector_store()
        print("\n✅ Knowledge base loaded successfully!")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not pre-load knowledge base: {e}")
        print("   The app will attempt to load it on first request")
    
    # Step 2: Start Streamlit
    print("\n"+"="*70)
    print("🌐 Step 2: Starting Streamlit app...")
    print("="*70)
    print("\n💡 The vector store is now in memory and will remain available")
    print("   as long as this process runs.\n")
    
    # Import streamlit to run it programmatically
    from streamlit.web import cli as stcli
    
    # Set up arguments for streamlit
    sys.argv = [
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    
    # Run streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
