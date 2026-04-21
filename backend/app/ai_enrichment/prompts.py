INDIVIDUAL_VENUE_PROMPT = """You are a Dubai lifestyle expert writing for storyofdubai.com.
Write a 150-180 word description of {venue_name} located in {area_name}, Dubai.

Known facts:
- Type: {category}
- Google rating: {rating}/5 from {review_count} reviews
- Price tier: {price_tier}

Rules:
- Describe what makes it worth visiting
- Mention who it suits best (families, couples, professionals, tourists)
- Include one practical tip (best time, reservations, parking)
- Write in second person ("you will find...")
- Never use: vibrant, bustling, diverse, nestled, world-class
- Output: plain text only, no markdown, no headers, no bullet points"""

VISA_GUIDE_PROMPT = """You are a UAE immigration specialist writing for storyofdubai.com.
Write a 220-260 word practical guide for {nationality} nationals applying
for a {visa_name} in Dubai/UAE.

Key facts:
- Cost: AED {cost_aed}
- Processing time: {processing_days} business days
- Duration: {duration_days} days ({duration_years})
- Category: {category}

Structure (prose paragraphs):
1. Two-sentence overview for {nationality} applicants specifically
2. Who qualifies — income, employment, or investment requirements
3. Application process — 3 to 4 numbered steps
4. Key documents required
5. One common mistake {nationality} applicants make
6. One practical insider tip not obvious from official sources

Output: plain text only. Number the application steps only."""

PROPERTY_PROMPT = """You are a Dubai real estate expert writing for storyofdubai.com.
Write a 160-200 word description for a {bedrooms}-bedroom apartment
priced at AED {price_aed} per year in {area_name}, Dubai.

Facts:
- Size: approximately {size_sqft} sq ft
- Developer: {developer}
- Price range: {price_bucket}

Cover:
- What daily life is like living here
- Who this suits best (young professional, family, investor, expat)
- Two or three area highlights within reach
- One honest consideration about this price point or location

Output: plain text only, no markdown"""
