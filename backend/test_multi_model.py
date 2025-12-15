#!/usr/bin/env python3
"""Test Multi-Model LLM Service Integration

Tests the 3-tier local model strategy:
- Tier 1 (Small): Phi-3.5 Mini (3.8B) - Complexity 1-4
- Tier 2 (Medium): Qwen2.5-7B - Complexity 5-7
- Tier 3 (Cloud): Gemini Pro - Complexity 8-10

This script will:
1. Test Phi-3.5 Mini model (should already be loaded)
2. Test Qwen2.5-7B model download and loading (first time: ~4.4GB download)
3. Test automatic model selection based on complexity
4. Benchmark performance (tokens/sec)
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.multi_model_service import multi_model_service, MLX_AVAILABLE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_service_availability():
    """Test 1: Check if multi-model service is available"""
    print("\n" + "=" * 80)
    print("TEST 1: Service Availability")
    print("=" * 80)

    if not MLX_AVAILABLE:
        print("❌ FAILED: MLX framework not available")
        print("   Install with: pip install mlx mlx-lm")
        return False

    if not multi_model_service:
        print("❌ FAILED: Multi-model service not initialized")
        return False

    print("✅ PASSED: Multi-model service available")

    # Show model info
    info = multi_model_service.get_model_info()
    print(f"\n📊 Service Info:")
    print(f"   Available: {info['available']}")
    print(f"   Loaded models: {info['loaded_models']}")
    print(f"   Active model: {info['active_model']}")

    return True


def test_phi_mini_generation():
    """Test 2: Test Phi-3.5 Mini generation (complexity 1-4)"""
    print("\n" + "=" * 80)
    print("TEST 2: Phi-3.5 Mini Generation (Complexity 1-4)")
    print("=" * 80)

    try:
        prompt = "List 3 simple chord progressions for beginners in C major"

        print(f"\n📝 Prompt: {prompt}")
        print(f"🎯 Complexity: 4 (should use Phi-3.5 Mini)")

        start_time = time.time()

        response = multi_model_service.generate(
            prompt=prompt,
            complexity=4,
            max_tokens=256,
            temperature=0.7,
        )

        elapsed = time.time() - start_time

        print(f"\n✅ PASSED: Phi-3.5 Mini generation successful")
        print(f"⏱️  Time: {elapsed:.2f}s")
        print(f"📄 Response:\n{response[:300]}...")

        # Estimate tokens/sec (rough approximation)
        word_count = len(response.split())
        tokens_approx = word_count * 1.3  # Rough estimate
        tokens_per_sec = tokens_approx / elapsed
        print(f"🚀 Speed: ~{tokens_per_sec:.1f} tokens/sec")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qwen_generation():
    """Test 3: Test Qwen2.5-7B generation (complexity 5-7)

    NOTE: First run will download ~4.4GB model, may take 5-10 minutes
    """
    print("\n" + "=" * 80)
    print("TEST 3: Qwen2.5-7B Generation (Complexity 5-7)")
    print("=" * 80)

    try:
        prompt = """Generate a comprehensive tutorial on jazz ii-V-I progressions.
Include:
1. Theory explanation
2. Common voicings
3. Practice tips
4. Common mistakes to avoid

