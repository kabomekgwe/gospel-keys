#!/usr/bin/env python3
"""
Comprehensive Hybrid Music Generator API Test
Runs 100+ permutations and compares outputs for uniqueness.
"""

import requests
import json
import hashlib
import time
from collections import defaultdict
from itertools import product
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/ai/generate/hybrid"

# Test parameters - keep genre fixed as "gospel"
GENRE = "gospel"
KEYS = ["C", "D", "E", "F", "G", "A", "B"]
TEMPOS = [60, 80, 100, 120, 140]
COMPLEXITIES = [1, 3, 5, 7, 9]
NUM_BARS = [4, 8]

def make_request(key, tempo, complexity, num_bars):
    """Make API request and return chord progression hash."""
    try:
        data = {
            "genre": GENRE,
            "key": key,
            "tempo": tempo,
            "complexity": complexity,
            "num_bars": num_bars,
            "synthesize_audio": "false",
            "include_melody": "true"
        }
        
        response = requests.post(BASE_URL, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            chords = result.get("chord_progression", {}).get("chords", [])
            voicings = result.get("chord_progression", {}).get("voicings", [])
            midi_tokens = result.get("midi_tokens", [])[:20]  # First 20 tokens
            
            # Create hash from chord progression content
            content = f"{chords}|{len(voicings)}|{midi_tokens}"
            hash_val = hashlib.md5(content.encode()).hexdigest()[:12]
            
            return {
                "success": True,
                "chords": chords,
                "hash": hash_val,
                "generation_time_ms": result.get("generation_time_ms", 0)
            }
        else:
            return {"success": False, "error": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 70)
    print("HYBRID MUSIC GENERATOR - 100+ PERMUTATION TEST")
    print(f"Genre: {GENRE} (fixed)")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Generate permutations
    permutations = list(product(KEYS, TEMPOS, COMPLEXITIES, NUM_BARS))
    total = len(permutations)
    print(f"\nTotal permutations: {total}")
    print(f"  Keys: {KEYS}")
    print(f"  Tempos: {TEMPOS}")
    print(f"  Complexities: {COMPLEXITIES}")
    print(f"  Num Bars: {NUM_BARS}")
    print()
    
    results = []
    hashes = defaultdict(list)
    chord_progressions = defaultdict(int)
    errors = 0
    
    for i, (key, tempo, complexity, num_bars) in enumerate(permutations):
        params = f"key={key} tempo={tempo} c={complexity} bars={num_bars}"
        
        result = make_request(key, tempo, complexity, num_bars)
        
        if result["success"]:
            chords_str = ", ".join(result["chords"])
            chord_progressions[chords_str] += 1
            hashes[result["hash"]].append(params)
            results.append(result)
            
            status = "✓"
            print(f"  [{i+1:3}/{total}] {status} {params} | {chords_str[:40]:<40} | {result['hash']}")
        else:
            errors += 1
            status = "✗"
            print(f"  [{i+1:3}/{total}] {status} {params} | ERROR: {result.get('error', 'unknown')}")
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    # Results summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    successful = len(results)
    unique_hashes = len(hashes)
    unique_progressions = len(chord_progressions)
    
    print(f"\n📊 Statistics:")
    print(f"   Total requests: {total}")
    print(f"   Successful: {successful}")
    print(f"   Errors: {errors}")
    print(f"   Unique hashes: {unique_hashes}")
    print(f"   Unique progressions: {unique_progressions}")
    print(f"   Uniqueness ratio: {unique_hashes/successful*100:.1f}%")
    
    print(f"\n🎵 Most common chord progressions:")
    sorted_progs = sorted(chord_progressions.items(), key=lambda x: -x[1])
    for prog, count in sorted_progs[:10]:
        pct = count/successful*100
        print(f"   [{count:3}x] ({pct:5.1f}%) {prog}")
    
    print(f"\n🔄 Duplicate hash analysis:")
    duplicates = {h: params for h, params in hashes.items() if len(params) > 1}
    if duplicates:
        print(f"   Found {len(duplicates)} hashes with duplicates:")
        for hash_val, params_list in list(duplicates.items())[:5]:
            print(f"   {hash_val}: {len(params_list)} occurrences")
            for p in params_list[:3]:
                print(f"      - {p}")
    else:
        print("   ✓ No duplicate hashes found!")
    
    # Time analysis
    if results:
        times = [r["generation_time_ms"] for r in results]
        avg_time = sum(times) / len(times)
        print(f"\n⏱️  Generation times:")
        print(f"   Average: {avg_time:.0f}ms")
        print(f"   Min: {min(times)}ms")
        print(f"   Max: {max(times)}ms")
    
    print("\n" + "=" * 70)
    print(f"✅ TEST COMPLETE - {unique_hashes}/{successful} unique ({unique_hashes/successful*100:.1f}%)")
    print("=" * 70)
    
    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "genre": GENRE,
        "total_requests": total,
        "successful": successful,
        "errors": errors,
        "unique_hashes": unique_hashes,
        "unique_progressions": unique_progressions,
        "uniqueness_ratio": unique_hashes/successful if successful > 0 else 0,
        "top_progressions": sorted_progs[:20],
        "duplicate_hashes": {h: len(p) for h, p in duplicates.items()}
    }
    
    with open("outputs/hybrid_permutation_test.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: outputs/hybrid_permutation_test.json")

if __name__ == "__main__":
    main()
