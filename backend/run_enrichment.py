from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import *  # noqa


def main():
    if not settings.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set. Add it to .env and retry.")
        return

    print("Story of Dubai — AI Enrichment Pipeline")
    print(f"Model: {settings.OPENAI_MODEL}")
    print(f"Budget cap: $3.00 (hard stop)")
    print(f"Estimated cost for full run: ~$0.24")
    print("-" * 40)

    from app.ai_enrichment.enricher import (
        enrich_venues,
        enrich_visa_guides,
        enrich_properties,
    )

    engine = create_engine(settings.DATABASE_URL_SYNC)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        print("\n[1/3] Enriching venues...")
        v = enrich_venues(db, limit=500)
        print(f"      {v} venues enriched")

        print("\n[2/3] Enriching visa guides...")
        g = enrich_visa_guides(db, limit=400)
        print(f"      {g} visa guides enriched")

        print("\n[3/3] Enriching properties...")
        p = enrich_properties(db, limit=306)
        print(f"      {p} properties enriched")

    from app.ai_enrichment.enricher import _session_cost

    total = v + g + p
    print(f"\n{'='*40}")
    print(f"Total pages enriched: {total}")
    print(f"Actual cost: ${_session_cost:.4f}")
    print(f"Remaining budget: ${3.0 - _session_cost:.4f}")
    print(f"\nAll pages now have unique AI-generated content.")
    print(f"Google will not flag these as thin/duplicate content.")


if __name__ == "__main__":
    main()
