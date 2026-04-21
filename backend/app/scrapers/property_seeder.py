"""Property seeder - generates realistic Dubai property seed data."""
import re
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.venue import Area
from app.models.property import Property, Developer
import structlog

logger = structlog.get_logger()

DEVELOPERS = [
    {
        "name": "Emaar Properties",
        "slug": "emaar-properties",
        "established_year": 1997,
        "total_projects": 85,
    },
    {
        "name": "DAMAC Properties",
        "slug": "damac-properties",
        "established_year": 2002,
        "total_projects": 60,
    },
    {"name": "Nakheel", "slug": "nakheel", "established_year": 2000, "total_projects": 45},
    {"name": "Meraas", "slug": "meraas", "established_year": 2007, "total_projects": 30},
    {
        "name": "Dubai Properties",
        "slug": "dubai-properties",
        "established_year": 2004,
        "total_projects": 40,
    },
    {
        "name": "Sobha Realty",
        "slug": "sobha-realty",
        "established_year": 1976,
        "total_projects": 25,
    },
    {
        "name": "Azizi Developments",
        "slug": "azizi-developments",
        "established_year": 2007,
        "total_projects": 35,
    },
    {
        "name": "Binghatti Developers",
        "slug": "binghatti-developers",
        "established_year": 2008,
        "total_projects": 28,
    },
]

