# Automatic SQLite Version Detection

## How It Works

The code now **automatically detects your SQLite version** and chooses the best mode:

```python
# In vector_store_manager.py

def supports_persistence() -> bool:
    """Check if SQLite >= 3.35.0"""
    current_version = get_sqlite_version()
    return current_version >= (3, 35, 0)
```

### On Your Local System (SQLite 3.35+)
```
📊 Environment Info:
   SQLite version: 3.45.0
   Persistence supported: ✅ Yes
   Mode: PERSISTENT

✅ Created persistent vector store at data/cisco_products_custom_loader
   Total documents: 150
   
➡️ Data WILL persist between restarts
➡️ Faster startup on subsequent runs (loads from disk)
➡️ Lower memory usage
```

### On Enterprise Server (SQLite 3.26.0)
```
📊 Environment Info:
   SQLite version: 3.26.0
   Persistence supported: ❌ No (requires 3.35.0+)
   Mode: IN-MEMORY

⚠️ SQLite < 3.35.0 - persistence disabled
✅ Created in-memory vector store
   Total documents: 150

➡️ Data will NOT persist between restarts
➡️ Slower startup (rebuilds each time)
➡️ Higher memory usage
```

## What Happens

### First Run (No existing data)
1. Detects SQLite version
2. Loads all documents from `knowledge_docs/`
3. Creates embeddings
4. **If SQLite 3.35+**: Saves to `data/cisco_products_custom_loader/`
5. **If SQLite < 3.35**: Keeps in memory only

### Subsequent Runs

**With SQLite 3.35+ (Persistent mode):**
```python
# Loads from disk - FAST! (~2-3 seconds)
📂 Loading existing vector store from data/cisco_products_custom_loader...
✅ Loaded existing vector store with 150 documents
```

**With SQLite 3.26.0 (In-memory mode):**
```python
# Rebuilds from scratch - SLOW (~30-60 seconds)
🔄 Initializing vector store...
⚠️ SQLite < 3.35.0 - persistence disabled
📚 Loading documents from knowledge_docs...
✅ Created in-memory vector store
```

## Benefits

✅ **Portable**: Works on both local (3.35+) and server (3.26.0)  
✅ **Automatic**: No manual configuration needed  
✅ **Optimal**: Uses persistence when available  
✅ **Safe**: Falls back gracefully when not  

## Code Flow

```
┌─────────────────────────────────────┐
│ initialize_vector_store()           │
└────────────┬────────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Get SQLite    │
     │ version       │
     └───────┬───────┘
             │
             ▼
       ┌─────────────┐
       │ >= 3.35.0?  │
       └──┬──────┬───┘
          │      │
    YES   │      │   NO
          ▼      ▼
   ┌──────────┐ ┌──────────┐
   │PERSISTENT│ │IN-MEMORY │
   └──────────┘ └──────────┘
          │      │
          ▼      ▼
   ┌──────────────────┐
   │ Existing data?   │
   └──┬──────────┬────┘
      │          │
    YES│        NO│
      ▼          ▼
   ┌────┐    ┌─────────┐
   │Load│    │Create   │
   │disk│    │from docs│
   └────┘    └─────────┘
```

## Testing

Check which mode your system uses:

```bash
python test_setup.py
```

Output shows:
- Current SQLite version
- Whether persistence is supported
- Which mode is active

## Manual Override (Optional)

If you want to force in-memory mode even with SQLite 3.35+:

```python
# In vector_store_manager.py
def supports_persistence() -> bool:
    return False  # Force in-memory mode
```

Or force persistent mode (will fail with old SQLite):

```python
def supports_persistence() -> bool:
    return True  # Force persistent mode (risky!)
```

## Files Changed

- ✅ **vector_store_manager.py** - Added SQLite version detection
- ✅ **streamlit_app.py** - Shows which mode is active
- ✅ **test_setup.py** - Displays SQLite version info

## Verification

Run your app and check the startup message:

**Local system:**
```
✅ Knowledge base loaded (persistent mode)
```

**Enterprise server:**
```
✅ Knowledge base loaded (in-memory mode)
ℹ️ Running in-memory mode due to SQLite version. 
   Data will not persist between restarts.
```

That's it! The code now adapts automatically to your environment.
