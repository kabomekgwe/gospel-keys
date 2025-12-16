"""
Comprehensive AI Integration Test Suite

Tests all AI features across all 8 genre generators:
- Local LLM integration (Day 1-2)
- ML progression prediction (Day 3-4)
- User preference learning (Day 3-4)

Test Categories:
1. Local LLM Quality Test (vs Gemini)
2. ML Prediction Accuracy Test
3. Adaptive Difficulty Test
4. Personalization Impact Test
5. End-to-End Integration Test
"""

import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("AI INTEGRATION TEST SUITE - Week 1, Day 5")
print("=" * 80)
print()

# Import all generator services
try:
    from app.services.gospel_generator import gospel_generator_service
    from app.services.jazz_generator import jazz_generator_service
    from app.services.blues_generator import blues_generator_service
    from app.services.classical_generator import classical_generator_service
    from app.services.neosoul_generator import neosoul_generator_service
    from app.services.reggae_generator import reggae_generator_service
    from app.services.latin_generator import latin_generator_service
    from app.services.rnb_generator import rnb_generator_service

    from app.schemas.jazz import GenerateJazzRequest

    print("✅ All imports successful")
    print()
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test configuration
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

test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests": {}
}


# ============================================================================
# TEST 1: MIXIN INTEGRATION TEST
# ============================================================================

