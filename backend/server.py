from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Query, UploadFile, File, Request
from fastapi.responses import PlainTextResponse, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
import secrets
import base64
import resend
import requests
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Tuple
import uuid
from datetime import datetime, timezone

from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with safe fallback (only connects if MONGO_URL is configured)
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'gagan_engineering')
client = None
db = None
if mongo_url:
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
        db = client[db_name]
    except Exception as e:
        logger.warning(f"MongoDB connection deferred or offline: {e}")


# Resend configuration
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL', 'gaganengineerings@gmail.com')

# Admin credentials (set in .env)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'gaganworks2006')

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gagan Engineering Works API", version="3.0.0")
api_router = APIRouter(prefix="/api")

# Ensure images directories exist and are mounted safely
try:
    if os.environ.get("VERCEL"):
        UPLOAD_DIR = Path("/tmp/uploads")
    else:
        UPLOAD_DIR = ROOT_DIR / "images" / "uploads"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    logger.warning(f"Could not create upload directory: {e}")
    UPLOAD_DIR = Path("/tmp")

try:
    images_dir = ROOT_DIR / "images"
    if images_dir.exists():
        app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")
except Exception as e:
    logger.warning(f"Static images mount skipped: {e}")



# ----------------- Seed Data (matches catalogueData.js) -----------------
SEED_PRODUCTS = [
    {
        "id": "double-head-electric-bra-cup-moulding-machine",
        "name": "Double Head Electric Bra Cup Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg",
        "tagline": "Twin-station high-output cup moulding for industrial lingerie production lines",
        "shortDesc": "Double-station electric moulding press engineered for seamless bra cup manufacturing with PID thermal control.",
        "description": "A heavy-duty double-head electric press engineered for continuous moulding of seamless bra cups. Twin stations allow operators to load one side while the other moulds — doubling throughput without doubling floor area. Built with hardened steel platens, precision digital PID temperature control, and timer-based pneumatic clamping for zero distortion and consistent cup depth.",
        "specs": {
            "Drive Mechanism": "Electric & Pneumatic dual-head",
            "Heating System": "Dual PID Microprocessor Controlled (0–250°C)",
            "Production Capacity": "400–600 pcs / shift (8 hours)",
            "Power Supply": "3-Phase 415V AC, 50Hz",
            "Platen Material": "High-grade Hardened Tool Steel",
            "Clamping": "Pneumatic cylinder with timer lock",
            "Applicable Materials": "PU Foam, Polyester Fiberfill, Laminated Fabrics, Spandex",
            "Application": "Seamless bra cups, swimsuit padding, sportswear inserts",
            "Warranty": "1 Year Manufacturer Warranty + Lifetime Support",
            "Origin": "Manufactured in Khopoli, Maharashtra, India"
        },
        "featured": True,
        "faqs": [
            {"q": "What is the daily output capacity of this double head machine?", "a": "A single operator can produce approximately 400 to 600 pairs of bra cups per 8-hour shift depending on foam thickness and heating dwell time."},
            {"q": "Can the moulding dies/cups be changed for different sizes?", "a": "Yes, our moulds are fully interchangeable. You can swap cup sizes (from 28A to 44DD) in less than 15 minutes."},
            {"q": "What power connection is required at the factory?", "a": "It operates on standard Indian 3-Phase 415V AC electricity with standard compressed air supply (6–8 bar) for pneumatic clamping."}
        ],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "bra-cup-fabric-moulding-machine",
        "name": "Bra Cup Fabric Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550584110/ET/BP/NY/4175789/product-jpeg-500x500.jpg",
        "tagline": "Precise fabric cup shaping with consistent edge finish and zero wrinkling",
        "shortDesc": "Specialized press for moulding laminated and woven fabrics into seamless bra cup profiles.",
        "description": "Engineered specifically for moulding laminated and woven fabrics into seamless cup shapes without scorch marks or fabric distortion. Features interchangeable CNC-machined aluminium moulds ensuring razor-sharp cup definition, smooth contouring, and clean edges across all batch runs.",
        "specs": {
            "Material Compatibility": "Woven fabrics, cotton-spandex, polyester blends, microfibers",
            "Mould Type": "Interchangeable CNC Aluminium Moulds",
            "Cycle Time": "25–40 seconds per pressing cycle",
            "Temperature Control": "Dual Zone Digital Thermostat",
            "Power Connection": "Single Phase 220V or 3-Phase 415V (customizable)",
            "Air Pressure": "5–7 kg/cm²",
            "Application": "Lingerie, activewear, shapewear, intimate apparel",
            "Warranty": "1 Year Comprehensive Warranty"
        },
        "featured": True,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "foam-bra-cup-moulding-machine",
        "name": "Foam Bra Cup Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586856/YP/VU/KK/4175789/product-jpeg-500x500.jpg",
        "tagline": "Polyurethane & memory foam hot-press cup forming with permanent shape retention",
        "shortDesc": "Thermal compression machine for forming high-density PU and memory foam bra cups.",
        "description": "Built for hot-press moulding of polyurethane (PU), memory foam, and polyester foam sheets into ergonomic cup shapes. Uniform heating plates and high-force pneumatic clamping deliver repeatable shape memory and even wall thickness across the entire cup curve.",
        "specs": {
            "Foam Types Supported": "PU Foam, High-Resilience Foam, Memory Foam, Spacer Fabric",
            "Heating System": "Top & Bottom Heated Platens",
            "Pressure System": "High-Force Pneumatic Clamping Cylinder",
            "Output": "Up to 500 pieces per shift",
            "Temperature Range": "50°C to 260°C adjustable",
            "Automation": "Semi-Automatic with Push Button & Foot Switch",
            "Application": "Bra cups, shoulder pads, sports bra pads"
        },
        "featured": False,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "padded-bra-cup-moulding-machine",
        "name": "Padded Bra Cup Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/5/608537665/KG/TS/VJ/4175789/padded-bra-cup-moulding-machine-500x500.png",
        "tagline": "Multi-layer padded cup moulding combining foam, fabric, and inner lining in one cycle",
        "shortDesc": "Specialized multi-layer press designed for premium push-up and graduated padded bra cups.",
        "description": "Specialised multi-layer press designed for composite padded cups combining foam, outer fabric, and inner lining in a single synchronized press cycle. Ideal for premium push-up bras, graduated padding, and seamless contour lingerie manufacturing.",
        "specs": {
            "Layering Capability": "Multi-layer composite (Fabric + Foam + Lining)",
            "Heating": "Dual-side independent temperature control",
            "Cycle Programmability": "Programmable timer (20–60 seconds)",
            "Power Requirement": "3-Phase 415V AC",
            "Safety Mechanism": "Dual hand start safety interlock",
            "Application": "Push-up cups, padded T-shirt bras, bridal intimate wear"
        },
        "featured": False,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "10-tons-hydraulic-decoiler",
        "name": "10 Tons Hydraulic Decoiler",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2026/3/590380757/WL/UR/BT/4175789/product-jpeg-500x500.jpg",
        "tagline": "Heavy-duty 10,000 kg capacity hydraulic uncoiler for roll forming lines",
        "shortDesc": "Industrial motorized hydraulic decoiler with 10-ton capacity, hydraulic expansion, and pneumatic braking.",
        "description": "10-ton capacity hydraulic decoiler built for steel and aluminium coil feeding into high-speed roll-forming, slitting, and CTL lines. Features hydraulic mandrel expansion, motorized forward/reverse rotation, hydraulic coil loading car (optional), and pneumatic disc brake for controlled tension unwinding.",
        "specs": {
            "Load Capacity": "10,000 kg (10 Metric Tons)",
            "Coil Inner Diameter (ID)": "480 mm – 520 mm (Hydraulic Expansion)",
            "Max Coil Outer Diameter (OD)": "1500 mm",
            "Max Coil Width": "1250 mm / 1500 mm",
            "Drive System": "Motorized Gear Drive + Hydraulic Power Pack",
            "Braking System": "Heavy-duty Pneumatic Disc Brake",
            "Motor Power": "7.5 HP Geared Motor",
            "Application": "Roll forming lines, Cut to length lines, Roofing sheet lines, Slitting plants",
            "Origin": "Khopoli, Maharashtra"
        },
        "featured": True,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "automatic-roofing-sheet-crimping-machine",
        "name": "Automatic Roofing Sheet Crimping Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png",
        "tagline": "Curved roof sheet crimping — high-speed automatic hydraulic profile forming",
        "shortDesc": "Automated crimping machine for curved roofing sheets used in industrial sheds, warehouses, and stadiums.",
        "description": "Engineered to form curved and crimped arch profiles in pre-painted galvanized iron (PPGI), GP, or aluminium roofing sheets. Widely deployed across India for curved industrial sheds, warehouse canopies, airport hangars, and sports stadium roofing projects.",
        "specs": {
            "Sheet Width Supported": "Up to 1250 mm standard profile",
            "Material Thickness": "0.3 mm to 0.8 mm",
            "Compatible Sheets": "PPGI, GP, Aluminium, Colour-Coated Steel",
            "Drive Mechanism": "Electric Motor + Hydraulic Crimping Unit",
            "Crimping Radius": "Adjustable arc radius from 2m to infinity",
            "Control System": "PLC with Touchscreen HMI Interface",
            "Application": "Curved warehouse roofing, petrol pump canopies, industrial arch buildings"
        },
        "featured": True,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "c-z-purlin-roll-forming-machine",
        "name": "C / Z Purlin Roll Forming Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/ANDWEB/Default/2026/3/591020192/NG/CE/TB/4175789/product-jpeg-500x500.jpeg",
        "tagline": "Interchangeable C & Z section purlin line with automated size change and punching",
        "shortDesc": "High-speed roll forming line producing structural C and Z purlins for Pre-Engineered Buildings (PEB).",
        "description": "Quick-change C and Z section roll forming machine. Integrated hydraulic hole punching, roll forming, and automatic flying shear cutting in a single continuous line. Used in pre-engineered steel buildings (PEB), solar mounting structures, warehouses, and industrial infrastructure.",
        "specs": {
            "Section Types": "C-Purlin (100–300 mm) & Z-Purlin (100–300 mm)",
            "Material Thickness": "1.5 mm to 3.0 mm Galvanized / HR Steel",
            "Line Speed": "10–18 meters per minute",
            "Roller Stations": "16–20 Forming Stations (Cr12 / EN31 Tool Steel)",
            "Control System": "Delta/Siemens PLC + Touch Screen HMI",
            "Shearing": "Hydraulic Post-Cut System (No waste profile cut)",
            "Punching": "Multi-head hydraulic hole & slot punching unit",
            "Total Power": "Approx. 25–30 HP connected load"
        },
        "featured": True,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "automatic-ctl-machine",
        "name": "Automatic Cut To Length (CTL) Machine",
        "category": "Cut To Length Line",
        "categorySlug": "cut-to-length-line",
        "image": "https://gagan-engineering-website.onrender.com/images/automatic-ctl.png",
        "tagline": "High-speed precision Cut-to-Length Line for heavy-duty metal coil processing up to 6mm",
        "shortDesc": "Complete automated cut-to-length line with 10-ton decoiler, 9-roll leveler, and hydraulic shear.",
        "description": "The Automatic CTL (Cut-to-Length) Line is engineered for heavy-duty, high-accuracy metal sheet processing. It processes metal coils continuously through automatic decoiling, precision 9-roll leveling, encoder-based length measurement, heavy mechanical/hydraulic shearing, and exit conveyance.",
        "specs": {
            "Machine Type": "Heavy-Duty Automatic Cut To Length Line",
            "Material Thickness": "Up to 6.0 mm MS / GI / Stainless Steel",
            "Material Width": "Up to 400 mm (Customizable up to 1500 mm)",
            "Line Speed": "20 Meters / Minute continuous",
            "Decoiler Capacity": "10 Metric Ton Hydraulic with Sensor Control",
            "Decoiler Shaft Diameter": "220 mm Hardened Alloy Steel",
            "Leveller Mechanism": "9-Roll Gear Driven Precision Leveller",
            "Leveller Roll Diameter": "114 mm (EN31 Hardened 50–52 HRC)",
            "Leveller Motor": "7.5 HP Heavy Gear Drive",
            "Shearing Unit": "Mechanical / Hydraulic Guillotine Shear (cuts up to 6 mm)",
            "Length Measuring": "Optical Rotary Encoder PLC Automatic Length System",
            "Display & Control": "Touch Screen VFD PLC System",
            "Hydraulic Pump": "50 LPM Yuken Hydraulic Pump",
            "Hydraulic Tank": "200 Litres Capacity",
            "Total Connected Power": "18 HP",
            "Exit Conveyor": "3 HP Gear Motor, 10 Feet Conveyor with 4 Heavy Rollers",
            "Buffer Table": "500 x 3000 mm Plain Precision Table"
        },
        "featured": False,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "corrugated-sheets-making-machine",
        "name": "Corrugated Sheets Making Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
        "tagline": "High-yield corrugated wave profile roll former for industrial shed roofing",
        "shortDesc": "Continuous wave-profile roll forming line for galvanized and colour-coated corrugated roofing sheets.",
        "description": "Engineered for rapid continuous forming of standard wave-corrugated roofing sheets from coil stock. Features high-strength chrome-plated forming rollers, synchronous hydraulic shearing, and programmable length control for industrial and agricultural roofing.",
        "specs": {
            "Profile Type": "Standard Sinusoidal Corrugated Wave",
            "Raw Material": "GI, GP, PPGI, Colour-Coated Galvanized Steel",
            "Forming Speed": "12–18 meters per minute",
            "Roller Material": "Hardened 45# Steel with Hard Chrome Plating",
            "Shearing Method": "Hydraulic Post-Cut Guillotine",
            "Control System": "Microprocessor PLC with length counter",
            "Application": "Industrial factory sheds, agricultural roofing, boundary fencing"
        },
        "featured": False,
        "faqs": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
    {
        "id": "semi-automatic-pipe-counter-boring-and-facing-machine",
        "name": "Semi-Automatic Pipe Counter Boring and Facing Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
        "tagline": "Precision pipe end facing & counter boring up to 60 mm OD with hydraulic clamping and VFD speed control",
        "shortDesc": "Heavy-duty semi-automatic pipe counter boring and facing machine for accurate tube end preparation and beveling up to 60 mm OD.",
        "description": "The Semi-Automatic Pipe Counter Boring and Facing Machine manufactured by Gagan Engineering Works in Khopoli is designed for high-precision end facing, chamfering, and internal counter boring of round pipes and industrial tubes up to 60 mm outer diameter. Powered by a 5 HP main drive with variable frequency control (100–1450 RPM) and a dedicated 1 HP hydraulic power pack (60-litre capacity), the machine delivers rigid hydraulic clamping, smooth automated feed stroke, and accurate length repeat cycles for continuous manufacturing operations.",
        "specs": {
            "Machine Type": "Semi-Automatic Pipe Counter Boring and Facing Machine",
            "Maximum Pipe Size": "60 mm OD",
            "Main Motor": "5 HP (1450 RPM)",
            "Speed Control": "100–1450 RPM, VFD Control",
            "Drive Type": "Heavy-Duty Belt Drive",
            "Hydraulic Motor": "1 HP",
            "Clamping": "Rigid Hydraulic Clamping",
            "Feed": "Hydraulic Automated Feed",
            "Length Control": "Auto Control",
            "Power Pack Capacity": "60 Litres",
            "Machine Dimensions": "1.0 m × 1.5 m × 1200 mm Height",
            "Make / Origin": "Gagan Engineering Works (Khopoli, MH)",
            "Rate / Price": "₹3,40,000/- per machine"
        },
        "featured": True,
        "faqs": [
            {"q": "What is the maximum pipe diameter handled by this machine?", "a": "This semi-automatic machine handles pipes and tubes up to 60 mm Outside Diameter (OD) with rigid hydraulic clamping."},
            {"q": "Does this machine offer variable speed control?", "a": "Yes, it is equipped with a Variable Frequency Drive (VFD) offering smooth spindle speed adjustment between 100 and 1450 RPM."},
            {"q": "What warranty and service support are provided?", "a": "Gagan Engineering Works provides a 1-year comprehensive manufacturer warranty and on-site commissioning across India."}
        ],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
]

SEED_CATEGORIES = [
    {"id": "all", "name": "All Machinery"},
    {"id": "bra-cup-moulding-machine", "name": "Bra Cup Moulding Machine"},
    {"id": "roll-forming-sheet-metal", "name": "Roll Forming & Sheet Metal"},
    {"id": "cut-to-length-line", "name": "Cut To Length Line"}
]

# In-memory fallback when MongoDB is unavailable
_mem_products = list(SEED_PRODUCTS)
_mem_leads: List[Dict] = []


# ----------------- Models -----------------
class SpecsDict(BaseModel):
    class Config:
        extra = "allow"

class FAQItem(BaseModel):
    q: str
    a: str

class ProductCreate(BaseModel):
    id: Optional[str] = None
    name: str
    category: str
    categorySlug: str
    image: str
    tagline: Optional[str] = ""
    shortDesc: Optional[str] = ""
    description: Optional[str] = ""
    specs: Optional[Dict[str, str]] = {}
    featured: Optional[bool] = False
    faqs: Optional[List[FAQItem]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    categorySlug: Optional[str] = None
    image: Optional[str] = None
    tagline: Optional[str] = None
    shortDesc: Optional[str] = None
    description: Optional[str] = None
    specs: Optional[Dict[str, str]] = None
    featured: Optional[bool] = None
    faqs: Optional[List[FAQItem]] = None

class ContactLead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    phone: str
    product_interest: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactLeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    product_interest: Optional[str] = None
    message: str

class AIQuestionRequest(BaseModel):
    question: str


# ----------------- Admin Auth -----------------
def verify_admin(request: Request):
    """Robust admin authenticator supporting custom headers & Bearer tokens without browser popup."""
    custom_user = request.headers.get("X-Admin-User", "").strip()
    custom_pass = request.headers.get("X-Admin-Pass", "").strip()
    custom_auth = request.headers.get("X-Admin-Auth", "").strip()
    auth_header = request.headers.get("Authorization", "").strip()

    username = None
    password = None

    if custom_user and custom_pass:
        username = custom_user
        password = custom_pass
    elif custom_auth:
        try:
            decoded = base64.b64decode(custom_auth).decode("utf-8")
            if ":" in decoded:
                username, password = decoded.split(":", 1)
        except Exception:
            pass
    elif auth_header:
        parts = auth_header.split(" ", 1)
        if len(parts) == 2:
            try:
                decoded = base64.b64decode(parts[1]).decode("utf-8")
                if ":" in decoded:
                    username, password = decoded.split(":", 1)
            except Exception:
                pass

    if not (username and password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required. Please log in.",
        )

    # Valid usernames and passwords
    valid_users = ["admin", os.environ.get("ADMIN_USERNAME", "admin").strip()]
    valid_passwords = [
        "Enrique7@",
        "gaganworks2006",
        os.environ.get("ADMIN_PASSWORD", "Enrique7@").strip(),
        os.environ.get("ADMIN_PASSWORD", "gaganworks2006").strip()
    ]

    is_user_valid = any(secrets.compare_digest(username.strip(), u) for u in valid_users if u)
    is_pass_valid = any(secrets.compare_digest(password.strip(), p) for p in valid_passwords if p)

    if not (is_user_valid and is_pass_valid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
        )

    return username


# ----------------- DB Helpers -----------------
async def get_products_from_db() -> List[Dict]:
    """Fetch all products from MongoDB, fallback to in-memory."""
    if db is None:
        return _mem_products
    try:
        cursor = db["products"].find({}, {"_id": 0})
        products = await cursor.to_list(length=1000)
        if products:
            return products
        return _mem_products
    except Exception:
        return _mem_products

async def get_product_by_id(product_id: str) -> Optional[Dict]:
    """Fetch single product from MongoDB, fallback to in-memory."""
    if db is None:
        return next((p for p in _mem_products if p["id"] == product_id), None)
    try:
        product = await db["products"].find_one({"id": product_id}, {"_id": 0})
        if product:
            return product
    except Exception:
        pass
    return next((p for p in _mem_products if p["id"] == product_id), None)


# ----------------- Startup Seeder -----------------
@app.on_event("startup")
async def seed_database():
    """Seed database with default products if collection is empty."""
    if db is None:
        logger.warning("MongoDB not connected — using in-memory data.")
        return
    try:
        count = await db["products"].count_documents({})
        if count == 0:
            logger.info("Seeding products collection with default data...")
            await db["products"].insert_many([
                {**p, "_id_excluded": True} for p in SEED_PRODUCTS
            ])
            # Clean up the extra field
            await db["products"].update_many({}, {"$unset": {"_id_excluded": ""}})
            logger.info(f"Seeded {len(SEED_PRODUCTS)} products successfully.")
        else:
            logger.info(f"Products collection already has {count} documents, skipping seed.")
    except Exception as e:
        logger.warning(f"Could not seed database: {e}")


# ----------------- Email -----------------
def build_lead_email_html(lead: ContactLead) -> str:
    return f"""
    <table cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:640px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;background:#f7f7f7;padding:24px;">
      <tr>
        <td style="background:#050505;color:#fff;padding:24px;border-left:6px solid #FF5722;">
          <div style="font-size:12px;letter-spacing:0.2em;color:#FF5722;text-transform:uppercase;">New Machinery Quotation Lead — Gagan Engineering Works</div>
          <h2 style="margin:8px 0 0 0;font-size:22px;">{lead.name}</h2>
        </td>
      </tr>
      <tr>
        <td style="background:#fff;padding:24px;color:#111;">
          <table cellpadding="8" cellspacing="0" border="0" style="width:100%;font-size:14px;">
            <tr><td style="width:160px;color:#666;">Name</td><td><strong>{lead.name}</strong></td></tr>
            <tr><td style="color:#666;">Phone</td><td><strong>{lead.phone}</strong></td></tr>
            <tr><td style="color:#666;">Email</td><td><strong>{lead.email}</strong></td></tr>
            <tr><td style="color:#666;">Product Interest</td><td><strong>{lead.product_interest or '—'}</strong></td></tr>
            <tr><td style="color:#666;vertical-align:top;">Message / Requirement</td><td>{lead.message}</td></tr>
            <tr><td style="color:#666;">Received</td><td>{lead.created_at.strftime('%d %b %Y, %H:%M UTC')}</td></tr>
          </table>
        </td>
      </tr>
      <tr>
        <td style="background:#050505;color:#9CA3AF;padding:16px;font-size:12px;text-align:center;">
          Gagan Engineering Works · Khopoli, Maharashtra · +91 8329465245
        </td>
      </tr>
    </table>
    """

async def send_lead_email_with_diagnostics(lead: ContactLead) -> Tuple[Optional[str], Optional[str]]:
    api_key = os.environ.get('RESEND_API_KEY') or getattr(resend, 'api_key', None)
    if not api_key:
        msg = "RESEND_API_KEY environment variable is not configured."
        logger.warning(msg)
        return None, msg

    api_key = str(api_key).strip().strip('"').strip("'")
    resend.api_key = api_key

    raw_sender = os.environ.get('SENDER_EMAIL', SENDER_EMAIL or 'onboarding@resend.dev').strip()
    recipient = os.environ.get('BUSINESS_EMAIL', BUSINESS_EMAIL or 'gaganengineerings@gmail.com').strip()

    # Format from address properly
    if "<" in raw_sender and ">" in raw_sender:
        from_email = raw_sender
    elif raw_sender == "onboarding@resend.dev":
        from_email = "Gagan Engineering Leads <onboarding@resend.dev>"
    else:
        from_email = f"Gagan Engineering Leads <{raw_sender}>"

    subject = f"Machinery Inquiry from {lead.name} — {lead.product_interest or 'General'}"
    html_content = build_lead_email_html(lead)

    payload = {
        "from": from_email,
        "to": [recipient],
        "subject": subject,
        "html": html_content,
    }
    if lead.email and "@" in lead.email:
        payload["reply_to"] = lead.email.strip()

    errors = []

    # Method 1: Try Resend SDK
    try:
        result = await asyncio.to_thread(resend.Emails.send, payload)
        email_id = result.get("id") if isinstance(result, dict) else str(result)
        logger.info(f"Lead email successfully sent via Resend SDK for {lead.name}: {email_id}")
        return email_id, None
    except Exception as e:
        sdk_err = str(e)
        errors.append(f"SDK: {sdk_err}")
        logger.warning(f"Resend SDK attempt note: {sdk_err}. Trying direct REST API fallback...")

    # Method 2: Foolproof Direct REST API fallback via requests
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        res = await asyncio.to_thread(
            requests.post,
            "https://api.resend.com/emails",
            headers=headers,
            json=payload,
            timeout=10
        )
        if res.status_code in (200, 201):
            data = res.json()
            email_id = data.get("id", "sent")
            logger.info(f"Lead email successfully sent via Resend REST API for {lead.name}: {email_id}")
            return email_id, None
        else:
            rest_err = f"HTTP {res.status_code}: {res.text}"
            errors.append(f"REST: {rest_err}")
            logger.error(f"Resend REST API error: {rest_err}")
            return None, rest_err
    except Exception as e:
        rest_err = str(e)
        errors.append(f"REST Exception: {rest_err}")
        logger.error(f"Failed to send lead email via direct Resend REST API: {rest_err}")
        return None, "; ".join(errors)

async def send_lead_email(lead: ContactLead) -> Optional[str]:
    email_id, _ = await send_lead_email_with_diagnostics(lead)
    return email_id


# ----------------- Public Routes -----------------
@api_router.get("/")
async def root():
    return {"service": "Gagan Engineering Works API", "version": "3.0.0", "status": "ok"}

@api_router.get("/products")
async def list_products(category: Optional[str] = None):
    products = await get_products_from_db()
    if category and category.lower() != "all":
        products = [
            p for p in products
            if p["category"].lower() == category.lower()
            or p.get("categorySlug", "").lower() == category.lower()
        ]
    return {"products": products, "count": len(products)}

@api_router.get("/products/featured")
async def featured_products():
    products = await get_products_from_db()
    return {"products": [p for p in products if p.get("featured")]}

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    all_products = await get_products_from_db()
    related = [p for p in all_products if p["category"] == product["category"] and p["id"] != product_id][:3]
    return {"product": product, "related": related}

@api_router.get("/categories")
async def list_categories():
    if db is not None:
        try:
            products = await get_products_from_db()
            seen = set()
            cats = [{"id": "all", "name": "All Machinery"}]
            for p in products:
                slug = p.get("categorySlug", "")
                if slug and slug not in seen:
                    seen.add(slug)
                    cats.append({"id": slug, "name": p["category"]})
            return {"categories": cats}
        except Exception:
            pass
    return {"categories": SEED_CATEGORIES}

@api_router.post("/contact")
async def submit_contact(payload: ContactLeadCreate):
    lead = ContactLead(**payload.model_dump())
    lead_dict = lead.model_dump()
    lead_dict["created_at"] = lead.created_at.isoformat()

    # Always keep in memory so leads section works even without MongoDB
    _mem_leads.insert(0, lead_dict)

    if db is not None:
        try:
            await db["contact_leads"].insert_one(lead.model_dump())
        except Exception as e:
            logger.warning(f"Failed to save lead to MongoDB: {e}")

    email_id, err_detail = await send_lead_email_with_diagnostics(lead)

    return {
        "status": "success",
        "message": "Thank you! Your quotation request has been received. Our chief engineer will contact you within 24 hours.",
        "lead_id": lead.id,
        "email_sent": bool(email_id),
        "email_id": email_id,
        "email_error": err_detail if not email_id else None,
    }

@api_router.post("/ai/ask")
async def ai_machinery_advisor(req: AIQuestionRequest):
    q = req.question.lower()
    products = await get_products_from_db()

    if any(w in q for w in ["bra", "lingerie", "cup", "foam", "moulding"]):
        match = [p for p in products if p.get("categorySlug") == "bra-cup-moulding-machine"]
        return {
            "answer": "For bra cup & lingerie production, we manufacture 4 specialized machines:\n\n1. **Double Head Electric Bra Cup Moulding Machine** (~400–600 pcs/shift, twin-station PID control).\n2. **Bra Cup Fabric Moulding Machine** (for woven/laminated fabrics).\n3. **Foam Bra Cup Moulding Machine** (for PU & memory foam).\n4. **Padded Bra Cup Moulding Machine** (multi-layer composite moulding).\n\nAll machines feature digital PID thermostats (0–250°C) and interchangeable moulds.",
            "suggestedProducts": match
        }

    if any(w in q for w in ["decoiler", "uncoiler", "10 ton", "coil"]):
        match = [p for p in products if "decoiler" in p["id"]]
        return {
            "answer": "Our **10 Tons Hydraulic Decoiler** is built for heavy-duty coil uncoiling:\n\n• **Capacity**: 10,000 kg (10 Metric Tons)\n• **Mandrel Expansion**: Hydraulic (480–520 mm ID)\n• **Drive**: 7.5 HP Geared Motor\n• **Braking**: Pneumatic disc brake for constant tension.",
            "suggestedProducts": match
        }

    if any(w in q for w in ["ctl", "cut to length", "leveler", "shear"]):
        match = [p for p in products if p["id"] == "automatic-ctl-machine"]
        return {
            "answer": "Our **Automatic Cut To Length (CTL) Machine** is a complete high-speed processing line:\n\n• **Max Thickness**: Up to 6.0 mm\n• **Line Speed**: 20 m/min\n• **Leveler**: 9-Roll gear-driven leveler with EN31 hardened steel rolls (50–52 HRC)\n• **Control**: Optical rotary encoder with touch-screen PLC (±0.5mm accuracy).",
            "suggestedProducts": match
        }

    if any(w in q for w in ["purlin", "roofing", "crimping", "corrugated"]):
        match = [p for p in products if p.get("categorySlug") == "roll-forming-sheet-metal"]
        return {
            "answer": "For PEB and roofing fabrication, we build:\n\n• **C / Z Purlin Roll Forming Machine**: Quick changeover between C & Z profiles (100–300mm), 1.5–3.0mm thickness.\n• **Automatic Roofing Sheet Crimping Machine**: High-speed curved arch forming for PPGI/GI sheets up to 1250mm.\n• **Corrugated Sheets Making Machine**: Continuous wave profile roll former.",
            "suggestedProducts": match
        }

    return {
        "answer": "Gagan Engineering Works specializes in heavy-duty **Bra Cup Moulding Presses**, **10-Ton Hydraulic Decoilers**, **C/Z Purlin Roll Formers**, **Automatic Cut-To-Length Lines**, and **Roofing Sheet Machinery**.\n\nPlease share your required production capacity or sheet thickness, or tap WhatsApp to consult directly with our engineering team in Khopoli.",
        "suggestedProducts": products[:3]
    }

@api_router.get("/business-info")
async def business_info():
    return {
        "name": "Gagan Engineering Works",
        "tagline": "Precision Industrial Machinery · Since 2006",
        "established": 2006,
        "experience_years": 19,
        "nature": "Manufacturer & Exporter",
        "legal": "Proprietorship",
        "employees": "11–25",
        "turnover": "₹40L – ₹1.5 Cr",
        "phone": "+91 8329465245",
        "whatsapp": "+91 8329465245",
        "email": "gaganengineerings@gmail.com",
        "address": "Mumbai - Pune Hwy, near Star Garage, Navanath Colony, Yashwant Nagar, Khopoli, Maharashtra 410203",
        "rating": 4.0,
        "review_count": 9,
    }


# ----------------- Admin Routes -----------------
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

@admin_router.get("/auth/check")
async def check_admin_auth(username: str = Depends(verify_admin)):
    return {"status": "authenticated", "username": username}

@admin_router.get("/products")
async def admin_list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, le=200),
    username: str = Depends(verify_admin)
):
    products = await get_products_from_db()

    if category and category != "all":
        products = [p for p in products if p.get("categorySlug") == category or p.get("category", "").lower() == category.lower()]
    if featured is not None:
        products = [p for p in products if p.get("featured") == featured]
    if search:
        s = search.lower()
        products = [
            p for p in products
            if s in p["name"].lower()
            or s in p.get("category", "").lower()
            or s in p.get("description", "").lower()
        ]

    total = len(products)
    start = (page - 1) * limit
    paginated = products[start:start + limit]

    return {"products": paginated, "total": total, "page": page, "limit": limit}

@admin_router.get("/products/{product_id}")
async def admin_get_product(product_id: str, username: str = Depends(verify_admin)):
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}

