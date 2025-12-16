import asyncio
from app.services.template_loader import template_loader
from app.services.curriculum_service import CurriculumService
from unittest.mock import MagicMock

async def test_template_instantiation():
    print("🚀 Starting Template Instantiation Test...")
    
    # 1. List Templates
    print("\n📋 Listing Templates...")
    templates = template_loader.list_templates()
    print(f"Found {len(templates)} templates.")
    for t in templates:
        print(f" - {t['id']}: {t['name']}")

    if not templates:
        print("❌ No templates found! Check templates/new-templates dir.")
        return

    # 2. Pick a template
    target_id = 'gemini-1' # Known good template
    print(f"\n🧪 Testing instantiation for: {target_id}")

    # 3. Mock DB Session
    mock_db = MagicMock()
    service = CurriculumService(mock_db)
    
    # 4. Map Template to Plan
    # (We test the internal mapping logic first to avoid DB calls)
    try:
        template_data = template_loader.get_template(target_id)
        if not template_data:
             print(f"❌ Failed to load data for {target_id}")
             return

        plan = service._map_template_to_plan(template_data, target_id)
        
        print("\n✅ Plan Mapped Successfully!")
        print(f"Title: {plan['title']}")
        print(f"Modules: {len(plan['modules'])}")
        
        for idx, mod in enumerate(plan['modules']):
            print(f"  Module {idx+1}: {mod['title']} ({len(mod['lessons'])} lessons)")
            if mod['lessons']:
                l1 = mod['lessons'][0]
                print(f"    - Lesson 1: {l1['title']} ({len(l1['exercises'])} exercises)")
                if l1['exercises']:
                    print(f"      * Ex 1: {l1['exercises'][0]['title']}")

    except Exception as e:
        print(f"❌ Error during mapping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_template_instantiation())