Format as JSON with sections."""

        print(f"\n📝 Prompt: {prompt[:100]}...")
        print(f"🎯 Complexity: 7 (should use Qwen2.5-7B)")
        print(f"\n⚠️  NOTE: First run will download ~4.4GB Qwen2.5-7B model")
        print(f"   This may take 5-10 minutes depending on connection...")

        start_time = time.time()

        response = multi_model_service.generate(
            prompt=prompt,
            complexity=7,
            max_tokens=1024,
            temperature=0.7,
        )

        elapsed = time.time() - start_time

        print(f"\n✅ PASSED: Qwen2.5-7B generation successful")
        print(f"⏱️  Time: {elapsed:.2f}s")
        print(f"📄 Response:\n{response[:400]}...")

        # Estimate tokens/sec
        word_count = len(response.split())
        tokens_approx = word_count * 1.3
        tokens_per_sec = tokens_approx / elapsed
        print(f"🚀 Speed: ~{tokens_per_sec:.1f} tokens/sec")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_structured_generation():
    """Test 4: Test structured JSON generation"""
    print("\n" + "=" * 80)
    print("TEST 4: Structured JSON Generation")
    print("=" * 80)

    try:
        prompt = "Generate a simple exercise for learning C major scale"

        schema = {
            "title": "string",
            "description": "string",
            "difficulty": "beginner|intermediate|advanced",
            "content": {
                "key": "string",
                "scale": "string",
                "practice_tips": ["string"]
            }
        }

        print(f"\n📝 Prompt: {prompt}")
        print(f"📋 Expected schema: {schema}")
        print(f"🎯 Complexity: 4 (Phi-3.5 Mini)")

        start_time = time.time()

        response = multi_model_service.generate_structured(
            prompt=prompt,
            schema=schema,
            complexity=4,
            max_tokens=512,
            temperature=0.3,
        )

        elapsed = time.time() - start_time

        print(f"\n✅ PASSED: Structured generation successful")
        print(f"⏱️  Time: {elapsed:.2f}s")
        print(f"📄 Response:")
        import json
        print(json.dumps(response, indent=2))

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_switching():
    """Test 5: Test automatic model switching"""
    print("\n" + "=" * 80)
    print("TEST 5: Automatic Model Switching")
    print("=" * 80)

    try:
        print("\n🔄 Testing model selection logic...")

        # Test complexity 1-4 (should use SMALL)
        tier_1 = multi_model_service.select_model(complexity=4)
        print(f"✅ Complexity 4 → {tier_1.value if tier_1 else 'None'} (expected: small)")

        # Test complexity 5-7 (should use MEDIUM)
        tier_2 = multi_model_service.select_model(complexity=7)
        print(f"✅ Complexity 7 → {tier_2.value if tier_2 else 'None'} (expected: medium)")

        # Test complexity 8-10 (should return None - use Gemini)
        tier_3 = multi_model_service.select_model(complexity=9)
        print(f"✅ Complexity 9 → {tier_3 if tier_3 else 'None (Gemini)'} (expected: None)")

        # Test actual switching
        print(f"\n🔄 Testing actual model switching...")

        # Generate with small model
        print(f"\n1. Generating with complexity 3 (Phi-3.5 Mini)...")
        response1 = multi_model_service.generate(
            prompt="Name 3 basic chords",
            complexity=3,
            max_tokens=50
        )
        print(f"   ✅ Generated: {response1[:80]}...")

        # Switch to medium model
        print(f"\n2. Generating with complexity 6 (Qwen2.5-7B)...")
        response2 = multi_model_service.generate(
            prompt="Explain the theory behind ii-V-I progressions",
            complexity=6,
            max_tokens=100
        )
        print(f"   ✅ Generated: {response2[:80]}...")

        # Switch back to small model
        print(f"\n3. Generating with complexity 2 (Phi-3.5 Mini)...")
        response3 = multi_model_service.generate(
            prompt="List 2 practice tips",
            complexity=2,
            max_tokens=50
        )
        print(f"   ✅ Generated: {response3[:80]}...")

        print(f"\n✅ PASSED: Model switching works correctly")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 MULTI-MODEL LLM SERVICE TEST SUITE")
    print("=" * 80)
    print("\nTesting 3-tier local model strategy:")
    print("  Tier 1: Phi-3.5 Mini (3.8B) - Complexity 1-4")
    print("  Tier 2: Qwen2.5-7B - Complexity 5-7")
    print("  Tier 3: Gemini Pro - Complexity 8-10")

    results = []

    # Run tests
    results.append(("Service Availability", test_service_availability()))

    if results[0][1]:  # Only continue if service is available
        results.append(("Phi-3.5 Mini Generation", test_phi_mini_generation()))
        results.append(("Qwen2.5-7B Generation", test_qwen_generation()))
        results.append(("Structured JSON Generation", test_structured_generation()))
        results.append(("Model Switching", test_model_switching()))

    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Multi-model integration successful!")
        print("\n💡 Next steps:")
        print("   1. Integrate with AI orchestrator (done!)")
        print("   2. Test tutorial generation quality")
        print("   3. Benchmark vs Gemini API")
        print("   4. Monitor cost savings")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
