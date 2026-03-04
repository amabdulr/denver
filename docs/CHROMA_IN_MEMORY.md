# ChromaDB In-Memory Configuration

## Environment Constraint

This project runs on an **enterprise Linux server with SQLite 3.26.0**, which is too old for ChromaDB's persistence features.

- **ChromaDB requires**: SQLite >= 3.35.0 for disk-based persistence
- **System has**: SQLite 3.26.0 (cannot be upgraded)
- **Solution**: Use in-memory ChromaDB (non-persistent)

## What This Means

### ⚠️ Data Does NOT Persist
- Vector embeddings are stored in RAM only
- Data is **lost when the process ends**
- You must re-run ingestion before starting the app each time

### Modified Files
1. **`app_functions.py`** - Removed `persist_directory` parameter
2. **`ingestion.py`** - Configured for in-memory operation

## Usage Workflow

### Option 1: Two-Step Process (Quick Testing)
```bash
# Step 1: Run ingestion (builds in-memory vector store)
python ingestion.py

# Step 2: IMMEDIATELY run the app (before ingestion process exits)
# Open new terminal while ingestion is still running
streamlit run streamlit_app.py
```

⚠️ **Problem**: This won't work because ingestion exits before the app starts!

### Option 2: Combined Process (Recommended)
Create a startup script that runs both:

```python
# startup.py
import subprocess
import threading
import time

def run_ingestion():
    """Run ingestion in the main thread"""
    import ingestion
    print("Ingestion complete - vector store ready in memory")

def run_streamlit():
    """Run streamlit after a delay"""
    time.sleep(5)  # Wait for ingestion to complete
    subprocess.run(["streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    # Run ingestion first
    run_ingestion()
    
    # Then start streamlit
    run_streamlit()
```

### Option 3: Pre-load on App Startup
Modify `streamlit_app.py` to run ingestion on first load:

```python
# In streamlit_app.py
if 'vector_store_loaded' not in st.session_state:
    with st.spinner("Loading knowledge base..."):
        import ingestion
        ingestion.main()  # Run ingestion
        st.session_state.vector_store_loaded = True
```

## Technical Details

### Before (Disk-Backed)
```python
vectorstore = Chroma(
    collection_name="cisco_products_custom_loader",
    persist_directory="data/cisco_products_custom_loader",  # ❌ Requires SQLite 3.35+
    embedding_function=embeddings,
)
```

### After (In-Memory)
```python
vectorstore = Chroma(
    collection_name="cisco_products_custom_loader",
    # No persist_directory = in-memory mode ✓
    embedding_function=embeddings,
)
```

## Considerations

### Advantages
✅ Compatible with SQLite 3.26.0  
✅ No disk I/O overhead  
✅ Faster queries (RAM access)  
✅ No database file corruption issues  

### Disadvantages
❌ Data lost on restart  
❌ Must re-ingest on each startup  
❌ Higher memory usage  
❌ Slower startup time  

## Alternative Solutions (If Possible)

1. **Use Docker** - Run in container with newer SQLite
2. **Use DuckDB backend** - ChromaDB supports DuckDB (check version requirements)
3. **Use different vector DB** - FAISS, Qdrant, Weaviate (if they don't have SQLite deps)
4. **Build SQLite from source** - Install SQLite 3.35+ to user directory

## Verification

Check your ChromaDB is running in-memory mode:
```python
import chromadb

# This should work (in-memory)
client = chromadb.Client()

# This will fail with old SQLite (disk-backed)
# client = chromadb.PersistentClient(path="./data")
```

## Questions?

If you see errors like:
- `"RuntimeError: Your system has an unsupported version of sqlite3"`
- `"sqlite3.OperationalError: near 'GENERATED': syntax error"`

These indicate SQLite version issues - confirm you're using in-memory mode without `persist_directory`.
