"""
Verification Script: Local LLM Integration into All 8 Genre Generators

Tests that all genre generators have successfully integrated LocalLLMGeneratorMixin
and can access local LLM capabilities.
"""

import sys
import inspect
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("LOCAL LLM INTEGRATION VERIFICATION")
print("=" * 80)
print()

# Import all genre generator services
try:
    from app.services.gospel_generator import gospel_generator_service
    from app.services.jazz_generator import jazz_generator_service
    from app.services.blues_generator import blues_generator_service
    from app.services.classical_generator import classical_generator_service
    from app.services.neosoul_generator import neosoul_generator_service
    from app.services.reggae_generator import reggae_generator_service
    from app.services.latin_generator import latin_generator_service
    from app.services.rnb_generator import rnb_generator_service
    from app.services.local_llm_generator_mixin import LocalLLMGeneratorMixin

    print("✅ All generator imports successful")
    print()
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test all generators
generators = {
    "Gospel": gospel_generator_service,
    "Jazz": jazz_generator_service,
    "Blues": blues_generator_service,
    "Classical": classical_generator_service,
    "Neo-Soul": neosoul_generator_service,
    "Reggae": reggae_generator_service,
    "Latin": latin_generator_service,
    "R&B": rnb_generator_service
}

print("GENERATOR VERIFICATION:")
print("-" * 80)

all_have_mixin = True
all_have_methods = True

for genre_name, service in generators.items():
    # Check if LocalLLMGeneratorMixin is in the class hierarchy
    has_mixin = isinstance(service, LocalLLMGeneratorMixin)

    # Check for key mixin methods
    has_generate_method = hasattr(service, '_generate_progression_with_local_llm')
    has_complexity_method = hasattr(service, '_estimate_complexity')
    has_stats_method = hasattr(service, 'get_llm_stats')
    has_enabled_flag = hasattr(service, '_local_llm_enabled')

    all_methods_present = all([
        has_generate_method,
        has_complexity_method,
        has_stats_method,
        has_enabled_flag
    ])

    # Print results
    status = "✅" if has_mixin and all_methods_present else "❌"
    print(f"{status} {genre_name:12} - Mixin: {has_mixin:5} | Methods: {all_methods_present:5}")

    if not has_mixin:
        all_have_mixin = False
    if not all_methods_present:
        all_have_methods = False

print("-" * 80)
print()

# Check multi-model service availability
try:
    from app.services.multi_model_service import multi_model_service, MLX_AVAILABLE
    print(f"MLX Available: {MLX_AVAILABLE}")
    print(f"Multi-Model Service Ready: {multi_model_service.is_available() if MLX_AVAILABLE else False}")
    print()
except Exception as e:
    print(f"⚠️  Multi-model service check: {e}")
    print()

# Final summary
print("=" * 80)
print("INTEGRATION SUMMARY:")
print("=" * 80)

if all_have_mixin and all_have_methods:
    print("✅ SUCCESS: All 8 generators have LocalLLMGeneratorMixin integrated")
    print("✅ All generators have access to zero-cost local LLM generation")
    print()
    print("Features now available:")
    print("  - Complexity-based routing (1-10 scale)")
    print("  - Automatic model selection (Phi-3.5 Mini / Llama 3.3 70B)")
    print("  - Gemini fallback for complex tasks")
    print("  - Cost tracking and savings reporting")
    print()
    print("Next steps:")
    print("  1. Test generation with local LLM (complexity 1-7)")
    print("  2. Compare quality: local LLM vs Gemini")
    print("  3. Measure cost savings")
    print("  4. Move to Day 3-4: ML features activation")
    sys.exit(0)
else:
    print("❌ FAILURE: Not all generators properly integrated")
    if not all_have_mixin:
        print("   - Some generators missing LocalLLMGeneratorMixin")
    if not all_have_methods:
        print("   - Some generators missing required methods")
    sys.exit(1)
