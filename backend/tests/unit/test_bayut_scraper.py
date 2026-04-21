"""Unit tests for Bayut scraper."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.scrapers.bayut import BayutScraper, PRICE_BUCKETS


class TestBayutScraper:
    """Test suite for BayutScraper class."""

    @pytest.fixture
    def scraper(self):
        """Create a fresh scraper instance for each test."""
        return BayutScraper()

    def test_initialization(self, scraper):
        """Test scraper initializes with correct defaults."""
        assert scraper.DELAY == 3.0
        assert scraper.JITTER == 1.5
        assert scraper.properties_found == 0
        assert scraper.properties_parsed == 0
        assert scraper.requests_made == 0
        assert len(scraper.errors) == 0

    def test_get_price_bucket_under_50k(self, scraper):
        """Test price bucket calculation for under 50k."""
        assert scraper.get_price_bucket(25000) == "under-50k"
        assert scraper.get_price_bucket(0) == "under-50k"
        assert scraper.get_price_bucket(49999) == "under-50k"

    def test_get_price_bucket_50k_100k(self, scraper):
        """Test price bucket calculation for 50k-100k range."""
        assert scraper.get_price_bucket(50000) == "50k-100k"
        assert scraper.get_price_bucket(75000) == "50k-100k"
        assert scraper.get_price_bucket(99999) == "50k-100k"

    def test_get_price_bucket_100k_200k(self, scraper):
        """Test price bucket calculation for 100k-200k range."""
        assert scraper.get_price_bucket(100000) == "100k-200k"
        assert scraper.get_price_bucket(150000) == "100k-200k"
        assert scraper.get_price_bucket(199999) == "100k-200k"

    def test_get_price_bucket_200k_plus(self, scraper):
        """Test price bucket calculation for 200k+ range."""
        assert scraper.get_price_bucket(200000) == "200k-plus"
        assert scraper.get_price_bucket(500000) == "200k-plus"
        assert scraper.get_price_bucket(1000000) == "200k-plus"

    def test_get_price_bucket_boundary_values(self, scraper):
        """Test price bucket boundaries are exact."""
        # Test exact boundary values
        assert scraper.get_price_bucket(50000) == "50k-100k"  # 50k is start of 50k-100k
        assert scraper.get_price_bucket(49999) == "under-50k"  # Just under 50k
        assert scraper.get_price_bucket(100000) == "100k-200k"  # 100k is start of 100k-200k
        assert scraper.get_price_bucket(99999) == "50k-100k"  # Just under 100k
        assert scraper.get_price_bucket(200000) == "200k-plus"  # 200k is start of 200k-plus
        assert scraper.get_price_bucket(199999) == "100k-200k"  # Just under 200k

    def test_slugify_basic_text(self, scraper):
        """Test slugify handles basic English text."""
        assert scraper.slugify("Dubai Marina Apartment") == "dubai-marina-apartment"
        assert scraper.slugify("Test Property") == "test-property"

    def test_slugify_spaces(self, scraper):
        """Test slugify converts spaces to hyphens."""
        assert scraper.slugify("Two Word Name") == "two-word-name"
        assert scraper.slugify("Multiple   Spaces") == "multiple-spaces"

    def test_slugify_special_characters(self, scraper):
        """Test slugify removes special characters."""
        assert scraper.slugify("Luxury @ Villa!") == "luxury-villa"
        assert scraper.slugify("2-Bed, 3-Bath") == "2-bed-3-bath"
        assert scraper.slugify("Price: AED 100,000") == "price-aed-100000"

    def test_slugify_multiple_hyphens(self, scraper):
        """Test slugify collapses multiple hyphens."""
        assert scraper.slugify("multiple---hyphens") == "multiple-hyphens"

    def test_slugify_leading_trailing_spaces(self, scraper):
        """Test slugify strips leading/trailing spaces."""
        assert scraper.slugify("  padded text  ") == "padded-text"

    def test_slugify_length_limit(self, scraper):
        """Test slugify limits to 100 characters."""
        long_text = "a" * 150
        result = scraper.slugify(long_text)
        assert len(result) == 100

    def test_slugify_uppercase_to_lowercase(self, scraper):
        """Test slugify converts uppercase to lowercase."""
        assert scraper.slugify("UPPERCASE TEXT") == "uppercase-text"
        assert scraper.slugify("MixedCaseText") == "mixedcasetext"

    def test_slugify_arabic_characters_removed(self, scraper):
        """Test slugify removes Arabic characters (doesn't transliterate)."""
        # Arabic characters are removed by [^\w\s-] regex
        result = scraper.slugify("مطعم Restaurant")
        # Only "restaurant" remains after removing non-word chars
        assert "restaurant" in result

    @pytest.mark.asyncio
    async def test_parse_listing_valid_data(self, scraper):
        """Test parse_listing with complete property data."""
        # Mock listing element
        listing = AsyncMock()

        # Mock selectors
        title_el = AsyncMock()
        await title_el.inner_text() or AsyncMock(return_value="2BR Apartment")
        title_el.inner_text = AsyncMock(return_value="2BR Apartment")

        price_el = AsyncMock()
        price_el.inner_text = AsyncMock(return_value="AED 100,000")

        bed_el = AsyncMock()
        bed_el.inner_text = AsyncMock(return_value="2 Bedrooms")

        bath_el = AsyncMock()
        bath_el.inner_text = AsyncMock(return_value="2 Bathrooms")

        size_el = AsyncMock()
        size_el.inner_text = AsyncMock(return_value="1000 sqft")

        link_el = AsyncMock()
        link_el.get_attribute = AsyncMock(return_value="/property/123456/")

        listing.query_selector = AsyncMock(side_effect=lambda selector: {
            "h2, [class*='title']": title_el,
            "[class*='price']": price_el,
            "[aria-label*='bed'], [class*='bed']": bed_el,
            "[aria-label*='bath'], [class*='bath']": bath_el,
            "[aria-label*='sqft'], [class*='area']": size_el,
            "a[href*='/property/']": link_el,
        }.get(selector))

        result = await scraper.parse_listing(listing, "dubai-marina")

        assert result is not None
        assert result["title"] == "2BR Apartment"
        assert result["bedrooms"] == 2
        assert result["bathrooms"] == 2
        assert result["price_aed"] == 100000
        assert result["area_slug"] == "dubai-marina"
        assert result["price_bucket"] == "100k-200k"

    @pytest.mark.asyncio
    async def test_parse_listing_returns_none_for_zero_price(self, scraper):
        """Test parse_listing returns None when price is 0."""
        listing = AsyncMock()

        title_el = AsyncMock()
        title_el.inner_text = AsyncMock(return_value="Test Property")

        price_el = AsyncMock()
        price_el.inner_text = AsyncMock(return_value="No Price")  # No digits

        listing.query_selector = AsyncMock(side_effect=lambda selector: {
            "h2, [class*='title']": title_el,
            "[class*='price']": price_el,
        }.get(selector))

        result = await scraper.parse_listing(listing, "dubai-marina")

        assert result is None  # Should return None for zero price

    @pytest.mark.asyncio
    async def test_parse_listing_returns_none_for_missing_title(self, scraper):
        """Test parse_listing returns None when title is missing."""
        listing = AsyncMock()

        title_el = AsyncMock()
        title_el.inner_text = AsyncMock(return_value="")

        listing.query_selector = AsyncMock(return_value=title_el)

        result = await scraper.parse_listing(listing, "dubai-marina")

        assert result is None  # Should return None for missing title

    def test_scraper_inherits_from_base_scraper(self, scraper):
        """Test BayutScraper properly inherits from BaseScraper."""
        from app.scrapers.base import BaseScraper

        assert isinstance(scraper, BaseScraper)

    def test_scraper_has_required_methods(self, scraper):
        """Test scraper has all required methods."""
        assert hasattr(scraper, "scrape")
        assert hasattr(scraper, "parse")
        assert hasattr(scraper, "get_user_agent")
        assert hasattr(scraper, "rate_limit_delay")
        assert hasattr(scraper, "get_stats")

    def test_slugify_with_numbers(self, scraper):
        """Test slugify preserves numbers."""
        assert scraper.slugify("2BR-3BA-Dubai") == "2br-3ba-dubai"
        assert scraper.slugify("Apt 123") == "apt-123"

    def test_get_stats_includes_all_fields(self, scraper):
        """Test get_stats returns all required fields."""
        scraper.requests_made = 5
        scraper.errors = ["error1", "error2"]

        stats = scraper.get_stats()

        assert "requests_made" in stats
        assert "errors_count" in stats
        assert "duration_seconds" in stats
        assert stats["requests_made"] == 5
        assert stats["errors_count"] == 2

    def test_price_buckets_coverage(self, scraper):
        """Test all price bucket ranges are covered."""
        test_cases = [
            (0, "under-50k"),
            (25000, "under-50k"),
            (50000, "50k-100k"),
            (75000, "50k-100k"),
            (100000, "100k-200k"),
            (150000, "100k-200k"),
            (200000, "200k-plus"),
            (500000, "200k-plus"),
            (1000000, "200k-plus"),
        ]

        for price, expected_bucket in test_cases:
            result = scraper.get_price_bucket(price)
            assert result == expected_bucket, f"Price {price} should be in {expected_bucket}, got {result}"
