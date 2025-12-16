#!/bin/bash
# Automated MIDI Dataset Collection for Phase 2 Training
#
# This script downloads and organizes 1000+ MIDI files for training:
# - Lakh MIDI Dataset (Gospel, Jazz, Blues filtered)
# - MAESTRO Dataset (Classical piano)
# - Generated Gospel files (using Phase 1)
#
# Total: ~1000-1500 files, ~8GB download
#
# Usage: bash scripts/collect_midi_dataset.sh

set -e  # Exit on error

echo "🎵 MIDI Dataset Collection for Phase 2 Training"
echo "================================================"
echo ""

# Configuration
DATA_DIR="backend/data/midi_sources"
DOWNLOAD_DIR="${DATA_DIR}/downloads"
OUTPUT_DIR="${DATA_DIR}"

mkdir -p "${DOWNLOAD_DIR}"
mkdir -p "${OUTPUT_DIR}"/{gospel,jazz,blues,classical,neosoul}

echo "📂 Directories created:"
echo "   Downloads: ${DOWNLOAD_DIR}"
echo "   Output: ${OUTPUT_DIR}"
echo ""

# ============================================
# STEP 1: Download Lakh MIDI Dataset
# ============================================
echo "📥 STEP 1: Downloading Lakh MIDI Dataset (Matched)"
echo "   Size: ~2GB compressed, ~4GB extracted"
echo "   Files: 45,129 MIDI files"
echo ""

LAKH_URL="http://hog.ee.columbia.edu/craffel/lmd/lmd_matched.tar.gz"
LAKH_FILE="${DOWNLOAD_DIR}/lmd_matched.tar.gz"

if [ -f "${LAKH_FILE}" ]; then
    echo "   ✓ Already downloaded: ${LAKH_FILE}"
else
    echo "   Downloading from ${LAKH_URL}..."
    wget -O "${LAKH_FILE}" "${LAKH_URL}" || {
        echo "   ⚠️  Download failed. You can manually download from:"
        echo "      ${LAKH_URL}"
        echo "   Or skip Lakh and use only generated data."
    }
fi

# Extract Lakh
if [ -f "${LAKH_FILE}" ]; then
    echo "   Extracting Lakh dataset..."
    tar -xzf "${LAKH_FILE}" -C "${DOWNLOAD_DIR}/" || {
        echo "   ⚠️  Extraction failed"
    }
    echo "   ✓ Lakh dataset extracted"
else
    echo "   ⚠️  Skipping Lakh dataset (not downloaded)"
fi

echo ""

# ============================================
# STEP 2: Download MAESTRO Dataset
# ============================================
echo "📥 STEP 2: Downloading MAESTRO Dataset (Classical Piano)"
echo "   Size: ~4GB"
echo "   Files: 1,282 performances"
echo ""

MAESTRO_URL="https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip"
MAESTRO_FILE="${DOWNLOAD_DIR}/maestro-v3.0.0-midi.zip"

if [ -f "${MAESTRO_FILE}" ]; then
    echo "   ✓ Already downloaded: ${MAESTRO_FILE}"
else
    echo "   Downloading from ${MAESTRO_URL}..."
    wget -O "${MAESTRO_FILE}" "${MAESTRO_URL}" || {
        echo "   ⚠️  Download failed. You can manually download from:"
        echo "      ${MAESTRO_URL}"
    }
fi

# Extract MAESTRO
if [ -f "${MAESTRO_FILE}" ]; then
    echo "   Extracting MAESTRO dataset..."
    unzip -q "${MAESTRO_FILE}" -d "${DOWNLOAD_DIR}/" || {
        echo "   ⚠️  Extraction failed"
    }
    echo "   ✓ MAESTRO dataset extracted"
else
    echo "   ⚠️  Skipping MAESTRO dataset (not downloaded)"
fi

echo ""

# ============================================
# STEP 3: Filter Lakh by Genre
# ============================================
echo "🔍 STEP 3: Filtering Lakh dataset by genre"
echo ""

if [ -d "${DOWNLOAD_DIR}/lmd_matched" ]; then
    echo "   Running genre filter script..."
    cd backend
    python scripts/filter_lakh_by_genre.py \
        --input "${DOWNLOAD_DIR}/lmd_matched" \
        --output-dir "${OUTPUT_DIR}" \
        --gospel-count 200 \
        --jazz-count 150 \
        --blues-count 100 || {
        echo "   ⚠️  Genre filtering failed (script may not exist yet)"
        echo "   Continuing with manual organization..."
    }
    cd ..