# area_slug → list of (bedrooms, price_aed, size_sqft, building_name)
PROPERTY_DATA = {
    "dubai-marina": [
        (1, 75000, 750, "Marina Gate"),
        (1, 85000, 820, "Cayan Tower"),
        (2, 120000, 1200, "Marina Gate"),
        (2, 145000, 1350, "Jumeirah Living"),
        (3, 200000, 1800, "Address Marina"),
        (3, 240000, 2100, "Marina Pinnacle"),
        (1, 65000, 680, "Marina Crown"),
        (2, 110000, 1100, "Elite Residence"),
        (2, 135000, 1250, "Marina Quays"),
        (3, 185000, 1750, "Damac Heights"),
        (1, 90000, 900, "Princess Tower"),
        (2, 160000, 1400, "23 Marina"),
        (4, 320000, 2800, "Sulafa Tower"),
        (1, 55000, 620, "Sparkle Towers"),
        (2, 125000, 1180, "The Waves"),
        (3, 210000, 1900, "Marina Residences"),
        (1, 78000, 770, "Marina Terrace"),
        (2, 140000, 1300, "Al Sahab Tower"),
        (1, 72000, 740, "Marina Towers"),
        (2, 118000, 1150, "Crescent Court"),
        (3, 225000, 2000, "Marina Heights"),
        (1, 68000, 700, "The Lagoons"),
        (2, 130000, 1280, "Venice Residences"),
        (4, 380000, 3100, "Gold Tower"),
        (1, 80000, 820, "Blue Waters Tower"),
        (2, 150000, 1380, "Concorde Tower"),
        (1, 70000, 710, "Tower Gardens"),
        (2, 140000, 1320, "Lagoon Tower"),
        (3, 230000, 2050, "Waterfront Residences"),
        (4, 390000, 3200, "Marina Crown"),
        (1, 82000, 840, "Beacon Towers"),
        (2, 155000, 1400, "Crystal Towers"),
        (3, 240000, 2100, "Emerald Heights"),
        (1, 76000, 780, "Sapphire Tower"),
        (2, 148000, 1360, "Diamond Court"),
        (3, 235000, 2080, "Golden Towers"),
        (4, 400000, 3300, "Luxury Marina"),
    ],
    "downtown-dubai": [
        (1, 95000, 800, "Burj Views"),
        (1, 110000, 880, "29 Boulevard"),
        (2, 165000, 1400, "Burj Views"),
        (2, 190000, 1600, "Opera Grand"),
        (3, 280000, 2200, "Il Primo"),
        (3, 310000, 2500, "Address Downtown"),
        (1, 88000, 760, "Boulevard Crescent"),
        (2, 155000, 1350, "Claren Tower"),
        (4, 450000, 3200, "The Residences"),
        (1, 105000, 850, "Standpoint"),
        (2, 175000, 1500, "South Ridge"),
        (3, 260000, 2100, "Executive Towers"),
        (1, 92000, 790, "Burj Khalifa District"),
        (2, 180000, 1550, "8 Boulevard Walk"),
        (3, 290000, 2300, "Act One Act Two"),
        (1, 98000, 820, "Downtown View"),
        (2, 170000, 1420, "Boulevard Heights"),
        (3, 295000, 2280, "Infinity Tower"),
        (1, 102000, 880, "Skyrise Residences"),
        (2, 185000, 1580, "Opera Residences"),
        (4, 480000, 3350, "Grand Tower"),
        (1, 96000, 810, "Khalifa Towers"),
        (2, 165000, 1380, "Symphony Towers"),
        (3, 275000, 2150, "Downtown Living"),
        (1, 100000, 850, "Elite Downtown"),
        (2, 170000, 1500, "Prestige Plaza"),
        (3, 300000, 2350, "Summit Tower"),
        (4, 500000, 3400, "Downtown Luxury"),
        (1, 94000, 800, "City View"),
        (2, 175000, 1550, "Boulevard View"),
        (3, 285000, 2250, "Skyline Tower"),
        (1, 99000, 840, "Metropolitan"),
        (2, 180000, 1600, "Urban Residences"),
        (3, 310000, 2400, "Premium Tower"),
    ],
    "business-bay": [
        (1, 65000, 700, "Damac Maison"),
        (1, 72000, 740, "The Pad"),
        (2, 105000, 1100, "Paramount Hotel"),
        (2, 118000, 1200, "Bay Square"),
        (3, 175000, 1700, "Aykon City"),
        (1, 60000, 650, "Executive Bay"),
        (2, 98000, 1050, "Churchill Residency"),
        (3, 160000, 1600, "The Oberoi"),
        (1, 68000, 710, "Capital Bay"),
        (2, 112000, 1150, "Anwa Aria"),
        (3, 185000, 1750, "Millennium Binghatti"),
        (1, 75000, 760, "SLS Dubai"),
        (2, 125000, 1250, "VERA Residences"),
        (4, 280000, 2600, "Opus Tower"),
        (1, 70000, 720, "Bay Heights"),
        (2, 110000, 1120, "Bay Square Residences"),
        (3, 180000, 1720, "Aykon Towers"),
        (1, 62000, 680, "Executive Towers"),
        (2, 100000, 1080, "Business District"),
        (3, 170000, 1650, "Commerce Court"),
        (1, 74000, 750, "Bay Center"),
        (2, 120000, 1200, "Marina Heights"),
        (4, 290000, 2650, "Grand Bay Tower"),
        (1, 76000, 760, "Executive Towers"),
        (2, 128000, 1280, "Bay Residence"),
        (3, 188000, 1800, "Commerce Plaza"),
        (4, 310000, 2750, "Business Tower"),
        (1, 73000, 740, "Corporate Bay"),
        (2, 114000, 1180, "Business View"),
        (3, 175000, 1680, "Bay Center Tower"),
        (1, 71000, 730, "District Plaza"),
        (2, 122000, 1240, "Bay Heights"),
        (4, 300000, 2700, "Commercial Tower"),
    ],
    "jumeirah-village-circle": [
        (1, 42000, 650, "Belgravia Heights"),
        (1, 48000, 700, "Park Lane"),
        (2, 70000, 1050, "Belgravia Heights"),
        (2, 78000, 1100, "District One"),
        (3, 110000, 1600, "Plazzo Heights"),
        (1, 38000, 600, "Bloom Towers"),
        (2, 65000, 980, "Catch Residences"),
        (3, 95000, 1450, "Atria Residences"),
        (1, 45000, 670, "Diamond Views"),
        (2, 72000, 1080, "Genesis by Meraki"),
        (1, 52000, 730, "Oxford Boulevard"),
        (2, 82000, 1150, "AG Square"),
        (3, 115000, 1650, "Sobha Hartland"),
        (1, 40000, 620, "Circle Living"),
        (1, 44000, 660, "Village Heights"),
        (2, 75000, 1080, "Sector 1"),
        (3, 120000, 1700, "Cambridge Court"),
        (1, 46000, 700, "Crystal Towers"),
        (2, 80000, 1120, "Veranda Residences"),
        (3, 125000, 1800, "Mayfair Towers"),
        (1, 41000, 640, "Community Park"),
        (2, 68000, 1000, "Lifestyle Apartments"),
        (3, 105000, 1500, "Village Square"),
        (1, 50000, 750, "Oxford Circle"),
        (2, 85000, 1180, "Watercrest Towers"),
        (1, 43000, 650, "Village Park"),
        (2, 73000, 1090, "District Residences"),
        (3, 118000, 1750, "Cambridge Heights"),
        (1, 49000, 720, "Circle Tower"),
        (2, 84000, 1160, "Sector 2"),
        (3, 122000, 1800, "Oxford Heights"),
        (1, 47000, 710, "Community Towers"),
        (2, 76000, 1100, "Village Heights"),
        (3, 110000, 1600, "Residential Complex"),
    ],
    "palm-jumeirah": [
        (1, 130000, 950, "Tiara Residences"),
        (2, 200000, 1600, "Marina Residences"),
        (3, 320000, 2400, "Oceana Residences"),
        (4, 520000, 3500, "Signature Villas"),
        (2, 220000, 1750, "The Shoreline"),
        (3, 350000, 2600, "Golden Mile"),
        (1, 145000, 1000, "Palm Views"),
        (2, 240000, 1850, "Fairmont Residences"),
        (4, 600000, 4000, "One Palm"),
        (3, 380000, 2800, "Atlantis The Royal"),
        (2, 210000, 1700, "Balqis Residence"),
        (1, 125000, 900, "Azure Residences"),
        (1, 140000, 980, "Palm Heights"),
        (2, 230000, 1800, "Crescent Court"),
        (3, 370000, 2750, "Emerald Tower"),
        (4, 580000, 3800, "Royal Villas"),
        (1, 135000, 950, "Waterfront View"),
        (2, 215000, 1750, "Horizon Residences"),
        (3, 360000, 2700, "Beachfront Tower"),
        (1, 150000, 1050, "Palm Strand"),
        (2, 250000, 1900, "Crescent Moon"),
        (4, 620000, 4100, "Palm Estates"),
        (1, 138000, 970, "Lagoon View"),
        (2, 225000, 1800, "Island Residences"),
        (3, 375000, 2800, "Palm Tower"),
        (4, 610000, 4050, "Peninsula Villas"),
        (1, 142000, 1000, "Waterfront Paradise"),
        (2, 235000, 1850, "Beach Living"),
        (3, 390000, 2900, "Luxury Towers"),
        (1, 148000, 1040, "Island Court"),
        (2, 245000, 1900, "Gulf View"),
        (4, 640000, 4200, "Prestige Estates"),
    ],
    "jumeirah": [
        (2, 130000, 1400, "Jumeirah 1 Villa"),
        (3, 200000, 2200, "Jumeirah 2 Villa"),
        (4, 300000, 3000, "Jumeirah 3 Villa"),
        (2, 115000, 1300, "Jumeirah Bay"),
        (3, 185000, 2000, "La Mer Residences"),
        (4, 280000, 2800, "Sunset Mall Area"),
        (2, 140000, 1500, "Sunset Beach"),
        (3, 220000, 2300, "Kite Beach Residences"),
        (2, 135000, 1420, "Beach House"),
        (3, 210000, 2150, "Seaside Villas"),
        (4, 320000, 3100, "Crescent Beach"),
        (2, 125000, 1350, "Oceanfront Tower"),
        (3, 195000, 2100, "Marina View"),
        (4, 310000, 3050, "Sunset Manor"),
        (2, 145000, 1550, "Beachfront Residences"),
        (3, 225000, 2400, "Waterfront Villas"),
        (2, 148000, 1600, "Coastal View"),
        (3, 230000, 2450, "Oceanside Towers"),
        (4, 325000, 3200, "Beachfront Estate"),
        (2, 138000, 1480, "Seaside Residences"),
        (3, 215000, 2300, "Marina Towers"),
        (4, 300000, 3000, "Tropical Villas"),
        (2, 142000, 1520, "Shore View"),
        (3, 220000, 2350, "Island Tower"),
    ],
    "al-barsha": [
        (1, 48000, 720, "Al Barsha Mall Area"),
        (2, 75000, 1100, "Al Barsha 1"),
        (3, 110000, 1600, "Al Barsha South"),
        (1, 42000, 660, "Al Barsha Heights"),
        (2, 68000, 980, "Tecom District"),
        (3, 95000, 1450, "Arjan"),
        (1, 52000, 750, "Al Barsha 3"),
        (2, 80000, 1150, "Dubai Science Park"),
        (1, 46000, 700, "Barsha Heights"),
        (2, 72000, 1050, "Barsha Center"),
        (3, 105000, 1550, "Barsha South Towers"),
        (1, 44000, 680, "Tech District"),
        (2, 70000, 1020, "Tecom Towers"),
        (3, 100000, 1500, "Science Park Residences"),
        (1, 50000, 730, "Barsha Tower"),
        (2, 78000, 1130, "Central Park"),
        (3, 115000, 1700, "South Bay Tower"),
        (1, 48000, 740, "Tech Heights"),
        (2, 76000, 1070, "Science Center"),
        (3, 108000, 1550, "Park Tower"),
        (1, 47000, 720, "Barsha Court"),
        (2, 74000, 1040, "Center Residences"),
        (3, 102000, 1480, "South Tower"),
        (1, 51000, 760, "Advanced Park"),
        (2, 82000, 1160, "Research Tower"),
        (3, 118000, 1750, "Innovation Hub"),
    ],
    "dubai-hills": [
        (1, 72000, 800, "Park Heights"),
        (2, 120000, 1300, "Mulberry"),
        (3, 185000, 1900, "Golfville"),
        (4, 290000, 2700, "Sidra Villas"),
        (2, 130000, 1400, "Collective"),
        (3, 200000, 2000, "Maple"),
        (1, 78000, 850, "Acacia"),
        (2, 115000, 1250, "Socio"),
        (4, 320000, 3000, "Emerald Hills"),
        (3, 195000, 1950, "Ellington House"),
        (1, 75000, 820, "Hills Tower"),
        (2, 125000, 1350, "Oak Heights"),
        (3, 190000, 1950, "Golf View Residences"),
        (4, 310000, 2850, "Villa Hills"),
        (1, 80000, 880, "Summit Residences"),
        (2, 135000, 1450, "Birch Gardens"),
        (3, 210000, 2100, "Elevation Tower"),
        (4, 340000, 3100, "Prestige Villas"),
        (2, 140000, 1500, "Garden Hills"),
        (3, 220000, 2200, "Pinnacle Tower"),
        (1, 77000, 840, "Valley View"),
        (2, 142000, 1520, "Hillside Residences"),
        (3, 225000, 2250, "Ridge Tower"),
        (4, 350000, 3150, "Mountain Villas"),
        (1, 82000, 900, "Heights Court"),
        (2, 145000, 1580, "Altitude Residences"),
        (3, 235000, 2350, "Summit Heights"),
        (1, 74000, 810, "Green Valley"),
        (2, 138000, 1480, "Nature View"),
        (3, 205000, 2050, "Forest Tower"),
    ],
    "jbr": [
        (1, 48000, 650, "JBR Towers"),
        (2, 75000, 1050, "Beach Apartments"),
        (3, 110000, 1400, "The Walk Residences"),
        (1, 42000, 600, "Bayshore Towers"),
        (2, 68000, 950, "Marina Terrace"),
        (3, 95000, 1300, "Sunset Tower"),
        (1, 52000, 720, "Paradise Lake"),
        (2, 80000, 1100, "The Promenade"),
        (1, 46000, 630, "Beach Tower"),
        (2, 72000, 1000, "Waterfront Apartments"),
        (3, 105000, 1350, "Crescent Towers"),
        (1, 44000, 620, "Shoreside Living"),
        (2, 70000, 980, "Beachfront Plaza"),
        (3, 100000, 1300, "Walk Residences"),
        (1, 50000, 700, "Bayshore Center"),
        (2, 78000, 1080, "Lagoon Towers"),
        (3, 115000, 1450, "Marina View Tower"),
        (1, 45000, 610, "Beach Central"),
        (2, 73000, 1020, "Shoreline Tower"),
        (3, 108000, 1380, "Waterfront View"),
        (1, 48000, 660, "Coastal Residences"),
        (2, 76000, 1050, "Wave Tower"),
        (3, 112000, 1420, "Horizon Towers"),
        (1, 47000, 650, "Beachside Court"),
        (2, 74000, 1030, "Tides Residences"),
        (3, 110000, 1400, "Ocean View Tower"),
    ],
    "difc": [
        (1, 85000, 800, "DIFC Gate Tower"),
        (2, 145000, 1300, "The Gate Apartments"),
        (3, 210000, 1800, "DIFC Residences"),
        (1, 95000, 850, "Downtown View"),
        (2, 165000, 1450, "Liberty House"),
        (3, 235000, 1950, "Park Heights"),
        (2, 155000, 1380, "Promenade Residences"),
        (3, 220000, 1850, "Central Park"),
        (1, 90000, 820, "Financial Tower"),
        (2, 150000, 1350, "Business Plaza"),
        (3, 215000, 1850, "Executive Residences"),
        (1, 92000, 840, "DIFC View"),
        (2, 160000, 1420, "Commerce Tower"),
        (3, 230000, 1920, "Tower Heights"),
        (2, 158000, 1400, "Pavilion Residences"),
        (3, 225000, 1880, "Metropolitan Tower"),
        (1, 88000, 810, "Skyline Towers"),
        (2, 148000, 1320, "Financial Park"),
        (3, 240000, 2000, "Prestige Tower"),
        (1, 86000, 830, "Investor's Tower"),
        (2, 152000, 1370, "Finance Court"),
        (3, 245000, 2050, "Banking Tower"),
        (1, 89000, 860, "District Tower"),
        (2, 162000, 1480, "Market Plaza"),
        (3, 255000, 2150, "Trade Center"),
        (2, 157000, 1410, "Commerce Residences"),
        (3, 248000, 2080, "Business Heights"),
        (1, 91000, 880, "Corporate Tower"),
        (2, 167000, 1520, "Executive Plaza"),
        (3, 260000, 2200, "Premium Business"),
    ],
}


