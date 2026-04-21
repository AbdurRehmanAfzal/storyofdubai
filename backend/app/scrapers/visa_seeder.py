"""Visa seeder - generates 400 visa guide seed data (50 nationalities × 8 visa types)."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.visa import Nationality, VisaType, VisaNationalityGuide
import uuid

NATIONALITIES = [
    {"name": "Pakistani", "slug": "pakistani", "iso_code": "PK"},
    {"name": "Indian", "slug": "indian", "iso_code": "IN"},
    {"name": "British", "slug": "british", "iso_code": "GB"},
    {"name": "American", "slug": "american", "iso_code": "US"},
    {"name": "Australian", "slug": "australian", "iso_code": "AU"},
    {"name": "Canadian", "slug": "canadian", "iso_code": "CA"},
    {"name": "German", "slug": "german", "iso_code": "DE"},
    {"name": "French", "slug": "french", "iso_code": "FR"},
    {"name": "Chinese", "slug": "chinese", "iso_code": "CN"},
    {"name": "Russian", "slug": "russian", "iso_code": "RU"},
    {"name": "Egyptian", "slug": "egyptian", "iso_code": "EG"},
    {"name": "Filipino", "slug": "filipino", "iso_code": "PH"},
    {"name": "Bangladeshi", "slug": "bangladeshi", "iso_code": "BD"},
    {"name": "Sri Lankan", "slug": "sri-lankan", "iso_code": "LK"},
    {"name": "Nepalese", "slug": "nepalese", "iso_code": "NP"},
    {"name": "Nigerian", "slug": "nigerian", "iso_code": "NG"},
    {"name": "South African", "slug": "south-african", "iso_code": "ZA"},
    {"name": "Kenyan", "slug": "kenyan", "iso_code": "KE"},
    {"name": "Turkish", "slug": "turkish", "iso_code": "TR"},
    {"name": "Iranian", "slug": "iranian", "iso_code": "IR"},
    {"name": "Jordanian", "slug": "jordanian", "iso_code": "JO"},
    {"name": "Lebanese", "slug": "lebanese", "iso_code": "LB"},
    {"name": "Saudi", "slug": "saudi", "iso_code": "SA"},
    {"name": "Kuwaiti", "slug": "kuwaiti", "iso_code": "KW"},
    {"name": "Qatari", "slug": "qatari", "iso_code": "QA"},
    {"name": "Bahraini", "slug": "bahraini", "iso_code": "BH"},
    {"name": "Omani", "slug": "omani", "iso_code": "OM"},
    {"name": "Moroccan", "slug": "moroccan", "iso_code": "MA"},
    {"name": "Algerian", "slug": "algerian", "iso_code": "DZ"},
    {"name": "Italian", "slug": "italian", "iso_code": "IT"},
    {"name": "Spanish", "slug": "spanish", "iso_code": "ES"},
    {"name": "Dutch", "slug": "dutch", "iso_code": "NL"},
    {"name": "Swedish", "slug": "swedish", "iso_code": "SE"},
    {"name": "Norwegian", "slug": "norwegian", "iso_code": "NO"},
    {"name": "Danish", "slug": "danish", "iso_code": "DK"},
    {"name": "Swiss", "slug": "swiss", "iso_code": "CH"},
    {"name": "Japanese", "slug": "japanese", "iso_code": "JP"},
    {"name": "South Korean", "slug": "south-korean", "iso_code": "KR"},
    {"name": "Singaporean", "slug": "singaporean", "iso_code": "SG"},
    {"name": "Malaysian", "slug": "malaysian", "iso_code": "MY"},
    {"name": "Thai", "slug": "thai", "iso_code": "TH"},
    {"name": "Indonesian", "slug": "indonesian", "iso_code": "ID"},
    {"name": "Vietnamese", "slug": "vietnamese", "iso_code": "VN"},
    {"name": "Brazilian", "slug": "brazilian", "iso_code": "BR"},
    {"name": "Mexican", "slug": "mexican", "iso_code": "MX"},
    {"name": "Argentinian", "slug": "argentinian", "iso_code": "AR"},
    {"name": "Colombian", "slug": "colombian", "iso_code": "CO"},
    {"name": "Ukrainian", "slug": "ukrainian", "iso_code": "UA"},
    {"name": "Polish", "slug": "polish", "iso_code": "PL"},
    {"name": "Romanian", "slug": "romanian", "iso_code": "RO"},
]

VISA_TYPES = [
    {
        "name": "Tourist Visa 30 Days",
        "slug": "tourist-visa-30-days",
        "category": "tourist",
        "duration_days": 30,
        "cost_aed": 350,
        "processing_days": 3,
        "ai_guide": "Single or multiple entry tourist visa valid for 30 days. Quick processing, valid for tourism and business visits.",
    },
    {
        "name": "Tourist Visa 60 Days",
        "slug": "tourist-visa-60-days",
        "category": "tourist",
        "duration_days": 60,
        "cost_aed": 650,
        "processing_days": 3,
        "ai_guide": "Extended tourist visa valid for 60 days. Ideal for longer stays and exploration of UAE.",
    },
    {
        "name": "Employment Visa",
        "slug": "employment-visa",
        "category": "employment",
        "duration_days": 730,
        "cost_aed": 1200,
        "processing_days": 10,
        "ai_guide": "Work visa sponsored by UAE employer, valid 2 years. Requires job offer and employer sponsorship.",
    },
    {
        "name": "Investor Visa 3 Years",
        "slug": "investor-visa-3-years",
        "category": "investor",
        "duration_days": 1095,
        "cost_aed": 3700,
        "processing_days": 15,
        "ai_guide": "Business investor visa for 3 years. Requires minimum investment and business plan.",
    },
    {
        "name": "Golden Visa 10 Years",
        "slug": "golden-visa-10-years",
        "category": "investor",
        "duration_days": 3650,
        "cost_aed": 4500,
        "processing_days": 30,
        "ai_guide": "Long-term residency golden visa valid 10 years. Premium visa for investors and professionals.",
    },
    {
        "name": "Freelancer Visa",
        "slug": "freelancer-visa",
        "category": "freelancer",
        "duration_days": 365,
        "cost_aed": 7500,
        "processing_days": 20,
        "ai_guide": "Self-employment visa for freelancers and consultants. Allows independent work in UAE.",
    },
    {
        "name": "Student Visa",
        "slug": "student-visa",
        "category": "student",
        "duration_days": 365,
        "cost_aed": 900,
        "processing_days": 7,
        "ai_guide": "Student visa for tertiary education in UAE. Valid for full duration of study program.",
    },
    {
        "name": "Retirement Visa 5 Years",
        "slug": "retirement-visa-5-years",
        "category": "retirement",
        "duration_days": 1825,
        "cost_aed": 3500,
        "processing_days": 20,
        "ai_guide": "Retirement visa for pensioners, valid 5 years. Requires proof of regular income/savings.",
    },
]


def seed_nationalities(db: Session) -> int:
    """Seed nationalities and return count of new records."""
    count = 0
    for nat_data in NATIONALITIES:
        existing = db.execute(
            select(Nationality).where(Nationality.slug == nat_data["slug"])
        ).scalar_one_or_none()
        if not existing:
            db.add(Nationality(id=str(uuid.uuid4()), **nat_data, is_active=True))
            count += 1
    db.commit()
    return count


def seed_visa_types(db: Session) -> int:
    """Seed visa types and return count of new records."""
    count = 0
    for vt_data in VISA_TYPES:
        existing = db.execute(
            select(VisaType).where(VisaType.slug == vt_data["slug"])
        ).scalar_one_or_none()
        if not existing:
            db.add(VisaType(id=str(uuid.uuid4()), **vt_data, is_active=True))
            count += 1
    db.commit()
    return count


def seed_visa_guides(db: Session) -> int:
    """Seed visa nationality guides (cross-product) and return count of new records."""
    count = 0
    nationalities = db.execute(select(Nationality)).scalars().all()
    visa_types = db.execute(select(VisaType)).scalars().all()

    for nat in nationalities:
        for vt in visa_types:
            existing = db.execute(
                select(VisaNationalityGuide).where(
                    VisaNationalityGuide.nationality_id == nat.id,
                    VisaNationalityGuide.visa_type_id == vt.id,
                )
            ).scalar_one_or_none()
            if not existing:
                # Generate composite slug from nationality + visa type
                guide_slug = f"{nat.slug}-{vt.slug}"
                db.add(
                    VisaNationalityGuide(
                        id=str(uuid.uuid4()),
                        nationality_id=nat.id,
                        visa_type_id=vt.id,
                        slug=guide_slug,
                    )
                )
                count += 1

    db.commit()
    return count
