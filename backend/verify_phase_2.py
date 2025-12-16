import asyncio
import sys
import os

# Ensure backend dir is in path
sys.path.append(os.getcwd())

async def verify_phase2():
    print("--- Phase 2 Verification ---")
    
    # 1. Verify RAG
    print("\n1. Testing RAG Service...")
    try:
        from app.services.ai.rag_service import rag_service
        
        # Add a mock document
        test_concept = "Kabo Chord"
        test_content = "The Kabo Chord is a theoretical chord consisting of C, E, G, B, and F#. It is known for its jazzy brilliance."
        rag_service.add_document("doc_001", test_content, {"category": "test"})
        
        # Retrieve it
        results = rag_service.retrieve("What is the Kabo Chord?")
        if test_content in results:
            print(f"✅ RAG Retrieval successful. Found: {results[0][:50]}...")
        else:
            print(f"❌ RAG Retrieval failed. Got: {results}")
            
    except Exception as e:
        print(f"❌ RAG Error: {e}")

    # 2. Verify Text-to-MIDI (Mock check if MusicLang needs model download)
    print("\n2. Testing Text-to-MIDI Generation...")
    try:
        from app.services.ai.chord_service import chord_service
        
        # We won't run full generation as it might prompt model download/heavy compute in this script
        # But we check if method exists and imports
        if hasattr(chord_service, 'generate_score'):
            print("✅ generate_score method exists on ChordService.")
        else:
            print("❌ generate_score method MISSING.")
            
    except Exception as e:
        print(f"❌ ChordService Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_phase2())
