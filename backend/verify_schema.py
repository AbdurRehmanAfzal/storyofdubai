#!/usr/bin/env python3
"""
Verify that all database models are correctly defined.
This script inspects the SQLAlchemy models and prints their schema.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models import (
    Area, Category, Venue, Developer, Property,
    Nationality, VisaType, VisaNationalityGuide,
    Company, ScrapeJob
)
from sqlalchemy import inspect, MetaData, create_engine
from app.database import Base

def print_table_schema():
    """Print detailed schema information for all models."""
    models = [
        ("Area", Area),
        ("Category", Category),
        ("Venue", Venue),
        ("Developer", Developer),
        ("Property", Property),
        ("Nationality", Nationality),
        ("VisaType", VisaType),
        ("VisaNationalityGuide", VisaNationalityGuide),
        ("Company", Company),
        ("ScrapeJob", ScrapeJob),
    ]

    print("\n" + "="*80)
    print("DATABASE SCHEMA VERIFICATION")
    print("="*80 + "\n")

    total_models = len(models)
    total_columns = 0
    total_indexes = 0
    total_constraints = 0

    for model_name, model_class in models:
        print(f"\n📦 {model_name}")
        print("-" * 80)

        # Get table info
        mapper = inspect(model_class)
        table = mapper.mapped_table

        # Columns
        columns = mapper.columns
        total_columns += len(columns)
        print(f"   Columns ({len(columns)}):")
        for col in columns:
            col_type = str(col.type)
            nullable = "nullable" if col.nullable else "NOT NULL"
            pk = "PK" if col.primary_key else ""
            unique = "UNIQUE" if col.unique else ""
            attrs = [nullable, pk, unique]
            attrs_str = " | ".join(a for a in attrs if a)
            print(f"     • {col.name:30} {col_type:20} [{attrs_str}]")

        # Foreign Keys
        fks = [c for c in table.constraints if hasattr(c, 'columns')]
        fks = [c for c in fks if any(col.foreign_keys for col in c.columns)]
        if fks:
            print(f"\n   Foreign Keys:")
            for fk in table.foreign_keys:
                print(f"     • {fk.parent.name} → {fk.column}")

        # Indexes
        indexes = list(table.indexes)
        total_indexes += len(indexes)
        if indexes:
            print(f"\n   Indexes ({len(indexes)}):")
            for idx in indexes:
                cols = ", ".join(c.name for c in idx.columns)
                unique_str = "UNIQUE" if idx.unique else ""
                print(f"     • {idx.name:40} ON ({cols}) {unique_str}")

        # Constraints
        constraints = [c for c in table.constraints
                      if c.__class__.__name__ in ('UniqueConstraint', 'PrimaryKeyConstraint')]
        total_constraints += len(constraints)
        if constraints:
            print(f"\n   Constraints ({len(constraints)}):")
            for const in constraints:
                const_type = const.__class__.__name__
                if hasattr(const, 'columns') and len(const.columns) > 0:
                    cols = ", ".join(c.name for c in const.columns)
                    print(f"     • {const_type:30} ON ({cols})")

        print()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ Total Models:      {total_models}")
    print(f"✓ Total Columns:     {total_columns}")
    print(f"✓ Total Indexes:     {total_indexes}")
    print(f"✓ Total Constraints: {total_constraints}")
    print("\n✅ All models loaded successfully!")
    print("\nMigration file: alembic/versions/001_initial_schema_all_tables.py")
    print("To apply: alembic upgrade head")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        print_table_schema()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
