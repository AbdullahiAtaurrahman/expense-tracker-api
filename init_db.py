import asyncio

from sqlalchemy import text

from app.database import Base, engine
from app.models.transaction import Transaction


async def init_db():
    try:
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))
            await connection.run_sync(Base.metadata.create_all)

        print("Database connection successful!")
        print("Tables created successfully!")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