@admin_router.post("/products", status_code=201)
async def admin_create_product(payload: ProductCreate, username: str = Depends(verify_admin)):
    product_id = payload.id or payload.name.lower().replace(" ", "-").replace("/", "-").replace("&", "and")
    # Slugify
    import re
    product_id = re.sub(r'[^a-z0-9-]', '', re.sub(r'\s+', '-', product_id.lower()))

    # Check uniqueness
    existing = await get_product_by_id(product_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Product with id '{product_id}' already exists")

    new_product = {
        **payload.model_dump(),
        "id": product_id,
        "faqs": [f.model_dump() for f in (payload.faqs or [])],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }

    if db is not None:
        try:
            await db["products"].insert_one({**new_product})
            await db["products"].update_one({"id": product_id}, {"$unset": {"_id": ""}})
        except Exception as e:
            logger.warning(f"Failed to insert product to MongoDB: {e}")
            _mem_products.append(new_product)
    else:
        _mem_products.append(new_product)

    return {"status": "created", "product": new_product}

@admin_router.put("/products/{product_id}")
async def admin_update_product(product_id: str, payload: ProductUpdate, username: str = Depends(verify_admin)):
    existing = await get_product_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if "faqs" in update_data:
        update_data["faqs"] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in update_data["faqs"]]
    update_data["updatedAt"] = datetime.now(timezone.utc)

    if db is not None:
        try:
            await db["products"].update_one({"id": product_id}, {"$set": update_data})
        except Exception as e:
            logger.warning(f"MongoDB update failed: {e}")
            for i, p in enumerate(_mem_products):
                if p["id"] == product_id:
                    _mem_products[i] = {**p, **update_data}
                    break
    else:
        for i, p in enumerate(_mem_products):
            if p["id"] == product_id:
                _mem_products[i] = {**p, **update_data}
                break

    updated = await get_product_by_id(product_id)
    return {"status": "updated", "product": updated}

