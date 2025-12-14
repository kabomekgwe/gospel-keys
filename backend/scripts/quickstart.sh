#!/bin/bash
# Gospel Piano AI - Quick Start Script
# Complete workflow from zero to 10,000 MIDIs

set -e  # Exit on error

echo "=================================="
echo "🎹 Gospel Piano AI - Quick Start"
echo "=================================="
echo ""
echo "This script will guide you through:"
echo "  1. Dataset collection (YouTube)"
echo "  2. MLX model training"
echo "  3. Batch MIDI generation"
echo ""
echo "M4 Pro Detected: Using MLX optimization"
echo "=================================="
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 completed successfully"
    else
        echo "❌ $1 failed"
        exit 1
    fi
}

# Menu
echo "What would you like to do?"
echo ""
echo "1) Test YouTube search (30 seconds)"
echo "2) Collect 10 gospel MIDIs (test, ~15 min)"
echo "3) Collect 100 gospel MIDIs (full, ~2-3 hours)"
echo "4) Monitor dataset progress (real-time)"
echo "5) Validate collected MIDIs"
echo "6) Train MLX model (requires 100+ MIDIs, 2-4 hours)"
echo "7) Generate 100 test MIDIs (after training)"
echo "8) Generate 10,000 production MIDIs (after training)"
echo "9) Complete pipeline (all steps)"
echo ""
read -p "Enter choice [1-9]: " choice

case $choice in
    1)
        echo ""
        echo "🔍 Testing YouTube search..."
        ~/.local/bin/uv run python scripts/build_gospel_dataset.py \
            --query "kirk franklin piano tutorial" \
            --limit 5 \
            --test
        check_status "YouTube search test"
        ;;

    2)
        echo ""
        echo "📥 Collecting 10 gospel piano MIDIs (test)..."
        ~/.local/bin/uv run python scripts/build_gospel_dataset.py \
            --limit 10 \
            --output data/gospel_dataset &

        # Start monitor in background
        sleep 5
        ~/.local/bin/uv run python scripts/monitor_dataset_progress.py \
            --target 10
        check_status "Dataset collection (10 MIDIs)"
        ;;

    3)
        echo ""
        echo "📥 Collecting 100 gospel piano MIDIs..."
        echo "⏱️  This will take 2-3 hours. Monitor progress in another terminal:"
        echo "   ~/.local/bin/uv run python scripts/monitor_dataset_progress.py"
        echo ""
        read -p "Start collection? (y/n): " confirm

        if [ "$confirm" = "y" ]; then
            ~/.local/bin/uv run python scripts/build_gospel_dataset.py \
                --limit 100 \
                --output data/gospel_dataset
            check_status "Dataset collection (100 MIDIs)"
        fi
        ;;

    4)
        echo ""
        echo "📊 Starting real-time progress monitor..."
        echo "   (Press Ctrl+C to exit)"
        ~/.local/bin/uv run python scripts/monitor_dataset_progress.py \
            --target 100 \
            --refresh 2
        ;;

    5)
        echo ""
        echo "🔍 Validating collected MIDIs..."
        ~/.local/bin/uv run python scripts/validate_gospel_midis.py \
            --input data/gospel_dataset/validated \
            --report data/gospel_dataset/validation_report.md
        check_status "MIDI validation"
        ;;

    6)
        echo ""
        echo "🤖 Training MLX Gospel Model..."
        echo "⏱️  This will take 2-4 hours on M4 Pro"
        echo ""

        # Check if enough MIDIs collected
        midi_count=$(find data/gospel_dataset/validated -name "*.mid" 2>/dev/null | wc -l)
        echo "   MIDIs available: $midi_count"

        if [ "$midi_count" -lt 100 ]; then
            echo "❌ Need at least 100 MIDIs for training (have $midi_count)"
            echo "   Run option 3 first to collect dataset"
            exit 1
        fi

        read -p "Start training? (y/n): " confirm

        if [ "$confirm" = "y" ]; then
            ~/.local/bin/uv run python scripts/train_mlx_gospel.py \
                --midi-dir data/gospel_dataset/validated \
                --epochs 10 \
                --batch-size 8
            check_status "MLX model training"
        fi
        ;;

    7)
        echo ""
        echo "🎹 Generating 100 test MIDIs..."

        # Check if model exists
        if [ ! -d "checkpoints/mlx-gospel/best" ]; then
            echo "❌ No trained model found. Run option 6 first."
            exit 1
        fi

        ~/.local/bin/uv run python scripts/generate_gospel_batch.py \
            --count 100 \
            --checkpoint checkpoints/mlx-gospel/best \
            --output output/gospel_test
        check_status "Test MIDI generation"
        ;;

    8)
        echo ""
        echo "🚀 Generating 10,000 production MIDIs..."
        echo "⏱️  This will take ~90 minutes on M4 Pro"
        echo ""

        # Check if model exists
        if [ ! -d "checkpoints/mlx-gospel/best" ]; then
            echo "❌ No trained model found. Run option 6 first."
            exit 1
        fi

        read -p "Start generation? (y/n): " confirm

        if [ "$confirm" = "y" ]; then
            ~/.local/bin/uv run python scripts/generate_gospel_batch.py \
                --count 10000 \
                --checkpoint checkpoints/mlx-gospel/best \
                --output output/gospel_production_10k
            check_status "Production MIDI generation"
        fi
        ;;

    9)
        echo ""
        echo "🔄 Running complete pipeline..."
        echo "   This will:"
        echo "   1. Collect 100 gospel MIDIs (2-3 hours)"
        echo "   2. Train MLX model (2-4 hours)"
        echo "   3. Generate 10,000 MIDIs (90 min)"
        echo "   Total time: ~6-8 hours"
        echo ""
        read -p "Start complete pipeline? (y/n): " confirm

        if [ "$confirm" = "y" ]; then
            # Step 1: Dataset collection
            echo ""
            echo "📥 Step 1/3: Collecting dataset..."
            ~/.local/bin/uv run python scripts/build_gospel_dataset.py \
                --limit 100 \
                --output data/gospel_dataset
            check_status "Dataset collection"

            # Step 2: Training
            echo ""
            echo "🤖 Step 2/3: Training MLX model..."
            ~/.local/bin/uv run python scripts/train_mlx_gospel.py \
                --midi-dir data/gospel_dataset/validated \
                --epochs 10 \
                --batch-size 8
            check_status "Model training"

            # Step 3: Generation
            echo ""
            echo "🎹 Step 3/3: Generating 10,000 MIDIs..."
            ~/.local/bin/uv run python scripts/generate_gospel_batch.py \
                --count 10000 \
                --checkpoint checkpoints/mlx-gospel/best \
                --output output/gospel_production_10k
            check_status "MIDI generation"

            echo ""
            echo "🎉 COMPLETE PIPELINE FINISHED!"
            echo "   Output: output/gospel_production_10k/"
        fi
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "✅ Done!"
echo "=================================="
echo ""
echo "📚 Next steps and documentation:"
echo "   - Complete guide: backend/MLX_GOSPEL_COMPLETE_GUIDE.md"
echo "   - Dataset guide: backend/data/DATASET_README.md"
echo ""
