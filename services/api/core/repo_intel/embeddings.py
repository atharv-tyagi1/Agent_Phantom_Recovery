import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from db.models.repo_intel import CodeSymbol

logger = logging.getLogger(__name__)


class CodeSearchEngine:
    """
    Search engine over codebase symbols and source code context snippets.
    Combines exact symbol matching, token overlap scoring, and docstring filtering.
    Ready for vector embedding (pgvector) upgrades in production.
    """

    @staticmethod
    def search_symbols(
        db: Session,
        repository_id: str,
        query: str,
        limit: int = 10,
        symbol_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search indexed symbols by query string and optional symbol type filter.
        """
        query_terms = [t.lower() for t in query.split() if len(t) > 1]
        if not query_terms:
            return []

        base_query = db.query(CodeSymbol).filter(CodeSymbol.repository_id == repository_id)
        if symbol_type:
            base_query = base_query.filter(CodeSymbol.symbol_type == symbol_type)

        all_symbols = base_query.all()
        scored_results = []

        for symbol in all_symbols:
            name_lower = symbol.name.lower()
            doc_lower = (symbol.docstring or "").lower()
            sig_lower = (symbol.signature or "").lower()
            file_lower = symbol.file_path.lower()

            score = 0.0

            # Exact symbol name match -> highest score
            if query.lower() == name_lower:
                score += 10.0
            elif query.lower() in name_lower:
                score += 5.0

            # Term overlap scoring
            for term in query_terms:
                if term in name_lower:
                    score += 3.0
                if term in sig_lower:
                    score += 1.5
                if term in doc_lower:
                    score += 1.0
                if term in file_lower:
                    score += 0.5

            if score > 0:
                scored_results.append((score, symbol))

        # Sort by relevance score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)

        return [
            {
                "id": s.id,
                "name": s.name,
                "symbol_type": s.symbol_type,
                "file_path": s.file_path,
                "start_line": s.start_line,
                "end_line": s.end_line,
                "signature": s.signature,
                "docstring": s.docstring,
                "relevance_score": round(score, 2)
            }
            for score, s in scored_results[:limit]
        ]
