import pytest
from app.scoring.venue_scorer import VenueScorer, VenueScoreInput


@pytest.fixture
def scorer():
    return VenueScorer()


class TestVenueScorer:
    """Test Bayesian venue scoring algorithm — 100% coverage"""

    def test_perfect_venue(self, scorer):
        """Perfect venue: 5.0 rating, 10k reviews, fresh, tier 2, complete → ~100"""
        input_data = VenueScoreInput(
            id="venue_perfect",
            google_rating=5.0,
            review_count=10000,
            price_tier=2,
            days_since_last_review=0,
            has_photos=True,
            has_phone=True,
            has_website=True,
        )
        result = scorer.score(input_data)
        assert result.score == 100.0
        assert result.entity_id == "venue_perfect"
        assert "rating_quality" in result.breakdown
        assert "review_volume" in result.breakdown

    def test_excellent_venue(self, scorer):
        """Excellent venue: 4.8 rating, 200 reviews, fresh, tier 2, complete"""
        input_data = VenueScoreInput(
            id="venue_excellent",
            google_rating=4.8,
            review_count=200,
            price_tier=2,
            days_since_last_review=3,
            has_photos=True,
            has_phone=True,
            has_website=True,
        )
        result = scorer.score(input_data)
        assert 85.0 < result.score < 95.0  # Should be in high range
        assert sum(result.breakdown.values()) == result.score

    def test_new_venue_high_rating(self, scorer):
        """New venue: 5.0 rating but only 5 reviews → Bayesian dampens"""
        input_data = VenueScoreInput(
            id="venue_new",
            google_rating=5.0,
            review_count=5,
            price_tier=2,
            days_since_last_review=1,
            has_photos=True,
            has_phone=True,
            has_website=True,
        )
        result = scorer.score(input_data)
        # Bayesian should pull down from perfect (Bayesian dampens low trust)
        assert result.score < 85.0
        assert result.score > 60.0
        # Rating quality should be less than 30 (max)
        assert result.breakdown["rating_quality"] < 30.0

    def test_no_rating_no_reviews(self, scorer):
        """No rating, no reviews → 0 from rating/volume components"""
        input_data = VenueScoreInput(
            id="venue_no_data",
            google_rating=None,
            review_count=0,
            price_tier=2,
            days_since_last_review=1,
            has_photos=True,
            has_phone=True,
            has_website=True,
        )
        result = scorer.score(input_data)
        assert result.breakdown["rating_quality"] == 0.0
        assert result.breakdown["review_volume"] == 0.0
        # Should only have recency, price, completeness
        assert result.score == 15.0 + 15.0 + 20.0  # price + completeness + recency

    def test_stale_venue(self, scorer):
        """Stale venue: good rating but 365 days old → recency = 0"""
        input_data = VenueScoreInput(
            id="venue_stale",
            google_rating=4.5,
            review_count=100,
            price_tier=2,
            days_since_last_review=365,  # very stale
            has_photos=True,
            has_phone=True,
            has_website=True,
        )
        result = scorer.score(input_data)
        assert result.breakdown["recency"] == 0.0  # No recency points for 365 days
        assert result.score < 60.0  # Much lower due to no recency

    def test_recency_boundaries(self, scorer):
        """Test all recency time boundaries"""
        base_input = VenueScoreInput(
            id="venue_recency",
            google_rating=4.0,
            review_count=100,
            price_tier=2,
            days_since_last_review=0,
            has_photos=False,
            has_phone=False,
            has_website=False,
        )

        # 7 days = 20 points
        test_input = VenueScoreInput(**{**vars(base_input), "days_since_last_review": 7})
        result = scorer.score(test_input)
        assert result.breakdown["recency"] == 20.0

        # 30 days = 15 points
        test_input = VenueScoreInput(**{**vars(base_input), "days_since_last_review": 30})
        result = scorer.score(test_input)
        assert result.breakdown["recency"] == 15.0

        # 90 days = 10 points
        test_input = VenueScoreInput(**{**vars(base_input), "days_since_last_review": 90})
        result = scorer.score(test_input)
        assert result.breakdown["recency"] == 10.0

        # 180 days = 5 points
        test_input = VenueScoreInput(**{**vars(base_input), "days_since_last_review": 180})
        result = scorer.score(test_input)
        assert result.breakdown["recency"] == 5.0

        # 365+ days = 0 points
        test_input = VenueScoreInput(**{**vars(base_input), "days_since_last_review": 365})
        result = scorer.score(test_input)
        assert result.breakdown["recency"] == 0.0

    def test_price_tier_all_values(self, scorer):
        """Test all 4 price tiers return correct points"""
        base_input = VenueScoreInput(
            id="venue_tier",
            google_rating=4.0,
            review_count=100,
            days_since_last_review=7,
            has_photos=False,
            has_phone=False,
            has_website=False,
        )

        # Tier 1 (budget) = 10 points
        test_input = VenueScoreInput(**{**vars(base_input), "price_tier": 1})
        result = scorer.score(test_input)
        assert result.breakdown["price_value"] == 10.0

        # Tier 2 (mid-range) = 15 points (optimal)
        test_input = VenueScoreInput(**{**vars(base_input), "price_tier": 2})
        result = scorer.score(test_input)
        assert result.breakdown["price_value"] == 15.0

        # Tier 3 (upscale) = 12 points
        test_input = VenueScoreInput(**{**vars(base_input), "price_tier": 3})
        result = scorer.score(test_input)
        assert result.breakdown["price_value"] == 12.0

        # Tier 4 (luxury) = 8 points
        test_input = VenueScoreInput(**{**vars(base_input), "price_tier": 4})
        result = scorer.score(test_input)
        assert result.breakdown["price_value"] == 8.0

        # Unknown tier = 10 points (default)
        test_input = VenueScoreInput(**{**vars(base_input), "price_tier": None})
        result = scorer.score(test_input)
        assert result.breakdown["price_value"] == 10.0

    def test_completeness_breakdown(self, scorer):
        """Test completeness scoring: 5pts each for photos/phone/website"""
        base_input = VenueScoreInput(
            id="venue_complete",
            google_rating=4.0,
            review_count=100,
            price_tier=2,
            days_since_last_review=7,
        )

        # No completeness
        test_input = VenueScoreInput(**{**vars(base_input), "has_photos": False, "has_phone": False, "has_website": False})
        result = scorer.score(test_input)
        assert result.breakdown["completeness"] == 0.0

        # Only photos
        test_input = VenueScoreInput(**{**vars(base_input), "has_photos": True, "has_phone": False, "has_website": False})
        result = scorer.score(test_input)
        assert result.breakdown["completeness"] == 5.0

        # Photos + phone
        test_input = VenueScoreInput(**{**vars(base_input), "has_photos": True, "has_phone": True, "has_website": False})
        result = scorer.score(test_input)
        assert result.breakdown["completeness"] == 10.0

        # All complete
        test_input = VenueScoreInput(**{**vars(base_input), "has_photos": True, "has_phone": True, "has_website": True})
        result = scorer.score(test_input)
        assert result.breakdown["completeness"] == 15.0

    def test_score_bounds(self, scorer):
        """Score is always 0-100, never negative, never > 100"""
        test_cases = [
            # Worst case scenario
            VenueScoreInput(
                id="worst",
                google_rating=None,
                review_count=0,
                price_tier=None,
                days_since_last_review=999,
                has_photos=False,
                has_phone=False,
                has_website=False,
            ),
            # Perfect case
            VenueScoreInput(
                id="perfect",
                google_rating=5.0,
                review_count=10000,
                price_tier=2,
                days_since_last_review=0,
                has_photos=True,
                has_phone=True,
                has_website=True,
            ),
        ]

        for test_input in test_cases:
            result = scorer.score(test_input)
            assert 0.0 <= result.score <= 100.0

    def test_breakdown_sums_to_score(self, scorer):
        """Score breakdown components must sum to final score"""
        input_data = VenueScoreInput(
            id="venue_sum_test",
            google_rating=4.6,
            review_count=150,
            price_tier=2,
            days_since_last_review=15,
            has_photos=True,
            has_phone=True,
            has_website=False,
        )
        result = scorer.score(input_data)
        total = sum(result.breakdown.values())
        assert total == result.score

    def test_deterministic_scoring(self, scorer):
        """Same input always produces same score — no randomness"""
        input_data = VenueScoreInput(
            id="venue_deterministic",
            google_rating=4.7,
            review_count=175,
            price_tier=2,
            days_since_last_review=5,
            has_photos=True,
            has_phone=True,
            has_website=True,
        )

        # Score multiple times
        score1 = scorer.score(input_data).score
        score2 = scorer.score(input_data).score
        score3 = scorer.score(input_data).score

        assert score1 == score2 == score3

    def test_review_count_logarithmic(self, scorer):
        """Review volume should use logarithmic scale (diminishing returns)"""
        base_input = VenueScoreInput(
            id="venue_log",
            google_rating=4.0,
            price_tier=2,
            days_since_last_review=7,
            has_photos=False,
            has_phone=False,
            has_website=False,
        )

        # 10 reviews
        test1 = VenueScoreInput(**{**vars(base_input), "review_count": 10})
        score1 = scorer.score(test1).breakdown["review_volume"]

        # 100 reviews (10x more)
        test2 = VenueScoreInput(**{**vars(base_input), "review_count": 100})
        score2 = scorer.score(test2).breakdown["review_volume"]

        # 1000 reviews (100x more)
        test3 = VenueScoreInput(**{**vars(base_input), "review_count": 1000})
        score3 = scorer.score(test3).breakdown["review_volume"]

        # Scores should increase but with diminishing returns
        assert score1 < score2 < score3
        # The difference should decrease with scale
        assert (score2 - score1) > (score3 - score2)

    def test_bayesian_averaging(self, scorer):
        """Bayesian average weights by review count"""
        base_input = VenueScoreInput(
            id="venue_bayesian",
            google_rating=5.0,  # Perfect rating
            price_tier=2,
            days_since_last_review=7,
            has_photos=False,
            has_phone=False,
            has_website=False,
        )

        # 1 review — should be heavily dampened toward global mean
        test1 = VenueScoreInput(**{**vars(base_input), "review_count": 1})
        score1 = scorer.score(test1).breakdown["rating_quality"]

        # 50 reviews — should be closer to actual rating
        test2 = VenueScoreInput(**{**vars(base_input), "review_count": 50})
        score2 = scorer.score(test2).breakdown["rating_quality"]

        # 5000 reviews — should be at maximum (5.0 rating)
        test3 = VenueScoreInput(**{**vars(base_input), "review_count": 5000})
        score3 = scorer.score(test3).breakdown["rating_quality"]

        # Score should increase with more reviews (more trust)
        assert score1 < score2 < score3
        # Max is 30 pts for perfect 5.0 rating
        assert score3 == 30.0
