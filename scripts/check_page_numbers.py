"""
Check if page numbers are preserved in the vector store
"""
from vector_store_manager import initialize_vector_store

print("=" * 80)
print("CHECKING PAGE NUMBERS IN VECTOR STORE")
print("=" * 80)

# Initialize vector store
print("\nInitializing vector store...")
vectorstore = initialize_vector_store()

# Get a sample of documents
print("\nGetting sample documents...")
results = vectorstore.similarity_search("security configuration", k=10)

print(f"\nChecking {len(results)} sample documents:\n")
print("-" * 80)

page_count = 0
no_page_count = 0

for i, doc in enumerate(results, 1):
    source = doc.metadata.get('source', 'Unknown')
    page = doc.metadata.get('page')
    section = doc.metadata.get('section', 'N/A')
    
    # Extract just filename from path
    if '/' in source:
        filename = source.split('/')[-1]
    else:
        filename = source
    
    print(f"\nDocument {i}:")
    print(f"  Source: {filename}")
    print(f"  Page: {page if page is not None else 'NOT AVAILABLE'}")
    print(f"  Section: {section[:60]}..." if len(section) > 60 else f"  Section: {section}")
    print(f"  Content preview: {doc.page_content[:100]}...")
    
    if page is not None:
        page_count += 1
    else:
        no_page_count += 1

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Documents WITH page numbers: {page_count}/{len(results)}")
print(f"Documents WITHOUT page numbers: {no_page_count}/{len(results)}")

if page_count > 0:
    print("\n✅ SUCCESS: Page numbers ARE preserved in the vector store!")
else:
    print("\n❌ WARNING: No page numbers found in sample!")
