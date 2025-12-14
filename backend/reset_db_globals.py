import asyncio
import sys
import os

# Add current directory to path so imports work
sys.path.append(os.getcwd())

from app.database.session import async_session_maker
from app.database.models import User
from app.database.curriculum_models import Curriculum
from app.core import security
from app.services.curriculum_service import CurriculumService
from app.services.curriculum_defaults import DEFAULT_CURRICULUMS
from sqlalchemy.future import select
from sqlalchemy import delete

async def reset_and_seed():
    print("🔄 Resetting Curriculums & Seeding Globals...")
    async with async_session_maker() as db:
        # 1. Truncate Curriculums (Cascade should handle children)
        print("🗑️  Deleting all existing curriculums...")
        await db.execute(delete(Curriculum))
        await db.commit()
        
        # 2. Get/Create Global Admin
        print("👤 Getting/Creating Global Admin (admin@gospelkeys.ai)...")
        result = await db.execute(select(User).where(User.email == "admin@gospelkeys.ai"))
        user = result.scalars().first()
        
        if not user:
            user = User(
                email="admin@gospelkeys.ai",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn96pzlkfq.gp.3/s1", # Fake hash
                full_name="Global Admin",
                is_active=True,
                is_superuser=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        print(f"Global Admin ID: {user.id}")
        
        # 3. Create Services
        service = CurriculumService(db)
        
        # 4. Create Each Curriculum for Admin
        for key, template in DEFAULT_CURRICULUMS.items():
            print(f"Creating global curriculum: {template['title']} ({key})...")
            try:
                curr = await service.create_default_curriculum(user.id, key)
                # Mark as global if we had a flag, but for now ownership by admin implies global
                print(f"✅ Created: {curr.id}")
            except Exception as e:
                print(f"❌ Failed to create {key}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reset_and_seed())