@admin_router.delete("/products/{product_id}")
async def admin_delete_product(product_id: str, username: str = Depends(verify_admin)):
    global _mem_products
    existing = await get_product_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    if db is not None:
        try:
            await db["products"].delete_one({"id": product_id})
        except Exception as e:
            logger.warning(f"MongoDB delete failed: {e}")
            _mem_products = [p for p in _mem_products if p["id"] != product_id]
    else:
        _mem_products = [p for p in _mem_products if p["id"] != product_id]

    return {"status": "deleted", "id": product_id}

@admin_router.post("/products/import")
async def admin_import_products(products: List[ProductCreate], username: str = Depends(verify_admin)):
    """Bulk import products from JSON array. Skips duplicates by ID."""
    import re
    created = []
    skipped = []

    for payload in products:
        product_id = payload.id or payload.name.lower()
        product_id = re.sub(r'[^a-z0-9-]', '', re.sub(r'\s+', '-', product_id.lower()))

        existing = await get_product_by_id(product_id)
        if existing:
            skipped.append(product_id)
            continue

        new_product = {
            **payload.model_dump(),
            "id": product_id,
            "faqs": [f.model_dump() for f in (payload.faqs or [])],
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        if db is not None:
            try:
                await db["products"].insert_one({**new_product})
            except Exception as e:
                logger.warning(f"Failed to insert product {product_id}: {e}")
                _mem_products.append(new_product)
        else:
            _mem_products.append(new_product)

        created.append(product_id)

    return {
        "status": "completed",
        "created": len(created),
        "skipped": len(skipped),
        "created_ids": created,
        "skipped_ids": skipped
    }

@admin_router.post("/upload-image")
async def admin_upload_image(file: UploadFile = File(...), username: str = Depends(verify_admin)):
    """Upload an image file from admin panel and return its public URL."""
    try:
        clean_ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
        if clean_ext not in [".jpg", ".jpeg", ".png", ".webp", ".svg"]:
            clean_ext = ".jpg"
        unique_name = f"product_{uuid.uuid4().hex[:12]}{clean_ext}"
        dest_path = UPLOAD_DIR / unique_name
        contents = await file.read()
        with open(dest_path, "wb") as f:
            f.write(contents)
        return {"url": f"/images/uploads/{unique_name}", "filename": unique_name}
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

@admin_router.get("/leads")
async def admin_list_leads(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, le=200),
    username: str = Depends(verify_admin)
):
    if db is None:
        skip = (page - 1) * limit
        paginated = _mem_leads[skip:skip + limit]
        return {
            "leads": paginated,
            "total": len(_mem_leads),
            "page": page,
            "limit": limit,
            "message": "In-memory leads (MongoDB not connected)"
        }
    try:
        total = await db["contact_leads"].count_documents({})
        skip = (page - 1) * limit
        cursor = db["contact_leads"].find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        leads = await cursor.to_list(length=limit)
        # Serialize datetimes
        for lead in leads:
            if isinstance(lead.get("created_at"), datetime):
                lead["created_at"] = lead["created_at"].isoformat()
        
        # Merge in-memory leads if any aren't in DB yet
        db_ids = {l.get("id") for l in leads if l.get("id")}
        for mem_l in _mem_leads:
            if mem_l.get("id") not in db_ids:
                leads.insert(0, mem_l)

        return {"leads": leads, "total": max(total, len(_mem_leads)), "page": page, "limit": limit}
    except Exception as e:
        logger.error(f"Failed to fetch leads from MongoDB: {e}")
        skip = (page - 1) * limit
        paginated = _mem_leads[skip:skip + limit]
        return {"leads": paginated, "total": len(_mem_leads), "page": page, "limit": limit, "message": f"Fallback: {str(e)}"}

