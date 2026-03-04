# Incremental Ingestion Guide

## Overview

The Bug Doctor app now supports **incremental ingestion** - only processing new or modified files instead of re-ingesting everything.

## How It Works

The system tracks file metadata (path, modification time, size) in `data/ingestion_metadata.json` and compares it against current files to detect:

- **New files**: Files added to `knowledge_docs/`
- **Modified files**: Existing files with changed content
- **Deleted files**: Files removed from `knowledge_docs/`

## Usage

### Quick Update (Recommended)

When you add or modify PDFs, just run:

```bash
python3 incremental_ingestion.py
```

This will:
- ✅ Detect what changed
- ✅ Remove old embeddings for modified/deleted files
- ✅ Add embeddings for new/modified files
- ✅ Preserve existing embeddings for unchanged files
- ✅ Update the tracking metadata

### Force Full Re-Ingestion

If you want to rebuild everything from scratch:

```bash
python3 incremental_ingestion.py --force
```

This will delete the vector store and re-ingest all files.

## Workflow

### Adding New Documents

1. **Add PDFs** to appropriate folder:
   ```bash
   cp new-guide.pdf knowledge_docs/sdwan/
   ```

2. **Run incremental ingestion**:
   ```bash
   python3 incremental_ingestion.py
   ```

3. **Restart the app**:
   ```bash
   python3 start.py
   ```

### Updating Existing Documents

Same workflow as above - the system auto-detects modifications.

### Output Example

```
=====================================
📚 Incremental Document Ingestion
=====================================

🔍 Scanning for documents...
   Found 28 files in knowledge_docs/

🔄 Detecting changes...
   New files: 2
   Modified files: 1
   Deleted files: 0

📂 Loading existing vector store...
   Current document count: 1247

♻️  Processing 1 modified files...
   🗑️  Removing documents from 1 files...
      Removed 45 chunks from old-guide.pdf

📥 Ingesting 3 files...
   Processing: new-guide-1.pdf
      ✅ Loaded 52 chunks
   Processing: new-guide-2.pdf
      ✅ Loaded 38 chunks
   Processing: old-guide.pdf
      ✅ Loaded 47 chunks

➕ Adding 137 chunks to vector store...

✅ Ingestion complete!
   Previous count: 1247
   Final count: 1294
   Change: +47
```

## Benefits

- ⚡ **Faster**: Only process what changed (seconds vs minutes)
- 💾 **Efficient**: Preserve existing embeddings
- 🔄 **Smart**: Auto-detect changes
- 📊 **Transparent**: Clear reporting of what changed

## Files

- `incremental_ingestion.py`: Main script
- `data/ingestion_metadata.json`: Tracking file (auto-generated)
- `data/cisco_products_custom_loader/`: Vector store (preserved)

## Comparison

### Old Method (`ingestion.py`)
```bash
python3 ingestion.py
# Re-ingests ALL files (~2-5 minutes)
# Deletes existing vector store
```

### New Method (`incremental_ingestion.py`)
```bash
python3 incremental_ingestion.py
# Only ingests changed files (~10-30 seconds)
# Preserves existing vector store
```

## Troubleshooting

### "No changes detected"
- ✅ This is good! Nothing to do.
- If you know files changed, check file timestamps

### "Could not remove [file]"
- Usually not critical - will re-add with new content
- Use `--force` if you want a clean rebuild

### Vector store corruption
```bash
# Force full rebuild
python3 incremental_ingestion.py --force
```

## Notes

- **Always restart the app** after ingestion to load new embeddings
- Metadata file is safe to delete (will trigger full re-ingestion)
- Both `ingestion.py` and `incremental_ingestion.py` work - use incremental for speed
