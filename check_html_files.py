"""
Check if there are HTML files in the vector store
"""
import chromadb

PERSIST_DIRECTORY = "./data/cisco_products_custom_loader"

print("Checking for HTML files in vector store...\n")

client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = client.get_collection("cisco_products_custom_loader")

print(f"Total documents: {collection.count()}\n")

# Get all documents (this might be slow with 21k docs)
print("Sampling 100 documents to check file types...")
results = collection.get(limit=100, include=["metadatas"])

html_count = 0
pdf_count = 0
md_count = 0
html_sources = set()

for metadata in results['metadatas']:
    source = metadata.get('source', '')
    if '.html' in source:
        html_count += 1
        html_sources.add(source)
    elif '.pdf' in source:
        pdf_count += 1
    elif '.md' in source:
        md_count += 1

print(f"\nFile type breakdown (sample of 100):")
print(f"  PDF files: {pdf_count}")
print(f"  HTML files: {html_count}")
print(f"  MD files: {md_count}")

if html_sources:
    print(f"\n❌ Found {len(html_sources)} unique HTML sources:")
    for source in sorted(html_sources):
        print(f"  - {source}")
    print("\n⚠️  These HTML files should NOT be in the vector store!")
    print("   They likely came from a previous ingestion.")
else:
    print("\n✅ No HTML files found in sample")