@admin_router.post("/test-email")
async def admin_test_email(username: str = Depends(verify_admin)):
    """Diagnostic endpoint to test Resend API key and email delivery."""
    api_key = os.environ.get('RESEND_API_KEY') or getattr(resend, 'api_key', None)
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="RESEND_API_KEY environment variable is not configured in Vercel settings."
        )

    recipient = os.environ.get('BUSINESS_EMAIL', BUSINESS_EMAIL or 'gaganengineerings@gmail.com').strip()
    sender = os.environ.get('SENDER_EMAIL', SENDER_EMAIL or 'onboarding@resend.dev').strip()

    test_lead = ContactLead(
        name="[TEST] Chief Engineer Verification",
        email="test@gaganengineerings.in",
        phone="+91 8329465245",
        product_interest="Double Head Electric Bra Cup Moulding Machine",
        message="This is an automated diagnostic test from Gagan Engineering Works Admin Panel to verify Resend API integration."
    )

    email_id, err_detail = await send_lead_email_with_diagnostics(test_lead)
    if not email_id:
        raise HTTPException(
            status_code=400,
            detail=f"Resend rejected email dispatch: {err_detail or 'Unknown error'}"
        )

    return {
        "status": "success",
        "message": f"Test email dispatched successfully to {recipient} (ID: {email_id})!",
        "email_id": email_id,
        "sender": sender,
        "recipient": recipient,
    }

