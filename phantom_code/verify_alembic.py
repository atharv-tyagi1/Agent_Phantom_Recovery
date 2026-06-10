import os
import sys
import importlib.util
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, text
from alembic.migration import MigrationContext
from alembic.operations import Operations

sys.path.append(os.path.join(os.path.dirname(__file__), 'packages/database/migrations/versions'))

def verify_alembic():
    print("=== STARTING POSTGRESQL (Emulated via SQLite) ===")
    engine = create_engine('sqlite:///:memory:', echo=False)
    metadata = MetaData()

    print("\n[DB] Creating baseline Phase 0 tables...")
    Table('executions', metadata, Column('id', String, primary_key=True), Column('status', String))
    Table('checkpoints', metadata, Column('id', String, primary_key=True), Column('execution_id', String), Column('created_at', DateTime))
    Table('execution_states', metadata, Column('id', String, primary_key=True), Column('execution_id', String))
    Table('tasks', metadata, Column('id', String, primary_key=True), Column('execution_id', String), Column('status', String))
    Table('audit_logs', metadata, Column('id', String, primary_key=True), Column('correlation_id', String))
    metadata.create_all(engine)

    print("\n[Alembic] Running alembic upgrade head (002_add_indexes.py)...")
    
    # Load the actual migration script
    spec = importlib.util.spec_from_file_location("add_indexes", "packages/database/migrations/versions/002_add_indexes.py")
    add_indexes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(add_indexes)

    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        op = Operations(ctx)
        
        # Monkeypatch alembic op into the script module
        add_indexes.op = op
        
        add_indexes.upgrade()
        print("  -> Migration 002_add_indexes executed successfully.")

        print("\n=== VERIFYING ACTUAL INDEXES CREATED ===")
        result = conn.execute(text("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")).fetchall()
        for row in result:
            if not row.name.startswith("sqlite_"):
                print(f"  -> Index Found: {row.name} ON TABLE {row.tbl_name}")

if __name__ == "__main__":
    verify_alembic()
