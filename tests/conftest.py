import asyncio
import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv

from gbf import models
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession


@pytest.fixture(scope="session", autouse=True)
def auto001_load_env():
    env_path = os.path.join(os.environ['CONFIG_FOLDER'], '.env.testing')
    load_dotenv(override=True, dotenv_path=env_path)


@pytest_asyncio.fixture(scope="session")
async def engine():
    """テストDBエンジンを生成する

    Returns:
        _type_: _description_
    """
    # db init
    DBUSER = os.environ['TEST_DBUSER']
    DBPASSWORD = os.environ['TEST_DBPASSWORD']
    DBHOST = os.environ['TEST_DBHOST']
    DBDATABASE = os.environ['TEST_DBDATABASE']

    URL = f'postgresql+asyncpg://{DBUSER}:{DBPASSWORD}@{DBHOST}/{DBDATABASE}'
    engine = create_async_engine(URL, echo=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def create_temp_table(engine: AsyncEngine):
    """テストDBにテーブルを一時的に作成する

    Args:
        engine (Engine): テストDBエンジン
    """
    await models.init_db_from_engine(engine)
    yield
    await models.drop_db_from_engine(engine)


@pytest_asyncio.fixture
async def async_db_session(engine, create_temp_table):
    """DBセッションを生成する

    Args:
        engine (Engine): テストDBエンジン

    Returns:
        AsyncSession: DBセッション
    """
    async_session = AsyncSession(bind=engine)
    try:
        yield async_session
    finally:
        await async_session.close()