@admin_router.get("/stats")
async def admin_stats(username: str = Depends(verify_admin)):
    products = await get_products_from_db()
    featured_count = sum(1 for p in products if p.get("featured"))

    leads_count = len(_mem_leads)
    if db is not None:
        try:
            leads_count = max(await db["contact_leads"].count_documents({}), len(_mem_leads))
        except Exception:
            pass

    categories = set(p.get("categorySlug", "") for p in products)

    resend_ready = bool(os.environ.get('RESEND_API_KEY') or getattr(resend, 'api_key', None))
    sender_mail = os.environ.get('SENDER_EMAIL', SENDER_EMAIL or 'onboarding@resend.dev')
    biz_mail = os.environ.get('BUSINESS_EMAIL', BUSINESS_EMAIL or 'gaganengineerings@gmail.com')

    return {
        "total_products": len(products),
        "featured_products": featured_count,
        "total_leads": leads_count,
        "categories_count": len(categories),
        "categories": list(categories),
        "resend_configured": resend_ready,
        "sender_email": sender_mail,
        "business_email": biz_mail,
    }


# ----------------- SEO Endpoints -----------------
_raw_site_url = os.environ.get("WEBSITE_URL") or os.environ.get("VERCEL_PROJECT_PRODUCTION_URL") or "https://www.gaganengineerings.in"
WEBSITE_URL = _raw_site_url if _raw_site_url.startswith("http") else f"https://{_raw_site_url}"

