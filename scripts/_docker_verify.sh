#!/bin/bash
echo "=== knowledge_docs subfolders ==="
find /app/knowledge_docs -type d | sort

echo ""
echo "=== PDFs in knowledge_docs (should be NONE) ==="
PDF_COUNT=$(find /app/knowledge_docs -name "*.pdf" | wc -l)
echo "PDF count: $PDF_COUNT"

echo ""
echo "=== ontology configs (should be present) ==="
find /app/ontology -type f | sort

echo ""
echo "=== sdwan ontology first 3 lines ==="
head -3 /app/ontology/sdwan/guide_mappings.json

echo ""
echo "=== shared ontology first 3 lines ==="
head -3 /app/ontology/_shared/guide_mappings.json

echo ""
echo "=== app Python files ==="
ls /app/app/*.py | wc -l | xargs echo "Python file count:"

echo ""
echo "=== prompts ==="
ls /app/prompts/*.md 2>/dev/null | wc -l | xargs echo "Prompt file count:"

echo ""
echo "=== streamlit version ==="
python -c "import streamlit; print(streamlit.__version__)"

echo ""
echo "=== host mount check ==="
mount | grep -E "knowledge_docs|Denver2" || echo "CLEAN - no host mounts detected"

echo ""
echo "=== VERDICT ==="
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "PASS: knowledge_docs is empty (no PDFs leaked from host)"
else
    echo "FAIL: found $PDF_COUNT PDFs in knowledge_docs"
fi

if [ -f /app/ontology/sdwan/guide_mappings.json ]; then
    echo "PASS: ontology configs are baked into the image"
else
    echo "FAIL: ontology configs missing"
fi
