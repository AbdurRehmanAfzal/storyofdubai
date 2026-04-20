import math
from dataclasses import dataclass
from typing import Optional
from app.scoring.base import BaseScorer, ScoreResult

# Global constants for Bayesian averaging
GLOBAL_MEAN_RATING = 3.8
TRUST_REVIEW_COUNT = 50  # full trust at 50+ reviews

# Score weights (must sum to 100)
WEIGHTS = {
    "rating_quality": 30,
    "review_volume": 20,
    "recency": 20,
    "price_value": 15,
    "completeness": 15,
}


@dataclass
class VenueScoreInput:
    id: str
    google_rating: Optional[float]
    review_count: int
    price_tier: Optional[int]
    days_since_last_review: int
    has_photos: bool
    has_phone: bool
    has_website: bool
    response_rate: Optional[float] = None


class VenueScorer(BaseScorer):
    """Bayesian scoring algorithm for venues/restaurants.

    Combines multiple signals into a deterministic 0-100 score:
    - Rating quality (30pts): Bayesian average to handle low review counts
    - Review volume (20pts): Log-scale logarithmic distribution
    - Recency (20pts): Rewards fresh activity/reviews
    - Price value (15pts): Mid-tier venues score highest
    - Profile completeness (15pts): Bonus for complete business info
    """

    def score(self, entity: VenueScoreInput) -> ScoreResult:
        """Calculate venue score from input metrics"""
        breakdown = {}

        # 1. Rating Quality (30 pts) — Bayesian average
        # Addresses: rating bias toward high/low extremes with low review counts
        if entity.google_rating and entity.review_count > 0:
            # Weight by review count (asymptotically approaches 1.0 at 50+ reviews)
            weight = min(entity.review_count / TRUST_REVIEW_COUNT, 1.0)
            # Bayesian formula: weighted_rating = weight * actual + (1-weight) * global_mean
            bayesian_rating = (weight * entity.google_rating) + (
                (1 - weight) * GLOBAL_MEAN_RATING
            )
            pts = (bayesian_rating / 5.0) * WEIGHTS["rating_quality"]
        else:
            pts = 0.0
        breakdown["rating_quality"] = round(pts, 2)

        # 2. Review Volume (20 pts) — Logarithmic scale
        # Addresses: diminishing returns (100 reviews >> 50 reviews, but 1000 vs 950 is marginal)
        if entity.review_count > 0:
            # log10 scale: max points at 5000 reviews, logarithmic curve
            log_reviews = math.log10(entity.review_count + 1)
            log_max = math.log10(5000)  # reference max
            volume_ratio = min(log_reviews / log_max, 1.0)
            pts = volume_ratio * WEIGHTS["review_volume"]
        else:
            pts = 0.0
        breakdown["review_volume"] = round(pts, 2)

        # 3. Recency (20 pts) — Time decay
        # Addresses: stale data is less valuable than fresh signals
        days = entity.days_since_last_review
        if days <= 7:
            pts = 20.0  # Very fresh
        elif days <= 30:
            pts = 15.0  # Fresh (within month)
        elif days <= 90:
            pts = 10.0  # Moderate (within 3 months)
        elif days <= 180:
            pts = 5.0  # Stale (within 6 months)
        else:
            pts = 0.0  # Very stale
        breakdown["recency"] = pts

        # 4. Price-Value Tier (15 pts)
        # Addresses: mid-tier restaurants (2) are most popular & profitable
        # Tier 1 = budget, 2 = mid-range, 3 = upscale, 4 = luxury
        tier_pts_map = {
            1: 10.0,  # budget — some value
            2: 15.0,  # mid-range — optimal
            3: 12.0,  # upscale — less common, smaller audience
            4: 8.0,  # luxury — niche, fewer reviews
        }
        breakdown["price_value"] = tier_pts_map.get(entity.price_tier, 10.0)

        # 5. Profile Completeness (15 pts)
        # Addresses: complete business info improves trust & conversion
        pts = 0.0
        if entity.has_photos:
            pts += 5.0
        if entity.has_phone:
            pts += 5.0
        if entity.has_website:
            pts += 5.0
        breakdown["completeness"] = pts

        # Calculate final score
        total = sum(breakdown.values())
        final_score = round(self.clamp(total), 2)

        return ScoreResult(
            entity_id=entity.id,
            score=final_score,
            breakdown=breakdown,
        )
