from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ParsingSource


async def create_source(session: AsyncSession, title: str, url: str, xpath: str) -> ParsingSource:
    """Создает новый источник для парсинга в базе данных"""
    new_source = ParsingSource(
        title=title,
        url=url,
        xpath=xpath
    )
    session.add(new_source)
    await session.commit()
    await session.refresh(new_source)
    return new_source


async def create_sources_bulk(session: AsyncSession, sources_data: list) -> list[ParsingSource]:
    """Создает несколько источников для парсинга одним запросом"""
    sources = [
        ParsingSource(
            title=item["title"],
            url=item["url"],
            xpath=item["xpath"]
        )
        for item in sources_data
    ]
    session.add_all(sources)
    await session.commit()

    # Получаем ID новых источников
    for source in sources:
        await session.refresh(source)

    return sources


async def get_all_sources(session: AsyncSession) -> list[ParsingSource]:
    """Получает все источники из базы данных"""
    result = await session.execute(select(ParsingSource))
    return result.scalars().all()


async def get_source_by_id(session: AsyncSession, source_id: int) -> ParsingSource:
    """Получает источник по ID"""
    return await session.get(ParsingSource, source_id)


async def update_source_price(session: AsyncSession, source_id: int, avg_price: float) -> ParsingSource:
    """Обновляет среднюю цену для источника"""
    source = await session.get(ParsingSource, source_id)
    if source:
        source.avg_price = avg_price
        await session.commit()
        await session.refresh(source)
    return source


async def update_sources_prices_bulk(session: AsyncSession, prices_data: dict) -> None:
    """Обновляет цены для нескольких источников одновременно"""
    for source_id, price in prices_data.items():
        source = await session.get(ParsingSource, source_id)
        if source:
            source.avg_price = price

    await session.commit()


async def delete_source(session: AsyncSession, source_id: int) -> bool:
    """Удаляет источник по ID"""
    source = await session.get(ParsingSource, source_id)
    if source:
        await session.delete(source)
        await session.commit()
        return True
    return False