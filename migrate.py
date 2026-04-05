import asyncio
from app.db.session import engine
from app.db.base import Base
from app.models import *

async def run_migration():
    print(f"Connecting to: {engine.url.render_as_string(hide_password=True)}")
    async with engine.begin() as conn:
        print("Creating tables on Supabase...")
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Migration successful! All tables are now on Supabase.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
