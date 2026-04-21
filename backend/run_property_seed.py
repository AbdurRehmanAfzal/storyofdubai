#!/usr/bin/env python3
"""Property seeder runner - generates 300 realistic Dubai property listings."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.scrapers.property_seeder import seed_properties
from app.models import *  # noqa — ensures all models are registered


def main():
    print("=" * 70)
    print("DUBAI PROPERTY SEEDER")
    print("=" * 70)
    print("\nSource: Curated seed data (10 areas, realistic prices)")
    print("Target: 300 property listings for page generation\n")

    engine = create_engine(settings.DATABASE_URL_SYNC)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        stats = seed_properties(db)
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Saved: {stats['saved']} new properties")
        print(f"Skipped: {stats['skipped']} (area not found)")
        print(f"Area errors: {stats['area_errors']}\n")

    print("=" * 70)
    print("PROPERTY PAGES NOW AVAILABLE AT:")
    print("=" * 70)
    print("  /apartments/dubai-marina/1-bedroom/50k-100k/")
    print("  /apartments/downtown-dubai/2-bedroom/100k-200k/")
    print("  /apartments/jumeirah-village-circle/1-bedroom/under-50k/")
    print("  /apartments/palm-jumeirah/4-bedroom/200k-plus/")
    print("\nRun: npm run build in frontend/ to generate property pages")
    print("=" * 70)


if __name__ == "__main__":
    main()