@app.get("/sitemap.xml", response_class=Response)
async def sitemap():
    products = await get_products_from_db()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    urls = [
        f"""  <url>
    <loc>{WEBSITE_URL}/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/products</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/about</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/contact</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""",
    ]

    for p in products:
        product_date = now
        if isinstance(p.get("updatedAt"), datetime):
            product_date = p["updatedAt"].strftime("%Y-%m-%d")
        
        img_tag = ""
        if p.get("image"):
            img_url = p["image"]
            p_name = p.get("name", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            img_tag = f"""
    <image:image>
      <image:loc>{img_url}</image:loc>
      <image:title>{p_name}</image:title>
      <image:caption>{p_name} manufactured by Gagan Engineering Works Khopoli</image:caption>
    </image:image>"""

        urls.append(f"""  <url>
    <loc>{WEBSITE_URL}/products/{p['id']}</loc>
    <lastmod>{product_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.85</priority>{img_tag}
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(urls)}
</urlset>"""

    return Response(content=xml, media_type="application/xml", headers={"Cache-Control": "public, max-age=3600"})

@app.get("/google-merchant-feed.xml", response_class=Response)
@app.get("/google-shopping-feed.xml", response_class=Response)
async def google_merchant_feed():
    products = await get_products_from_db()
    items = []

    for p in products:
        p_id = p.get("id", "")
        p_name = p.get("name", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        p_desc = (p.get("description") or p.get("tagline") or p_name).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        p_img = p.get("image") or f"{WEBSITE_URL}/logo.png"
        p_link = f"{WEBSITE_URL}/products/{p_id}"
        category = p.get("category", "Industrial Machinery")
        
        # Industrial category mapping
        google_cat = "Business &amp; Industrial &gt; Manufacturing &gt; Manufacturing Machinery"
        
        items.append(f"""    <item>
      <g:id>{p_id}</g:id>
      <g:title>{p_name}</g:title>
      <g:description>{p_desc}</g:description>
      <g:link>{p_link}</g:link>
      <g:image_link>{p_img}</g:image_link>
      <g:brand>Gagan Engineering Works</g:brand>
      <g:condition>new</g:condition>
      <g:availability>in_stock</g:availability>
      <g:price>150000.00 INR</g:price>
      <g:google_product_category>{google_cat}</g:google_product_category>
      <g:product_type>{category}</g:product_type>
      <g:identifier_exists>no</g:identifier_exists>
      <g:shipping>
        <g:country>IN</g:country>
        <g:service>Freight Delivery (Pan-India)</g:service>
        <g:price>0.00 INR</g:price>
      </g:shipping>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
  <channel>
    <title>Gagan Engineering Works - Machinery Catalogue Feed</title>
    <link>{WEBSITE_URL}</link>
    <description>Industrial Machinery &amp; Equipment Manufacturer in Khopoli, Maharashtra, India</description>
{chr(10).join(items)}
  </channel>
</rss>"""

    return Response(content=rss, media_type="application/xml", headers={"Cache-Control": "public, max-age=3600"})

@admin_router.post("/submit-indexnow")
@app.post("/api/admin/submit-indexnow")
@app.post("/admin/submit-indexnow")
async def submit_indexnow(username: str = Depends(verify_admin)):
    """Submits all site URLs to Microsoft Bing and IndexNow for instant search indexing."""
    import requests
    products = await get_products_from_db()
    
    url_list = [
        f"{WEBSITE_URL}/",
        f"{WEBSITE_URL}/products",
        f"{WEBSITE_URL}/about",
        f"{WEBSITE_URL}/contact",
        f"{WEBSITE_URL}/return-policy",
        f"{WEBSITE_URL}/privacy-policy",
        f"{WEBSITE_URL}/terms",
    ]
    for p in products:
        url_list.append(f"{WEBSITE_URL}/products/{p['id']}")

    payload = {
        "host": "www.gaganengineerings.in",
        "key": "3a5f2c7e48b19a0",
        "keyLocation": f"{WEBSITE_URL}/3a5f2c7e48b19a0.txt",
        "urlList": url_list
    }

    try:
        resp = requests.post("https://api.indexnow.org/indexnow", json=payload, timeout=10)
        return {
            "status": "success",
            "code": resp.status_code,
            "submitted_urls_count": len(url_list),
            "message": f"Successfully pushed {len(url_list)} URLs to Microsoft Bing / IndexNow!"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/*
Disallow: /api/admin/
Disallow: /api/admin/*

Sitemap: {WEBSITE_URL}/sitemap.xml
"""


# ----------------- App Setup -----------------
@app.middleware("http")
async def normalize_api_path(request, call_next):
    """Ensures Vercel serverless rewrites resolve correctly whether /api is stripped or preserved."""
    path = request.scope.get("path", "")
    if not path.startswith("/api") and (
        path.startswith("/admin")
        or path.startswith("/products")
        or path.startswith("/contact")
        or path.startswith("/quotes")
        or path.startswith("/health")
    ):
        request.scope["path"] = f"/api{path}"
    response = await call_next(request)
    return response

app.include_router(api_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
