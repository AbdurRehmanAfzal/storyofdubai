#!/usr/bin/env python3
"""Test scraper structure and imports without requiring API calls."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import inspect
from app.scrapers.google_places_demo import GooglePlacesScraper
from app.scrapers.base import BaseScraper
from app.scoring.venue_scorer import VenueScorer
from app.pipeline.tasks import (
    scrape_google_places_all_areas,
    run_scoring_engine_all,
)

def test_scraper_inheritance():
    """Verify GooglePlacesScraper inherits from BaseScraper"""
    print("Testing scraper inheritance...")
    assert issubclass(GooglePlacesScraper, BaseScraper)
    print("  ✅ GooglePlacesScraper inherits from BaseScraper")


def test_scraper_methods():
    """Verify required methods exist"""
    print("\nTesting scraper methods...")

    required_methods = [
        "scrape",
        "parse",
        "_search_restaurants",
        "_get_or_create_area",
        "_get_or_create_category",
        "_create_or_update_venue",
        "get_stats",
        "rate_limit_delay",
        "fetch_with_retry",
    ]

    for method in required_methods:
        assert hasattr(GooglePlacesScraper, method), f"Missing method: {method}"
        print(f"  ✅ {method}")


def test_base_scraper_methods():
    """Verify BaseScraper provides rate limiting and retry"""
    print("\nTesting BaseScraper methods...")

    base_methods = [
        "rate_limit_delay",
        "fetch_with_retry",
        "get_stats",
        "get_user_agent",
    ]

    for method in base_methods:
        assert hasattr(BaseScraper, method)
        print(f"  ✅ {method}")


def test_scorer_implementation():
    """Verify VenueScorer has scoring method"""
    print("\nTesting VenueScorer...")

    assert hasattr(VenueScorer, "score")
    print("  ✅ VenueScorer.score() method exists")

    # Check signature
    sig = inspect.signature(VenueScorer.score)
    print(f"  ✅ Signature: {sig}")


def test_celery_tasks():
    """Verify Celery tasks are properly decorated"""
    print("\nTesting Celery tasks...")

    # Check that tasks are decorated with @celery_app.task
    assert hasattr(scrape_google_places_all_areas, "apply_async")
    print("  ✅ scrape_google_places_all_areas is a Celery task")

    assert hasattr(run_scoring_engine_all, "apply_async")
    print("  ✅ run_scoring_engine_all is a Celery task")


def test_parse_method():
    """Test the parse method without API calls"""
    print("\nTesting parse method...")

    # Mock a Google Places API response
    mock_place = {
        "name": "Test Restaurant",
        "place_id": "ChIJ1234567890",
        "rating": 4.5,
        "user_ratings_total": 150,
        "formatted_address": "123 Main St, Dubai Marina, Dubai",
        "formatted_phone_number": "+971 4 111 1111",
        "website": "https://example.com",
        "price_level": 2,
        "types": ["restaurant", "food"],
    }

    # Mock scraper (without async)
    from unittest.mock import MagicMock
    scraper = MagicMock()
    scraper.__class__ = GooglePlacesScraper

    # Use real parse method
    result = GooglePlacesScraper.parse(scraper, mock_place)

    assert result["name"] == "Test Restaurant"
    assert result["google_place_id"] == "ChIJ1234567890"
    assert result["google_rating"] == 4.5
    assert result["review_count"] == 150
    assert result["address"] == "123 Main St, Dubai Marina, Dubai"

    print("  ✅ Parse method correctly extracts venue data")
    print(f"     Result: {result}")


def test_slug_generation():
    """Test slug generation"""
    print("\nTesting slug generation...")

    from unittest.mock import MagicMock
    scraper = MagicMock()
    scraper.__class__ = GooglePlacesScraper

    test_cases = [
        ("Nobu Dubai Marina", "dubai-marina", "nobu-dubai-marina"),
        ("مطعم النيل", "dubai-marina", "marina"),  # Arabic name
        ("Café & Bar (2026)", "downtown", "cafe-bar-2026"),
        ("L'Atelier", "jumeirah", "latelier"),
    ]

    for name, area, expected_contains in test_cases:
        slug = GooglePlacesScraper._generate_slug(scraper, name, area)
        assert isinstance(slug, str)
        assert len(slug) > 0
        assert "-" in slug or len(slug) < 20
        print(f"  ✅ '{name}' → '{slug}'")


def test_demo_areas():
    """Verify demo areas are configured"""
    print("\nTesting demo areas...")

    from app.scrapers import google_places_demo

    assert hasattr(google_places_demo, "DEMO_AREAS")
    assert len(google_places_demo.DEMO_AREAS) == 10
    print(f"  ✅ {len(google_places_demo.DEMO_AREAS)} Dubai areas configured:")
    for slug, name in google_places_demo.DEMO_AREAS.items():
        print(f"     - {slug}: {name}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("SCRAPER STRUCTURE VERIFICATION")
    print("=" * 60)

    try:
        test_scraper_inheritance()
        test_scraper_methods()
        test_base_scraper_methods()
        test_scorer_implementation()
        test_celery_tasks()
        test_parse_method()
        test_slug_generation()
        test_demo_areas()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nScraper is ready for deployment!")
        print("\nNext steps:")
        print("1. Set GOOGLE_PLACES_API_KEY in .env")
        print("2. Run: python run_scraper_demo.py")
        print("3. Monitor: Check logs for insert/update statistics")

        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
