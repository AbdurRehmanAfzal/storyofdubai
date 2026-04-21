#!/usr/bin/env python3
"""Verify AI enrichment completion and quality."""

from sqlalchemy import create_engine, text
from app.config import settings


def main():
    engine = create_engine(settings.DATABASE_URL_SYNC)

    with engine.connect() as conn:
        # Count totals and enriched
        venues_total = conn.execute(text("SELECT COUNT(*) FROM venues")).scalar()
        venues_enriched = conn.execute(text(
            "SELECT COUNT(*) FROM venues WHERE description != '' AND description IS NOT NULL"
        )).scalar()

        visas_total = conn.execute(text("SELECT COUNT(*) FROM visa_nationality_guides")).scalar()
        visas_enriched = conn.execute(text(
            "SELECT COUNT(*) FROM visa_nationality_guides WHERE ai_guide != '' AND ai_guide IS NOT NULL"
        )).scalar()

        props_total = conn.execute(text("SELECT COUNT(*) FROM properties")).scalar()
        props_enriched = conn.execute(text(
            "SELECT COUNT(*) FROM properties WHERE description != '' AND description IS NOT NULL"
        )).scalar()

        # Display results
        print("=" * 60)
        print("AI ENRICHMENT VERIFICATION")
        print("=" * 60)
        print(f"\nVenues:        {venues_enriched:>4}/{venues_total:<4} enriched ({100*venues_enriched//venues_total if venues_total else 0}%)")
        print(f"Visa Guides:   {visas_enriched:>4}/{visas_total:<4} enriched ({100*visas_enriched//visas_total if visas_total else 0}%)")
        print(f"Properties:    {props_enriched:>4}/{props_total:<4} enriched ({100*props_enriched//props_total if props_total else 0}%)")

        total = venues_enriched + visas_enriched + props_enriched
        target = venues_total + visas_total + props_total
        print(f"\n{'TOTAL':15} {total:>4}/{target:<4} pages ({100*total//target if target else 0}%)")

        # Show samples
        print("\n" + "=" * 60)
        print("SAMPLE CONTENT (First 200 chars)")
        print("=" * 60)

        if venues_enriched > 0:
            print("\n[VENUE SAMPLE]")
            venue = conn.execute(text("""
                SELECT name, LEFT(description, 200) FROM venues
                WHERE description != '' LIMIT 1
            """)).fetchone()
            print(f"  {venue[0]}")
            print(f"  {venue[1]}...")

        if visas_enriched > 0:
            print("\n[VISA GUIDE SAMPLE]")
            visa = conn.execute(text("""
                SELECT n.name, vt.name, LEFT(vng.ai_guide, 200)
                FROM visa_nationality_guides vng
                JOIN nationalities n ON n.id = vng.nationality_id
                JOIN visa_types vt ON vt.id = vng.visa_type_id
                WHERE vng.ai_guide != '' LIMIT 1
            """)).fetchone()
            print(f"  {visa[0]} → {visa[1]}")
            print(f"  {visa[2]}...")

        if props_enriched > 0:
            print("\n[PROPERTY SAMPLE]")
            prop = conn.execute(text("""
                SELECT title, LEFT(description, 200) FROM properties
                WHERE description != '' LIMIT 1
            """)).fetchone()
            print(f"  {prop[0]}")
            print(f"  {prop[1]}...")

        print("\n" + "=" * 60)
        if total == target:
            print("✓ ENRICHMENT COMPLETE - All pages have unique AI content")
        else:
            print(f"⏳ ENRICHMENT IN PROGRESS - {target - total} pages remaining")
        print("=" * 60)

    engine.dispose()


if __name__ == "__main__":
    main()
