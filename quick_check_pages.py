"""
Quick script to check if page numbers exist in ChromaDB metadata
without loading the full embeddings model
"""
import chromadb
import os

PERSIST_DIRECTORY = "./data/cisco_products_custom_loader"

print("=" * 80)
print("QUICK PAGE NUMBER CHECK")
print("=" * 80)

if not os.path.exists(PERSIST_DIRECTORY):
    print(f"❌ Vector store not found at {PERSIST_DIRECTORY}")
    exit(1)

print(f"\n📂 Opening ChromaDB at {PERSIST_DIRECTORY}...")

# Connect to ChromaDB directly
client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = client.get_collection("cisco_products_custom_loader")

print(f"✅ Collection loaded: {collection.count()} documents\n")

# Get a sample of documents
print("📋 Sampling 10 random documents...\n")
results = collection.get(limit=10, include=["metadatas", "documents"])

found_page_numbers = 0
missing_page_numbers = 0

for i, metadata in enumerate(results['metadatas'], 1):
    doc_preview = results['documents'][i-1][:80] + "..." if len(results['documents'][i-1]) > 80 else results['documents'][i-1]
    
    source = metadata.get('source', 'Unknown')
    page = metadata.get('page', None)
    
    if page is not None:
        found_page_numbers += 1
        print(f"✅ Document {i}:")
        print(f"   Source: {source}")
        print(f"   Page: {page}")
        print(f"   Preview: {doc_preview}\n")
    else:
        missing_page_numbers += 1
        print(f"❌ Document {i}:")
        print(f"   Source: {source}")
        print(f"   Page: NOT FOUND")
        print(f"   Preview: {doc_preview}\n")

print("=" * 80)
print(f"SUMMARY:")
print(f"  Documents with page numbers: {found_page_numbers}/10")
print(f"  Documents without page numbers: {missing_page_numbers}/10")

if found_page_numbers == 10:
    print("  ✅ All sampled documents have page numbers!")
elif found_page_numbers > 0:
    print(f"  ⚠️  {missing_page_numbers} documents missing page numbers")
else:
    print("  ❌ No page numbers found in metadata")
print("=" * 80)
