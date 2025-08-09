from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def fts_search(db: AsyncSession, q: str, limit: int = 24) -> List[Dict[str, Any]]:
    sql = text(
        """
        select id, title, neutral_cite, reporter_cite, ts_rank(fts_doc, plainto_tsquery('english', :q)) as rank
        from authorities
        where fts_doc @@ plainto_tsquery('english', :q)
        order by rank desc
        limit :limit
        """
    )
    rows = (await db.execute(sql, {"q": q, "limit": limit})).mappings().all()
    return [dict(r) for r in rows]


async def trigram_cite_search(db: AsyncSession, cite: str, limit: int = 10) -> List[Dict[str, Any]]:
    sql = text(
        """
        select id, title, neutral_cite, reporter_cite,
               greatest(similarity(neutral_cite, :cite), similarity(reporter_cite, :cite)) as sim
        from authorities
        order by sim desc
        limit :limit
        """
    )
    rows = (await db.execute(sql, {"cite": cite, "limit": limit})).mappings().all()
    return [dict(r) for r in rows]


