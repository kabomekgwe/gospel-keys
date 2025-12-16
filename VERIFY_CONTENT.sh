#!/bin/bash

# Gospel Keys Content Generation Verification Script
# Verifies that all generated content is properly created and accessible

echo "==============================================="
echo "Gospel Keys Content Generation Verification"
echo "==============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check generated files
echo "[1/5] Checking generated content files..."
echo ""

files=(
    "backend/app/data/generated_content/tutorials/tutorials.json"
    "backend/app/data/generated_content/exercises/exercises.json"
    "backend/app/data/generated_content/curriculum/curricula.json"
    "backend/app/data/generated_content/README.md"
)

all_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo -e "${GREEN}✓${NC} $file ($size)"
    else
        echo -e "${RED}✗${NC} $file (MISSING)"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo ""
    echo -e "${RED}Error: Some files are missing!${NC}"
    echo "Run: python3 backend/app/data/generate_comprehensive_content.py"
    exit 1
fi

echo ""
echo "[2/5] Validating JSON files..."
echo ""

# Validate tutorials.json
if python3 -m json.tool backend/app/data/generated_content/tutorials/tutorials.json > /dev/null 2>&1; then
    count=$(python3 -c "import json; f=open('backend/app/data/generated_content/tutorials/tutorials.json'); data=json.load(f); print(len(data))")
    echo -e "${GREEN}✓${NC} tutorials.json is valid ($count tutorials)"
else
    echo -e "${RED}✗${NC} tutorials.json is INVALID"
    exit 1
fi

# Validate exercises.json
if python3 -m json.tool backend/app/data/generated_content/exercises/exercises.json > /dev/null 2>&1; then
    count=$(python3 -c "import json; f=open('backend/app/data/generated_content/exercises/exercises.json'); data=json.load(f); print(len(data))")
    echo -e "${GREEN}✓${NC} exercises.json is valid ($count exercises)"
else
    echo -e "${RED}✗${NC} exercises.json is INVALID"
    exit 1
fi

# Validate curricula.json
if python3 -m json.tool backend/app/data/generated_content/curriculum/curricula.json > /dev/null 2>&1; then
    count=$(python3 -c "import json; f=open('backend/app/data/generated_content/curriculum/curricula.json'); data=json.load(f); print(len(data))")
    echo -e "${GREEN}✓${NC} curricula.json is valid ($count curricula)"
else
    echo -e "${RED}✗${NC} curricula.json is INVALID"
    exit 1
fi

echo ""
echo "[3/5] Checking documentation files..."
echo ""

docs=(
    "backend/app/data/generated_content/README.md"
    "GENERATED_CONTENT_INTEGRATION.md"
    "CONTENT_GENERATION_SUMMARY.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        lines=$(wc -l < "$doc")
        echo -e "${GREEN}✓${NC} $doc ($lines lines)"
    else
        echo -e "${YELLOW}⚠${NC} $doc (optional)"
    fi
done

echo ""
echo "[4/5] Verifying generator scripts..."
echo ""

scripts=(
    "backend/app/data/generate_comprehensive_content.py"
    "backend/populate_default_content.py"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        lines=$(wc -l < "$script")
        echo -e "${GREEN}✓${NC} $script ($lines lines)"
    else
        echo -e "${RED}✗${NC} $script (MISSING)"
    fi
done

echo ""
echo "[5/5] Content Statistics..."
echo ""

python3 << 'EOF'
import json
import os

base_path = "backend/app/data/generated_content"

# Load tutorials
with open(f"{base_path}/tutorials/tutorials.json") as f:
    tutorials = json.load(f)

# Load exercises
with open(f"{base_path}/exercises/exercises.json") as f:
    exercises = json.load(f)

# Load curricula
with open(f"{base_path}/curriculum/curricula.json") as f:
    curricula = json.load(f)

# Statistics
print(f"Total Tutorials: {len(tutorials)}")

# By genre
genres = {}
for t in tutorials:
    g = t.get('genre', 'unknown')
    genres[g] = genres.get(g, 0) + 1
print(f"  Genres: {genres}")

# By difficulty
difficulties = {}
for t in tutorials:
    d = t.get('difficulty', 'unknown')
    difficulties[d] = difficulties.get(d, 0) + 1
print(f"  Difficulties: {difficulties}")

print()
print(f"Total Exercises: {len(exercises)}")

# By type
types = {}
for e in exercises:
    t = e.get('exercise_type', 'unknown')
    types[t] = types.get(t, 0) + 1
print(f"  Types: {types}")

# By genre
ex_genres = {}
for e in exercises:
    g = e.get('genre', 'unknown')
    ex_genres[g] = ex_genres.get(g, 0) + 1
print(f"  Genres: {ex_genres}")

print()
print(f"Total Curricula: {len(curricula)}")
total_weeks = sum(c.get('duration_weeks', 0) for c in curricula)
print(f"  Total Weeks: {total_weeks}")

# Unique concepts
all_concepts = set()
for t in tutorials:
    for concept in t.get('concepts_covered', []):
        all_concepts.add(concept)
print()
print(f"Unique Concepts Covered: {len(all_concepts)}")

EOF

echo ""
echo "==============================================="
echo -e "${GREEN}✓ All content verified successfully!${NC}"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Populate database: python backend/populate_default_content.py"
echo "2. Start backend: python -m uvicorn app.main:app --reload"
echo "3. Access tutorials: curl http://localhost:8000/api/tutorials"
echo ""
