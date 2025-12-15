
import asyncio
import os
import sys
from app.services.ai_generator import AIGeneratorService
from app.schemas.ai import ProgressionRequest, ProgressionStyle

# Mock settings if needed, but we expect .env to be loaded by the app or we load it here
from app.core.config import settings

async def test_generation():
    print(f"Google Key present: {bool(settings.google_api_key)}")
    print(f"Anthropic Key present: {bool(settings.anthropic_api_key)}")
    
    service = AIGeneratorService()
    print(f"Service initialized. Gemini available: {service.gemini_available}")
    
    request = ProgressionRequest(
        key="C",
        mode="major",
        style=ProgressionStyle.JAZZ,
        length=4
    )
    
    try:
        print("Attempting to generate progression...")
        response = await service.generate_progression(request)
        print("Success!")
        print(response)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ensure asyncio loop matches what uvicorn uses
    asyncio.run(test_generation())
