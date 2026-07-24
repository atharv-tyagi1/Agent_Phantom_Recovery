import os
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from db.models.repo_intel import CodeSymbol, DependencyEdge
from core.repo_intel.parser import CodeParser

logger = logging.getLogger(__name__)


class IncrementalASTIndexer:
    """
    Performs targeted incremental AST re-indexing for added, modified, deleted, or renamed files.
    Avoids expensive full repository re-indexing.
    """

    @classmethod
    def process_diff_files(
        cls,
        db: Session,
        repository_id: str,
        root_path: str,
        added_files: List[str],
        modified_files: List[str],
        deleted_files: List[str]
    ) -> Dict[str, Any]:
        
        updated_count = 0
        deleted_count = 0

        # 1. Handle deleted files: purge stale symbols & edges
        all_to_remove = set(deleted_files + modified_files)
        for rel_file in all_to_remove:
            db.query(CodeSymbol).filter(
                CodeSymbol.repository_id == repository_id,
                CodeSymbol.file_path == rel_file
            ).delete()

            db.query(DependencyEdge).filter(
                DependencyEdge.repository_id == repository_id,
                (DependencyEdge.source_file == rel_file) | (DependencyEdge.target_file == rel_file)
            ).delete()
            deleted_count += 1

        db.commit()

        # 2. Parse added & modified files
        all_to_parse = set(added_files + modified_files)

        for rel_file in all_to_parse:
            full_file_path = os.path.join(root_path, rel_file)
            if not os.path.isfile(full_file_path):
                continue

            try:
                with open(full_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if rel_file.endswith(".py"):
                    res = CodeParser.parse_python(content)
                elif rel_file.endswith((".ts", ".tsx", ".js", ".jsx")):
                    res = CodeParser.parse_typescript(content)
                else:
                    continue

                for sym_data in res.get("symbols", []):
                    sym = CodeSymbol(
                        repository_id=repository_id,
                        file_path=rel_file,
                        name=getattr(sym_data, "name", ""),
                        symbol_type=getattr(sym_data, "symbol_type", "function"),
                        start_line=getattr(sym_data, "start_line", 1),
                        end_line=getattr(sym_data, "end_line", 1),
                        docstring=getattr(sym_data, "docstring", None),
                        signature=getattr(sym_data, "signature", None)
                    )
                    db.add(sym)
                    updated_count += 1
            except Exception as e:
                logger.warning(f"[IncrementalASTIndexer] Error parsing file {rel_file}: {e}")

        db.commit()
        logger.info(f"[IncrementalASTIndexer] Incremental update complete: {updated_count} symbols indexed, {deleted_count} stale files purged.")

        return {
            "status": "incremental_indexed",
            "symbols_added": updated_count,
            "files_purged": deleted_count
        }
