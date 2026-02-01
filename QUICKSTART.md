# Quick Start Guide - In-Memory ChromaDB Mode

## ⚠️ Important: SQLite 3.26.0 Compatibility

This project is configured for **in-memory ChromaDB** to work with SQLite 3.26.0 (ChromaDB requires 3.35+ for persistence).

## How to Run the App

### Method 1: Standard Streamlit (Recommended)
```bash
streamlit run streamlit_app.py
```

**What happens:**
- Streamlit starts immediately
- On first load, the app initializes the vector store (takes ~30-60 seconds)
- Knowledge base stays in memory as long as the app runs
- You'll see a loading spinner: "🔄 Loading knowledge base into memory..."

### Method 2: Using start.py (Optional)
```bash
python start.py
```

**What happens:**
- Pre-loads the knowledge base before Streamlit starts
- Better startup feedback and error handling
- Same end result as Method 1

### Method 3: Standalone Ingestion (For Testing)
```bash
python ingestion.py
```

**What happens:**
- Loads all documents and creates vector store
- **⚠️ Data is lost when the process exits!**
- Only useful for testing the ingestion pipeline

## How It Works

### Architecture
```
┌─────────────────────────────────────────────────┐
│  streamlit_app.py (Streamlit UI)               │
│  ├─ Initializes vector store on first load      │
│  └─ Calls vector_store_manager                  │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│  vector_store_manager.py (Singleton Manager)    │
│  ├─ Maintains ONE shared vector store instance  │
│  ├─ initialize_vector_store() - setup once      │
│  └─ get_vector_store() - get instance           │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│  ingestion.py (Document Loader)                 │
│  ├─ load_documents() - reads knowledge_docs/    │
│  └─ Processes MD/PDF files into chunks          │
└─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│  app_functions.py (RAG Logic)                   │
│  ├─ get_product_info() - RAG tool               │
│  └─ Uses shared vector store                    │
└─────────────────────────────────────────────────┘
```

### Key Files Modified

1. **`vector_store_manager.py`** (NEW)
   - Singleton pattern for shared vector store
   - `initialize_vector_store()` - loads documents once
   - `get_vector_store()` - access from anywhere

2. **`streamlit_app.py`** (MODIFIED)
   - Auto-initializes vector store on first load
   - Shows loading spinner with status

3. **`app_functions.py`** (MODIFIED)
   - Uses `get_vector_store()` instead of creating new instance
   - No more `persist_directory` parameter

4. **`ingestion.py`** (MODIFIED)
   - Exports `load_documents()` function
   - Can run standalone for testing
   - Simplified main block

5. **`start.py`** (NEW - OPTIONAL)
   - Pre-loads knowledge base before Streamlit
   - Better startup experience

## Troubleshooting

### "Vector store not initialized" Error
If you see this in `app_functions.py`:
- The app will auto-initialize on first use
- Check that `knowledge_docs/` directory exists
- Verify it contains `.md` or `.pdf` files

### Slow First Load
- First initialization takes 30-60 seconds
- This is normal - loading and embedding all documents
- Subsequent requests are fast (data in memory)

### Memory Usage
- Vector store stays in RAM (not saved to disk)
- Typical usage: 200-500 MB depending on document count
- If memory is an issue, reduce number of documents

### Data Loss on Restart
- **This is expected behavior!**
- In-memory mode = no persistence
- Knowledge base reloads on each app restart
- Use persistent ChromaDB if you upgrade SQLite to 3.35+

## Checking Your Setup

### Verify In-Memory Mode
```python
from vector_store_manager import is_initialized, get_vector_store

# Check if initialized
print(f"Initialized: {is_initialized()}")

# Get the store (will auto-initialize if needed)
store = get_vector_store()
print(f"Collection: {store._collection.name}")
```

### Test Ingestion
```bash
python ingestion.py
```
Should output:
```
======================================================================
🔄 ChromaDB In-Memory Ingestion
======================================================================

⚠️  WARNING: Running in IN-MEMORY mode - data will NOT persist
   SQLite 3.26.0 compatibility mode (ChromaDB requires 3.35+)

📚 Loading documents from knowledge_docs...
Reading file: knowledge_docs/9800/file1.md
...
✅ Document loading complete:
   Files processed: X
   Documents created: Y
```

## Production Deployment

For production on the enterprise Linux server:

1. **Just use:** `streamlit run streamlit_app.py`
2. App will auto-initialize on first request
3. Knowledge base stays loaded during the session
4. Each app restart reloads the knowledge base (30-60s delay)

### Optional: Reduce Startup Time
Consider pre-embedding documents and loading from pickle:
```python
# Save embeddings (run once)
import pickle
from ingestion import load_documents
docs = load_documents()
with open('docs_cache.pkl', 'wb') as f:
    pickle.dump(docs, f)

# Load embeddings (fast startup)
with open('docs_cache.pkl', 'rb') as f:
    docs = pickle.load(f)
```

## Migration Back to Persistent Mode

When SQLite is upgraded to 3.35+, revert to persistent mode:

1. In `vector_store_manager.py`:
   ```python
   _vector_store = Chroma.from_documents(
       collection_name="cisco_products_custom_loader",
       persist_directory="data/cisco_products_custom_loader",  # Add this
       embedding=embeddings,
       documents=documents,
   )
   ```

2. Remove auto-initialization from `streamlit_app.py`

3. Run ingestion once: `python ingestion.py`

4. Data now persists between restarts!

---

**Questions?** See [CHROMA_IN_MEMORY.md](CHROMA_IN_MEMORY.md) for detailed documentation.
