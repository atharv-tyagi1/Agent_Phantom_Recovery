import unittest
import os
import uuid
import tempfile
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.session import Base
from db.models.user import User
from db.models.project import Project
from db.models.repository import Repository
from db.models.repo_intel import CodeSymbol, DependencyEdge
from core.repo_intel.parser import CodeParser
from core.repo_intel.graph import DependencyGraph
from core.repo_intel.embeddings import CodeSearchEngine
from core.repo_intel.indexer import RepoIndexer

# In-memory SQLite for repository intelligence database tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


class TestRepositoryIntelligence(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.db = TestingSessionLocal(bind=self.connection)

        self.user = User(
            id=str(uuid.uuid4()),
            supabase_id=str(uuid.uuid4()),
            email=f"user_{uuid.uuid4().hex[:6]}@phantom.ai"
        )
        self.db.add(self.user)
        self.db.commit()

        self.project = Project(
            id=str(uuid.uuid4()),
            name="Sample Project",
            description="Testing repo intel",
            owner_id=self.user.id
        )
        self.db.add(self.project)
        self.db.commit()

        self.repo = Repository(
            id=str(uuid.uuid4()),
            project_id=self.project.id,
            name="Sample Target Repo",
            git_url="https://github.com/phantom/sample.git",
            local_path=tempfile.mkdtemp()
        )
        self.db.add(self.repo)
        self.db.commit()
        self.db.refresh(self.repo)

    def tearDown(self):
        if os.path.exists(self.repo.local_path):
            shutil.rmtree(self.repo.local_path, ignore_errors=True)
        self.db.close()
        self.transaction.rollback()
        self.connection.close()

    # ── AST Parser Tests ──────────────────────────────────────────────────────

    def test_python_parser(self):
        py_code = '''"""Module docstring."""
import sys
from os import path

class DataProcessor:
    """Class docstring."""
    def process(self, data: str) -> bool:
        return True

async def fetch_user_data(user_id: str):
    return {"id": user_id}
'''
        parsed = CodeParser.parse_python(py_code)
        symbols = parsed["symbols"]
        imports = parsed["imports"]

        self.assertIn("sys", imports)
        self.assertIn("os", imports)

        names = [s.name for s in symbols]
        self.assertIn("DataProcessor", names)
        self.assertIn("DataProcessor.process", names)
        self.assertIn("fetch_user_data", names)

    def test_typescript_parser(self):
        ts_code = '''import { useState } from 'react';
import axios from 'axios';

export interface UserProfile {
    id: string;
    name: string;
}

export function UserComponent(props: UserProfile) {
    return null;
}

export const fetchProfile = async () => {
    return {};
};
'''
        parsed = CodeParser.parse_typescript(ts_code)
        symbols = parsed["symbols"]
        imports = parsed["imports"]

        self.assertIn("react", imports)
        self.assertIn("axios", imports)

        names = [s.name for s in symbols]
        self.assertIn("UserProfile", names)
        self.assertIn("UserComponent", names)
        self.assertIn("fetchProfile", names)

    # ── Dependency Graph Tests ───────────────────────────────────────────────

    def test_dependency_graph_and_impact_radius(self):
        graph = DependencyGraph()
        
        # File A imports B; File C imports A; File D imports C
        graph.add_dependency("services/api/main.py", "services/api/core/auth.py")
        graph.add_dependency("services/api/routes/auth.py", "services/api/core/auth.py")
        graph.add_dependency("services/api/tests/test_auth.py", "services/api/routes/auth.py")

        # Check impact radius when `core/auth.py` is edited
        impact = graph.get_impact_radius("services/api/core/auth.py", max_depth=3)
        
        self.assertEqual(impact["target_file"], "services/api/core/auth.py")
        self.assertEqual(impact["total_impacted_count"], 3)
        self.assertIn("services/api/main.py", impact["impacted_files"])
        self.assertIn("services/api/routes/auth.py", impact["impacted_files"])
        self.assertIn("services/api/tests/test_auth.py", impact["impacted_files"])

    # ── End-to-End Indexer & Search Engine Tests ──────────────────────────────

    def test_repo_indexer_and_search_engine(self):
        # Scaffold sample files inside local_path
        src_dir = os.path.join(self.repo.local_path, "services")
        os.makedirs(src_dir, exist_ok=True)

        file1 = os.path.join(src_dir, "auth_service.py")
        with open(file1, "w", encoding="utf-8") as f:
            f.write('''import sys

class AuthService:
    """Authentication and session management service."""
    def validate_token(self, token: str) -> bool:
        return True
''')

        indexer = RepoIndexer()
        res = indexer.index_repository(self.db, repository_id=self.repo.id, root_path=self.repo.local_path)

        self.assertGreaterEqual(res["files_indexed"], 1)
        self.assertGreaterEqual(res["symbols_extracted"], 2)

        # Search codebase
        results = CodeSearchEngine.search_symbols(
            db=self.db,
            repository_id=self.repo.id,
            query="AuthService"
        )
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "AuthService")
        self.assertEqual(results[0]["symbol_type"], "class")


if __name__ == "__main__":
    unittest.main()