else
    echo "   ⚠️  Lakh dataset not found, skipping genre filtering"
fi

echo ""

# ============================================
# STEP 4: Organize MAESTRO files
# ============================================
echo "📁 STEP 4: Organizing MAESTRO files"
echo ""

if [ -d "${DOWNLOAD_DIR}/maestro-v3.0.0" ]; then
    echo "   Copying Classical MIDI files..."

    # Copy first 200 MAESTRO files to classical directory
    find "${DOWNLOAD_DIR}/maestro-v3.0.0" -name "*.midi" -o -name "*.mid" | \
        head -200 | \
        xargs -I {} cp {} "${OUTPUT_DIR}/classical/"

    CLASSICAL_COUNT=$(find "${OUTPUT_DIR}/classical" -name "*.mid*" | wc -l)
    echo "   ✓ Copied ${CLASSICAL_COUNT} classical files"
else
    echo "   ⚠️  MAESTRO dataset not found"
fi

echo ""

# ============================================
# STEP 5: Generate synthetic Gospel data
# ============================================
echo "🤖 STEP 5: Generating synthetic Gospel MIDI with Phase 1"
echo ""

if [ -f "backend/scripts/generate_bootstrap_dataset.py" ]; then
    echo "   Running bootstrap generator..."
    cd backend
    python scripts/generate_bootstrap_dataset.py \
        --output "${OUTPUT_DIR}/gospel" \
        --count 250 || {
        echo "   ⚠️  Bootstrap generation failed (script may not exist yet)"
    }
    cd ..
else
    echo "   ⚠️  Bootstrap generator not found"
    echo "   Create backend/scripts/generate_bootstrap_dataset.py to generate synthetic data"
fi

echo ""

# ============================================
# STEP 6: Summary Statistics
# ============================================
echo "📊 DATASET COLLECTION SUMMARY"
echo "================================================"
echo ""

GOSPEL_COUNT=$(find "${OUTPUT_DIR}/gospel" -name "*.mid*" 2>/dev/null | wc -l | tr -d ' ')
JAZZ_COUNT=$(find "${OUTPUT_DIR}/jazz" -name "*.mid*" 2>/dev/null | wc -l | tr -d ' ')
BLUES_COUNT=$(find "${OUTPUT_DIR}/blues" -name "*.mid*" 2>/dev/null | wc -l | tr -d ' ')
CLASSICAL_COUNT=$(find "${OUTPUT_DIR}/classical" -name "*.mid*" 2>/dev/null | wc -l | tr -d ' ')
NEOSOUL_COUNT=$(find "${OUTPUT_DIR}/neosoul" -name "*.mid*" 2>/dev/null | wc -l | tr -d ' ')

TOTAL=$((GOSPEL_COUNT + JAZZ_COUNT + BLUES_COUNT + CLASSICAL_COUNT + NEOSOUL_COUNT))

echo "Genre Distribution:"
echo "   Gospel:     ${GOSPEL_COUNT} files (target: 500)"
echo "   Jazz:       ${JAZZ_COUNT} files (target: 250)"
echo "   Blues:      ${BLUES_COUNT} files (target: 200)"
echo "   Classical:  ${CLASSICAL_COUNT} files (target: 150)"
echo "   Neo-Soul:   ${NEOSOUL_COUNT} files (target: 100)"
echo ""
echo "   TOTAL:      ${TOTAL} files (target: 1000+)"
echo ""

if [ ${TOTAL} -ge 1000 ]; then
    echo "✅ SUCCESS! Dataset collection complete (${TOTAL} files)"
    echo ""
    echo "Next steps:"
    echo "   1. Run: python scripts/prepare_stage1_dataset.py"
    echo "   2. Run: python scripts/prepare_stage2_dataset.py"
    echo "   3. Run: python scripts/convert_tokens_to_text.py"
    echo "   4. Begin training: bash scripts/train_workflow_optimized.sh"
else
    echo "⚠️  PARTIAL SUCCESS: Collected ${TOTAL}/1000 files"
    echo ""
    echo "To reach 1000+ files:"
    echo "   1. Create generate_bootstrap_dataset.py (generates 250+ Gospel)"
    echo "   2. Create filter_lakh_by_genre.py (extracts 450+ from Lakh)"
    echo "   3. Manually add MIDI files to ${OUTPUT_DIR}/<genre>/"
    echo "   4. Download from FreeMIDI.org, BitMIDI.com, etc."
fi

echo ""
echo "🎉 Dataset collection script complete!"