def get_price_bucket(price_aed: int) -> str:
    """Determine price bucket from AED amount."""
    if price_aed < 50000:
        return "under-50k"
    if price_aed < 100000:
        return "50k-100k"
    if price_aed < 200000:
        return "100k-200k"
    return "200k-plus"


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:100]


def seed_developers(db: Session) -> dict:
    """Seed developers and return slug→id mapping."""
    dev_map = {}
    for dev_data in DEVELOPERS:
        try:
            existing = db.execute(
                select(Developer).where(Developer.slug == dev_data["slug"])
            ).scalar_one_or_none()
            if not existing:
                dev = Developer(id=str(uuid.uuid4()), **dev_data, ai_summary="", is_active=True)
                db.add(dev)
                db.flush()
                dev_map[dev_data["slug"]] = dev.id
            else:
                dev_map[dev_data["slug"]] = existing.id
        except Exception as e:
            logger.warning("developer_seed_error", slug=dev_data["slug"], error=str(e))
            # Map to None if error
            dev_map[dev_data["slug"]] = None

    try:
        db.commit()
        logger.info("developers_seeded", count=len(dev_map))
    except Exception as e:
        logger.warning("developers_commit_error", error=str(e))
        db.rollback()

    return dev_map


def seed_properties(db: Session) -> dict:
    """Seed all property records across areas."""
    import random

    dev_map = seed_developers(db)
    dev_slugs = list(dev_map.keys())

    saved = 0
    skipped = 0
    area_errors = 0

    for area_slug, properties in PROPERTY_DATA.items():
        area = db.execute(
            select(Area).where(Area.slug == area_slug)
        ).scalar_one_or_none()

        if not area:
            logger.warning("property_area_not_found", area_slug=area_slug)
            area_errors += 1
            skipped += len(properties)
            continue

        for bedrooms, price_aed, size_sqft, building_name in properties:
            slug = slugify(
                f"{building_name}-{area_slug}-{bedrooms}br-{price_aed//1000}k"
            )

            existing = db.execute(
                select(Property).where(Property.slug == slug)
            ).scalar_one_or_none()

            if existing:
                # Update existing property
                existing.price_aed = price_aed
                existing.price_bucket = get_price_bucket(price_aed)
                db.merge(existing)
            else:
                # Create new property
                dev_slug = random.choice(dev_slugs)
                developer_id = dev_map.get(dev_slug)  # Could be None if developer not found
                prop = Property(
                    id=str(uuid.uuid4()),
                    title=f"{bedrooms} Bedroom Apartment in {building_name}",
                    slug=slug,
                    area_id=area.id,
                    bedrooms=bedrooms,
                    bathrooms=bedrooms,
                    size_sqft=float(size_sqft),
                    price_aed=price_aed,
                    price_bucket=get_price_bucket(price_aed),
                    property_type="apartment",
                    developer_id=developer_id,
                    composite_score=round(50 + (price_aed / 600000) * 40, 1),
                    affiliate_url=f"https://www.propertyfinder.ae/search?q={area_slug}",
                    description="",
                    is_active=True,
                )
                db.add(prop)
                saved += 1

    db.commit()
    logger.info(
        "properties_seeded",
        saved=saved,
        skipped=skipped,
        area_errors=area_errors,
        total_areas=len(PROPERTY_DATA),
    )
    return {"saved": saved, "skipped": skipped, "area_errors": area_errors}