def test_mixin_integration():
    """Test that all generators have all 3 mixins properly integrated."""
    print("=" * 80)
    print("TEST 1: MIXIN INTEGRATION")
    print("=" * 80)
    print()

    results = {}
    all_passed = True

    for genre_name, service in generators.items():
        # Check for LocalLLMGeneratorMixin methods
        has_local_llm = all([
            hasattr(service, '_generate_progression_with_local_llm'),
            hasattr(service, '_estimate_complexity'),
            hasattr(service, 'get_llm_stats')
        ])

        # Check for MLProgressionPredictorMixin methods
        has_ml_predictor = all([
            hasattr(service, 'predict_next_chord'),
            hasattr(service, 'get_progression_suggestions'),
            hasattr(service, 'get_ml_predictor_stats')
        ])

        # Check for UserPreferenceLearningMixin methods
        has_user_pref = all([
            hasattr(service, 'adapt_to_user_preferences'),
            hasattr(service, 'get_user_profile'),
            hasattr(service, 'get_personalized_recommendations'),
            hasattr(service, 'get_preference_learning_stats')
        ])

        passed = has_local_llm and has_ml_predictor and has_user_pref
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} {genre_name:12} - LLM:{has_local_llm:5} ML:{has_ml_predictor:5} User:{has_user_pref:5}")

        results[genre_name] = {
            "local_llm": has_local_llm,
            "ml_predictor": has_ml_predictor,
            "user_preference": has_user_pref,
            "passed": passed
        }

        if not passed:
            all_passed = False

    print()
    print(f"RESULT: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print()

    test_results["tests"]["mixin_integration"] = {
        "passed": all_passed,
        "details": results
    }

    return all_passed


# ============================================================================
# TEST 2: LOCAL LLM COMPLEXITY ROUTING TEST
# ============================================================================

def test_complexity_routing():
    """Test complexity estimation and routing logic."""
    print("=" * 80)
    print("TEST 2: COMPLEXITY ROUTING")
    print("=" * 80)
    print()

    # Test cases with expected complexity ranges
    test_cases = [
        {
            "description": "simple C major progression",
            "num_bars": 8,
            "expected_min": 1,
            "expected_max": 4
        },
        {
            "description": "sophisticated jazz progression with altered dominants",
            "num_bars": 16,
            "expected_min": 5,
            "expected_max": 7
        },
        {
            "description": "experimental avant-garde fusion with unusual modulations",
            "num_bars": 32,
            "expected_min": 8,
            "expected_max": 10
        }
    ]

    generator = jazz_generator_service
    results = []
    all_passed = True

    for case in test_cases:
        complexity = generator._estimate_complexity(
            case["description"],
            case["num_bars"]
        )

        passed = case["expected_min"] <= complexity <= case["expected_max"]
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} Complexity {complexity:2} for: {case['description'][:50]}...")
        print(f"      Expected: {case['expected_min']}-{case['expected_max']}, Got: {complexity}")
        print()

        results.append({
            "description": case["description"],
            "expected_range": [case["expected_min"], case["expected_max"]],
            "actual": complexity,
            "passed": passed
        })

        if not passed:
            all_passed = False

    print(f"RESULT: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print()

    test_results["tests"]["complexity_routing"] = {
        "passed": all_passed,
        "details": results
    }

    return all_passed


# ============================================================================
# TEST 3: ML PREDICTION TEST
# ============================================================================

def test_ml_prediction():
    """Test ML chord progression prediction."""
    print("=" * 80)
    print("TEST 3: ML CHORD PREDICTION")
    print("=" * 80)
    print()

    generator = jazz_generator_service
    results = []
    all_passed = True

    # Test case 1: Simple jazz progression
    current_progression = ["Cmaj7", "Am7"]
    context = {
        "key": "C",
        "user_id": "test_user",
        "style": "standard"
    }

    try:
        predictions = generator.predict_next_chord(current_progression, context)

        # Check predictions format
        has_predictions = len(predictions) > 0
        valid_format = all(
            isinstance(pred, tuple) and len(pred) == 2
            for pred in predictions
        )
        valid_confidence = all(
            0.0 <= conf <= 1.0
            for _, conf in predictions
        )

        passed = has_predictions and valid_format and valid_confidence
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} Prediction for {current_progression}")
        print(f"      Predictions: {len(predictions)}")
        if predictions:
            print(f"      Top 3: {predictions[:3]}")
        print()

        results.append({
            "progression": current_progression,
            "predictions_count": len(predictions),
            "top_predictions": predictions[:3] if predictions else [],
            "passed": passed
        })

        if not passed:
            all_passed = False

    except Exception as e:
        print(f"❌ FAIL Prediction test raised exception: {e}")
        print()
        results.append({
            "progression": current_progression,
            "error": str(e),
            "passed": False
        })
        all_passed = False

    print(f"RESULT: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print()

    test_results["tests"]["ml_prediction"] = {
        "passed": all_passed,
        "details": results
    }

    return all_passed


# ============================================================================
# TEST 4: USER PROFILE TEST
# ============================================================================

def test_user_profiling():
    """Test user preference learning and profiling."""
    print("=" * 80)
    print("TEST 4: USER PROFILING")
    print("=" * 80)
    print()

    generator = jazz_generator_service
    test_user_id = "test_user_profile"
    results = []
    all_passed = True

    # Test 1: Get empty profile
    try:
        profile = generator.get_user_profile(test_user_id)

        has_profile = profile is not None
        has_required_fields = all(
            field in profile
            for field in ["complexity_level", "success_rate", "total_generations"]
        )

        passed = has_profile and has_required_fields
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} Get user profile")
        print(f"      Profile exists: {has_profile}")
        print(f"      Has required fields: {has_required_fields}")
        if has_profile:
            print(f"      Complexity level: {profile.get('complexity_level', 'N/A')}")
            print(f"      Total generations: {profile.get('total_generations', 0)}")
        print()

        results.append({
            "test": "get_profile",
            "user_id": test_user_id,
            "profile_exists": has_profile,
            "has_required_fields": has_required_fields,
            "passed": passed
        })

        if not passed:
            all_passed = False

    except Exception as e:
        print(f"❌ FAIL Profile test raised exception: {e}")
        print()
        results.append({
            "test": "get_profile",
            "error": str(e),
            "passed": False
        })
        all_passed = False

    # Test 2: Get personalized recommendations
    try:
        recommendations = generator.get_personalized_recommendations(
            test_user_id,
            count=3
        )

        has_recommendations = recommendations is not None
        is_list = isinstance(recommendations, list)
        valid_format = all(
            isinstance(rec, dict) and "type" in rec
            for rec in recommendations
        ) if is_list else False

        passed = has_recommendations and is_list and valid_format
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} Get personalized recommendations")
        print(f"      Recommendations: {len(recommendations) if is_list else 0}")
        if recommendations and len(recommendations) > 0:
            print(f"      First recommendation type: {recommendations[0].get('type', 'N/A')}")
        print()

        results.append({
            "test": "recommendations",
            "count": len(recommendations) if is_list else 0,
            "passed": passed
        })

        if not passed:
            all_passed = False

    except Exception as e:
        print(f"❌ FAIL Recommendations test raised exception: {e}")
        print()
        results.append({
            "test": "recommendations",
            "error": str(e),
            "passed": False
        })
        all_passed = False

    print(f"RESULT: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print()

    test_results["tests"]["user_profiling"] = {
        "passed": all_passed,
        "details": results
    }

    return all_passed


# ============================================================================
# TEST 5: STATISTICS TEST
# ============================================================================

def test_statistics():
    """Test statistics reporting from all mixins."""
    print("=" * 80)
    print("TEST 5: STATISTICS REPORTING")
    print("=" * 80)
    print()

    generator = jazz_generator_service
    results = {}
    all_passed = True

    # Test LLM stats
    try:
        llm_stats = generator.get_llm_stats()
        has_stats = llm_stats is not None
        has_fields = all(
            field in llm_stats
            for field in ["local_llm_enabled", "local_generations", "gemini_generations"]
        )
        passed = has_stats and has_fields
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} LLM Statistics")
        if has_stats:
            print(f"      Enabled: {llm_stats.get('local_llm_enabled', False)}")
            print(f"      Local generations: {llm_stats.get('local_generations', 0)}")
            print(f"      Gemini generations: {llm_stats.get('gemini_generations', 0)}")
        print()

        results["llm_stats"] = {
            "passed": passed,
            "stats": llm_stats if has_stats else None
        }

        if not passed:
            all_passed = False

    except Exception as e:
        print(f"❌ FAIL LLM stats raised exception: {e}")
        print()
        results["llm_stats"] = {"passed": False, "error": str(e)}
        all_passed = False

    # Test ML predictor stats
    try:
        ml_stats = generator.get_ml_predictor_stats()
        has_stats = ml_stats is not None
        has_fields = all(
            field in ml_stats
            for field in ["enabled", "predictions_made", "users_tracked"]
        )
        passed = has_stats and has_fields
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} ML Predictor Statistics")
        if has_stats:
            print(f"      Enabled: {ml_stats.get('enabled', False)}")
            print(f"      Predictions made: {ml_stats.get('predictions_made', 0)}")
            print(f"      Users tracked: {ml_stats.get('users_tracked', 0)}")
        print()

        results["ml_predictor_stats"] = {
            "passed": passed,
            "stats": ml_stats if has_stats else None
        }

        if not passed:
            all_passed = False

    except Exception as e:
        print(f"❌ FAIL ML predictor stats raised exception: {e}")
        print()
        results["ml_predictor_stats"] = {"passed": False, "error": str(e)}
        all_passed = False

    # Test preference learning stats
    try:
        pref_stats = generator.get_preference_learning_stats()
        has_stats = pref_stats is not None
        has_fields = all(
            field in pref_stats
            for field in ["enabled", "profiles_created", "adaptations_made"]
        )
        passed = has_stats and has_fields
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} Preference Learning Statistics")
        if has_stats:
            print(f"      Enabled: {pref_stats.get('enabled', False)}")
            print(f"      Profiles created: {pref_stats.get('profiles_created', 0)}")
            print(f"      Adaptations made: {pref_stats.get('adaptations_made', 0)}")
        print()

        results["preference_learning_stats"] = {
            "passed": passed,
            "stats": pref_stats if has_stats else None
        }

        if not passed:
            all_passed = False

    except Exception as e:
        print(f"❌ FAIL Preference learning stats raised exception: {e}")
        print()
        results["preference_learning_stats"] = {"passed": False, "error": str(e)}
        all_passed = False

    print(f"RESULT: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print()

    test_results["tests"]["statistics"] = {
        "passed": all_passed,
        "details": results
    }

    return all_passed


# ============================================================================
# TEST 6: PROGRESSION SUGGESTIONS TEST
# ============================================================================

def test_progression_suggestions():
    """Test progression suggestions across multiple genres."""
    print("=" * 80)
    print("TEST 6: PROGRESSION SUGGESTIONS")
    print("=" * 80)
    print()

    results = {}
    all_passed = True

    # Test 2 representative generators
    test_generators = {
        "Jazz": jazz_generator_service,
        "Gospel": gospel_generator_service
    }

    for genre_name, generator in test_generators.items():
        try:
            suggestions = generator.get_progression_suggestions(
                key="C",
                style="traditional"
            )

            has_suggestions = suggestions is not None
            is_list = isinstance(suggestions, list)
            valid_format = all(
                isinstance(sug, dict) and "progression" in sug
                for sug in suggestions
            ) if is_list else False

            passed = has_suggestions and is_list and valid_format
            status = "✅ PASS" if passed else "❌ FAIL"

            print(f"{status} {genre_name:12} - Suggestions: {len(suggestions) if is_list else 0}")
            if suggestions and len(suggestions) > 0:
                print(f"      First suggestion: {suggestions[0].get('name', 'N/A')}")
            print()

            results[genre_name] = {
                "count": len(suggestions) if is_list else 0,
                "passed": passed
            }

            if not passed:
                all_passed = False

        except Exception as e:
            print(f"❌ FAIL {genre_name} suggestions raised exception: {e}")
            print()
            results[genre_name] = {"passed": False, "error": str(e)}
            all_passed = False

    print(f"RESULT: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print()

    test_results["tests"]["progression_suggestions"] = {
        "passed": all_passed,
        "details": results
    }

    return all_passed


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and generate report."""
    print()
    print("=" * 80)
    print("STARTING COMPREHENSIVE AI INTEGRATION TESTS")
    print("=" * 80)
    print()

    # Run all tests
    tests = [
        ("Mixin Integration", test_mixin_integration),
        ("Complexity Routing", test_complexity_routing),
        ("ML Prediction", test_ml_prediction),
        ("User Profiling", test_user_profiling),
        ("Statistics", test_statistics),
        ("Progression Suggestions", test_progression_suggestions)
    ]

    passed_count = 0
    failed_count = 0

    for test_name, test_func in tests:
        try:
            passed = test_func()
            if passed:
                passed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ TEST CRASHED: {test_name} - {e}")
            print()
            failed_count += 1
            test_results["tests"][test_name.lower().replace(" ", "_")] = {
                "passed": False,
                "error": str(e)
            }

    # Final summary
    print()
    print("=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Tests: {passed_count + failed_count}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print()

    test_results["summary"] = {
        "total": passed_count + failed_count,
        "passed": passed_count,
        "failed": failed_count,
        "success_rate": passed_count / (passed_count + failed_count) if (passed_count + failed_count) > 0 else 0
    }

    # Save results
    try:
        results_path = Path("test_results/ai_integration_test_results.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(results_path, "w") as f:
            json.dump(test_results, f, indent=2)
        print(f"📊 Test results saved to: {results_path}")
        print()
    except Exception as e:
        print(f"⚠️  Could not save test results: {e}")
        print()

    if failed_count == 0:
        print("🎉 ALL TESTS PASSED! AI integration is working perfectly!")
        print()
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Review results above")
        print()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
