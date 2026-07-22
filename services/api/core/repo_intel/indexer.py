import os
import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from db.models.repo_intel import CodeSymbol, DependencyEdge
from core.repo_intel.parser import CodeParser
from core.repo_intel.graph import DependencyGraph

logger = logging.getLogger(__name__)

# Exclude common non-source directories
IGNORED_DIRS = {
    ".git", "__pycache__", "node_modules", "venv", ".venv",
    "dist", "build", ".next", ".pytest_cache"
}

SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx"}


class RepoIndexer:
    """
    Orchestrates repository intelligence indexing:
    1. Scans codebase directory tree.
    2. Parses AST symbols and import dependencies.
    3. Persists CodeSymbol and DependencyEdge DB rows.
    4. Constructs an in-memory DependencyGraph for impact analysis.
    """

    def __init__(self):
        self.graph = DependencyGraph()

    def index_repository(self, db: Session, repository_id: str, root_path: str) -> Dict[str, Any]:
        if not os.path.exists(root_path):
            raise FileNotFoundError(f"Repository root directory does not exist: {root_path}")

        logger.info(f"[RepoIndexer] Indexing repository {repository_id} at {root_path}...")

        # Purge existing symbols/edges for clean re-index
        db.query(CodeSymbol).filter(CodeSymbol.repository_id == repository_id).delete()
        db.query(DependencyEdge).filter(DependencyEdge.repository_id == repository_id).delete()
        db.commit()

        indexed_files = 0
        extracted_symbols_count = 0
        edges_count = 0

        for root, dirs, files in os.walk(root_path):
            # Filter ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_path).replace("\\", "/")

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        code_content = f.read()

                    parsed = CodeParser.parse_file(rel_path, code_content)
                    indexed_files += 1

                    # Save Extracted Symbols
                    for sym in parsed.get("symbols", []):
                        db_sym = CodeSymbol(
                            repository_id=repository_id,
                            file_path=rel_path,
                            name=sym.name,
                            symbol_type=sym.symbol_type,
                            start_line=sym.start_line,
                            end_line=sym.end_line,
                            docstring=sym.docstring,
                            signature=sym.signature
                        )
                        db.add(db_sym)
                        extracted_symbols_count += 1

                    # Save Import Dependency Edges
                    for imp in parsed.get("imports", []):
                        edge = DependencyEdge(
                            repository_id=repository_id,
                            source_file=rel_path,
                            target_file=imp,
                            dependency_type="import"
                        )
                        db.add(edge)
                        self.graph.add_dependency(rel_path, imp)
                        edges_count += 1

                except Exception as e:
                    logger.warning(f"[RepoIndexer] Failed to parse file {rel_path}: {e}")

        db.commit()
        logger.info(
            f"[RepoIndexer] Complete: {indexed_files} files, {extracted_symbols_count} symbols, {edges_count} edges."
        )

        return {
            "repository_id": repository_id,
            "status": "indexed",
            "files_indexed": indexed_files,
            "symbols_extracted": extracted_symbols_count,
            "dependency_edges": edges_count
        }


# Singleton instance used across the app
repo_indexer = RepoIndexer()
