from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

os.environ['db_url'] = os.getenv('database_url')
engine = create_async_engine(os.environ['db_url'], echo = True)

print('Database Connection successful')

async def get_async_session():
    global engine
    async_conn = sessionmaker(
        bind = engine, 
        class_= AsyncSession, 
        expire_on_commit=False
    )
    ## creating an async session with the db
    async with async_conn() as session: 
        yield session
