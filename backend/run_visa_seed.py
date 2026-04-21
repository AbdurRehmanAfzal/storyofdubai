#!/usr/bin/env python3
"""Visa seeder runner - generates 400 visa guide pages (50 nationalities × 8 visa types)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.scrapers.visa_seeder import seed_nationalities, seed_visa_types, seed_visa_guides
from app.models import *  # noqa — ensures all models registered


def main():
    print("=" * 70)
    print("VISA SEEDER")
    print("=" * 70)
    print("\nSource: Seed data (50 nationalities, 8 visa types)")
    print("Target: 400 visa guide pages for programmatic SEO\n")

    engine = create_engine(settings.DATABASE_URL_SYNC)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        nat_count = seed_nationalities(db)
        vt_count = seed_visa_types(db)
        guide_count = seed_visa_guides(db)

        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Nationalities seeded: {nat_count}")
        print(f"Visa types seeded:    {vt_count}")
        print(f"Guide pages created:  {guide_count}")
        print(f"\nTotal visa pages ready: {guide_count}")
        print(f"URL pattern: /visa-guide/[nationality]/[visa-type]/")
        print(f"Example: /visa-guide/pakistani/golden-visa-10-years/\n")

        print("=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("Run in frontend/: npm run build")
        print("This will generate all 400 visa pages from the database")
        print("=" * 70)


if __name__ == "__main__":
    main()
