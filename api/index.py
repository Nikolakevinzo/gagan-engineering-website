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
import time
from datetime import datetime, timezone

from fastapi.staticfiles import StaticFiles

import certifi

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with safe fallback (only connects if MONGO_URL is configured)
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'gagan_engineering')
client = None
db = None
if mongo_url:
    try:
        client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where()
        )
        db = client[db_name]
    except Exception as e:
        logger.warning(f"MongoDB connection deferred or offline: {e}")



# Resend configuration
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL', 'gaganengineerings@gmail.com')

# Admin credentials (set in .env)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Enrique7')

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
    "id": "23-nali-liner-sheet-roll-forming-machine---1220-mm",
    "name": "23 Nali Liner Sheet Roll Forming Machine - 1220 mm",
    "category": "Roll Forming & Sheet Metal",
    "categorySlug": "roll-forming-sheet-metal",
    "image": "https://lh3.googleusercontent.com/d/11mvvORHsgk4-1FY0FDBM2VfmoCPBmPPE",
    "tagline": "High-Speed 23 Nali Liner Profile Production with PLC-Controlled Precision",
    "shortDesc": "Automatic 23 Nali liner sheet roll forming machine for 1220 mm PPGL, PPGI and galvanized steel coils, featuring 18 forming stations, precision rollers and PLC-controlled hydraulic cutting.",
    "description": "The Gagan Engineering Works 23 Nali Liner Sheet Roll Forming Machine is designed for continuous production of precision liner and cladding profiles from colour-coated and galvanized steel coils. The machine handles 0.30-0.80 mm material with 1220 mm input width and uses an 18-station roll forming system for smooth, consistent profile formation.\n\nThe high-speed configuration features EN9 hard-chrome rollers, PLC automation, automatic length measurement and hydraulic cutting for repeatable production and clean finished sheets. It is suitable for manufacturing liner sheets used in industrial wall cladding, ceilings, partitions, side walls, facades and PEB applications. Liner-profile industry references similarly describe these products as multi-rib sheets primarily intended for wall and ceiling/cladding applications.",
    "specs": {
        "Machine Type": "Automatic 23 Nali Liner Sheet Roll Forming Machine",
        "Profile Type": "23 Nali / Multi-Rib Liner Profile",
        "Input Coil Width": "1220 mm",
        "Material Thickness": "0.30-0.80 mm",
        "Suitable Material": "PPGL / PPGI / GC / BGL / Galvanized & Colour-Coated Steel",
        "Forming Stations": "18 Stations",
        "Forming Speed": "50-60 m/min (High-Speed Configuration)",
        "Main Motor": "7.5 HP",
        "Shaft Diameter": "80 mm",
        "Length Accuracy": "±1 mm",
        "Cutting System": "PLC-Controlled Hydraulic Shearing",
        "Cutter Blade": "Cr12 Hardened / Quenched Tool Steel",
        "Hydraulic Power Pack": "5.5 kW",
        "Decoiler": "7 Ton Hydraulic Decoiler - Available with Line",
        "Automation": "Automatic Length & Quantity Measurement",
        "Machine Workflow": "Decoiling → Feeding → Roll Forming → Length Measurement → Hydraulic Cutting → Output",
        "Origin": "Manufactured in Khopoli, Maharashtra, India"
    },
    "featured": True,
    "faqs": [
        {
            "q": "What material thickness can the liner machine process?",
            "a": "The machine is designed for 0.30 mm to 0.80 mm sheet thickness."
        },
        {
            "q": "What is the input coil width?",
            "a": "The standard configuration is designed for 1220 mm wide coils."
        },
        {
            "q": "Which materials can be processed?",
            "a": "The machine supports PPGI, PPGL, GC, BGL and other suitable colour-coated or galvanized steel coils."
        },
        {
            "q": "What profile does the machine manufacture?",
            "a": "It is designed for the 23 Nali multi-rib liner profile, with tooling manufactured according to the approved profile/sample sheet."
        },
        {
            "q": "Is a decoiler available with the machine?",
            "a": "Yes. A 7-ton hydraulic decoiler can be supplied as part of the production line."
        }
    ],
    "images": [
        "https://lh3.googleusercontent.com/d/11mvvORHsgk4-1FY0FDBM2VfmoCPBmPPE"
    ],
    "video_url": None,
    "createdAt": "2026-09-20 12:22:04.624000",
    "updatedAt": "2026-09-20 12:22:04.624000"
},

    {
        "id": "10-tons-hydraulic-decoiler",
        "name": "10 Tons Hydraulic Decoiler Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2026/3/590380757/WL/UR/BT/4175789/product-jpeg-500x500.jpg",
        "images": [
                    "https://5.imimg.com/data5/ANDROID/Default/2026/3/590380757/WL/UR/BT/4175789/product-jpeg-500x500.jpg"
        ],
        "tagline": "Heavy-Duty 10,000 kg Capacity Motorized Hydraulic Uncoiler with Pneumatic Tension Braking",
        "shortDesc": "Industrial 10-ton motorized hydraulic uncoiler with wedge mandrel expansion (480–520 mm), loop sensor automation, and pneumatic disc brake for high-speed roll forming lines.",
        "description": "The 10 Tons Hydraulic Decoiler manufactured by Gagan Engineering Works in Khopoli, Maharashtra is engineered for continuous, heavy-duty coil feeding into high-speed roll forming, Cut-to-Length (CTL), slitting, and roofing sheet manufacturing lines. Rated for continuous industrial service with steel, aluminium, galvanized iron (GI), and stainless steel coils up to 10,000 kg (10 Metric Tons), the machine features a rigid 220 mm forged alloy steel main shaft supported by spherical roller bearings in heavy-duty cast steel pillow blocks. The 4-segment wedge-style expanding mandrel provides smooth hydraulic expansion from 480 mm to 520 mm coil inner diameter (ID), backed by hydraulic pilot check valves to guarantee zero pressure drop during high-speed rotation. Powered by a 7.5 HP heavy geared motor with Variable Frequency Drive (VFD) acceleration/deceleration, the uncoiler integrates a dual pneumatic disc brake system that eliminates coil over-run during emergency or flying-shear stop cycles. Equipped with non-contact photoelectric loop sensors for automatic feed synchronization and optional hydraulic coil loading car with motorized traversing, this decoiler drastically minimizes coil changeover downtime in high-throughput metal processing plants across India and global export destinations.",
        "specs": {
                    "Load Capacity": "10,000 kg (10 Metric Tons Continuous Duty)",
                    "Coil Inner Diameter (ID)": "480 mm – 520 mm (Hydraulic Wedge Expansion)",
                    "Max Coil Outer Diameter (OD)": "1500 mm (Optional up to 1800 mm)",
                    "Max Coil Width": "1250 mm / 1500 mm (Customizable up to 1600 mm)",
                    "Main Spindle Shaft": "220 mm Diameter Solid Forged Alloy Steel (40Cr)",
                    "Mandrel Segments": "4-Segment Wedge Expansion with Bronze Wear Plates",
                    "Expansion Mechanism": "Hydraulic Cylinder with Pilot Check Valve Pressure Lock",
                    "Main Drive System": "7.5 HP (5.5 kW) Helical Geared Motor with VFD",
                    "Rotation Modes": "Forward / Reverse / Free-Wheeling / Jogging Mode",
                    "Braking System": "Heavy-Duty Pneumatic Caliper Disc Brake (6–8 bar)",
                    "Loop Control": "Infrared Photoelectric Sensor for Auto Speed Match",
                    "Hydraulic Power Unit": "3.0 HP Independent Hydraulic Station (60L Reservoir)",
                    "Optional Accessories": "Hydraulic Coil Loading Car with Motorized Track (10-Ton)",
                    "Snubber / Hold-Down Arm": "Optional Pneumatic / Hydraulic Motorized Hold-Down Arm",
                    "Application": "Roll forming lines, CTL lines, Slitting plants, Tube mills",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "What is the maximum coil weight and width capacity of this hydraulic uncoiler?",
                                "a": "It is rated for continuous industrial duty with metal coils weighing up to 10,000 kg (10 Metric Tons) and coil widths up to 1250 mm or 1500 mm."
                    },
                    {
                                "q": "How does the hydraulic mandrel maintain expansion pressure during rotation?",
                                "a": "The mandrel features an integrated hydraulic cylinder with dual pilot-operated check valves that mechanically lock hydraulic pressure, preventing loosening even during power interruption."
                    },
                    {
                                "q": "Does this decoiler synchronize automatically with downstream roll forming or CTL lines?",
                                "a": "Yes, non-contact optical loop sensors detect coil sag between the uncoiler and forming mill, automatically modulating feed speed via VFD to maintain a smooth feeding loop."
                    },
                    {
                                "q": "What braking mechanism is used to prevent loose coil over-run?",
                                "a": "It employs a heavy-duty pneumatic caliper disc brake system linked to line stop commands, providing immediate, controlled deceleration without coil unwinding."
                    },
                    {
                                "q": "Is an optional motorized coil loading car available?",
                                "a": "Yes, we provide an optional 10-Ton Hydraulic Coil Car with V-cradle and motorized in-floor rail traversing that cuts coil loading time down to under 3 minutes."
                    },
                    {
                                "q": "What warranty and after-sales service does Gagan Engineering Works provide?",
                                "a": "We offer a 1-year comprehensive manufacturer warranty covering hydraulics, drive motors, and electricals, with complete on-site commissioning across Pan-India and export ports."
                    }
        ],
    },
    {
        "id": "automatic-ctl-machine",
        "name": "Automatic Cut To Length (CTL) Machine",
        "category": "Cut To Length Line",
        "categorySlug": "cut-to-length-line",
        "image": "/automatic-ctl.png",
        "images": [
                    "/automatic-ctl.png"
        ],
        "tagline": "High-Speed Precision Cut-to-Length Line for Heavy-Duty Metal Coil Processing Up to 6.0 mm",
        "shortDesc": "Complete automated cut-to-length line with 10-ton hydraulic decoiler, 9-roll gear-driven leveler, optical encoder shearing, and motorized exit conveyor.",
        "description": "The Automatic Cut-to-Length (CTL) Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an automated, heavy-duty coil processing line designed for precision flattening, high-speed measuring, and burr-free shearing of metal coils up to 6.0 mm thickness. Built to process Hot Rolled (HR), Cold Rolled (CR), Galvanized Iron (GI), Stainless Steel, and Aluminium coils, the line integrates an automated 10-Ton Hydraulic Decoiler, a 9-roll gear-driven precision leveler, an optical rotary encoder measuring bridge, a heavy mechanical/hydraulic guillotine shear, and a powered exit run-out conveyor. The leveler features 9 high-strength EN31 alloy steel rollers (114 mm diameter, hardened to 50–52 HRC and ground to mirror finish) driven through a heavy-duty distribution gearbox to eliminate coil set, crossbow, and edge wave. Controlled by a centralized Delta/Siemens PLC touchscreen console with Variable Frequency Drive (VFD), the line maintains a high cutting length tolerance of ±0.5 mm at line speeds up to 20 meters per minute. Operators can program up to 20 variable batch cut lengths on the touchscreen interface with automated scrap minimization and piece counter displays. Extensively utilized by steel service centers, automotive stamping vendors, electrical panel manufacturers, and PEB fabrication plants across India and overseas.",
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
                    "Buffer Table": "500 x 3000 mm Plain Precision Table",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "What coil gauges and material grades can this automatic CTL line level and cut?",
                                "a": "It processes coils up to 6.0 mm thickness in Mild Steel (MS), Galvanized Iron (GI), Stainless Steel, and Aluminium with strip widths up to 400 mm (or custom up to 1500 mm)."
                    },
                    {
                                "q": "What is the sheet length accuracy and how is it measured?",
                                "a": "An optical rotary encoder rolling directly against the moving strip feeds real-time pulses into the PLC, maintaining repeatable cutting tolerances of ±0.5 mm."
                    },
                    {
                                "q": "How does the 9-roll precision leveler eliminate sheet curvature and coil set?",
                                "a": "The 9 staggered EN31 alloy rollers subject the metal strip to controlled reverse plastic bending, neutralizing residual stresses and yielding flat sheet blanks."
                    },
                    {
                                "q": "What is the daily tonnage capacity of this Cut-to-Length line?",
                                "a": "Operating at 20 m/min, an 8-hour shift produces approximately 20 to 35 Metric Tons of precision cut blanks depending on sheet thickness and cut lengths."
                    },
                    {
                                "q": "Can different batch quantities and sheet lengths be programmed automatically?",
                                "a": "Yes, the touchscreen PLC supports up to 20 recipe programs, allowing automated execution of varying sheet lengths and piece counts without stopping."
                    },
                    {
                                "q": "What electrical and hydraulic components are utilized in this machine?",
                                "a": "We integrate genuine Yuken hydraulic valves and pumps, Delta/Siemens PLC controllers, and ABB/Schneider electrical switchgear for maximum reliability."
                    }
        ],
    },
    {
        "id": "c-z-purlin-roll-forming-machine",
        "name": "C / Z Purlin Roll Forming Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/ANDWEB/Default/2026/3/591020192/NG/CE/TB/4175789/product-jpeg-500x500.jpeg",
        "images": [
                    "https://5.imimg.com/data5/ANDWEB/Default/2026/3/591020192/NG/CE/TB/4175789/product-jpeg-500x500.jpeg"
        ],
        "tagline": "Interchangeable C & Z Section Purlin Line with Automated Size Change and Multi-Head Hole Punching",
        "shortDesc": "High-speed 16–20 station roll forming line producing structural C and Z purlins for Pre-Engineered Buildings (PEB) and solar structures.",
        "description": "The C / Z Purlin Roll Forming Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an advanced, high-yield continuous roll forming line engineered for manufacturing structural C-purlins and Z-purlins used extensively in Pre-Engineered Steel Buildings (PEB), solar mounting structures, warehouses, and industrial infrastructure. Built to process high-tensile galvanized steel and hot-rolled coils from 1.5 mm to 3.0 mm thickness, the machine features 16 to 20 progressive forming stations equipped with precision CNC-machined Cr12/EN31 vacuum heat-treated rollers (58–62 HRC) and solid 75 mm 40Cr alloy shafts. An innovative quick-change mechanical design allows operators to transition between C-section and Z-section profiles in under 30 minutes without disassembling roller sets, with web widths adjustable from 100 mm to 300 mm and flange heights from 40 mm to 80 mm. The line incorporates a multi-station hydraulic hole and slot punching unit for automated bolt-hole fabrication, followed by a hydraulic post-cut flying shear that produces clean, zero-distortion profile cut ends. Driven by a 25–30 HP heavy-duty motor through precision distribution gearboxes and orchestrated by a Delta/Siemens PLC touchscreen interface, the line delivers consistent forming speeds of 10 to 18 meters per minute with tight dimensional tolerances.",
        "specs": {
                    "Section Profiles": "C-Purlin (Web 100–300 mm) & Z-Purlin (Web 100–300 mm)",
                    "Flange Height Range": "40 mm to 80 mm (Customizable)",
                    "Lip Size Range": "10 mm to 25 mm",
                    "Material Thickness": "1.5 mm to 3.0 mm High-Tensile GI / HR / CR Steel",
                    "Forming Stations": "16 to 20 Progressive Forming Stages",
                    "Roller Metallurgy": "Cr12 / EN31 Vacuum Heat-Treated Tool Steel (58–62 HRC)",
                    "Shaft Diameter": "75 mm / 80 mm Solid 40Cr Alloy Steel",
                    "Profile Changeover Time": "Under 30 minutes (Quick-Rotate C to Z Mechanism)",
                    "Forming Speed": "10 to 18 meters per minute (VFD Controlled)",
                    "Hydraulic Hole Punching": "Multi-Station Pre/Post Punching for Web & Flange Holes",
                    "Shearing System": "Hydraulic Flying Shear / Stop-to-Shear (Cr12MoV Blade)",
                    "Main Motor Power": "20 HP to 25 HP Geared Motor with Heavy Chain/Gear Drive",
                    "Hydraulic Station": "7.5 HP Power Pack with Yuken Directional Valves",
                    "Control Console": "Delta / Siemens PLC Touchscreen HMI with Encoder Feedback",
                    "Cutting Length Accuracy": "± 1.0 mm per 10-meter purlin",
                    "Application": "PEB buildings, solar mounting racks, industrial warehouses, railway sheds",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "How long does it take to switch from C-purlin to Z-purlin profile?",
                                "a": "Our quick-adjust roller assembly allows changeover between C and Z profiles in under 30 minutes with minimal manual wrenching."
                    },
                    {
                                "q": "What sheet thicknesses and steel grades can this purlin line form?",
                                "a": "The line processes high-tensile Galvanized Iron (GI), Hot Rolled (HR), and Cold Rolled (CR) steel coils from 1.5 mm up to 3.0 mm thickness."
                    },
                    {
                                "q": "Can bolt holes and slot punching be integrated automatically in the line?",
                                "a": "Yes, the line features a multi-head hydraulic punch unit that punches web holes and flange slots at pre-programmed pitch intervals prior to shearing."
                    },
                    {
                                "q": "What web and flange dimensions can be produced?",
                                "a": "Web widths range from 100 mm to 300 mm, flange heights from 40 mm to 80 mm, and lips from 10 mm to 25 mm, adjustable via motorized or manual screw jacks."
                    },
                    {
                                "q": "How is length and punching accuracy controlled?",
                                "a": "A high-resolution optical rotary encoder synchronizes with the Delta/Siemens PLC to deliver punching and length cutting accuracy within ±1.0 mm."
                    },
                    {
                                "q": "What warranty and commissioning support are provided by Gagan Engineering?",
                                "a": "We provide a 1-year comprehensive warranty, foundation engineering drawings, on-site mechanical alignment, and full operator training."
                    }
        ],
    },
    {
        "id": "automatic-roofing-sheet-crimping-machine",
        "name": "Automatic Roofing Sheet Crimping Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png",
        "images": [
                    "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png"
        ],
        "tagline": "Curved Roof Sheet Crimping — High-Speed Automatic Hydraulic Profile Forming for Arch Sheds",
        "alternateName": [
            "Curved Roofing Sheet Crimping Machine",
            "Arch Roofing Sheet Curving Machine",
            "Crimping Curving Machine",
            "Curved Metal Sheet Bending Machine",
            "Self-Supporting Curved Roof Crimper"
        ],
        "keywords": "Automatic Roofing Sheet Crimping Machine, Curved Roofing Sheet Crimping Machine, Arch Roofing Sheet Curving Machine, Crimping Curving Machine India, Curved Sheet Bending Machine Price, PEB Curved Roof Crimper Khopoli",
        "shortDesc": "Automated crimping machine for curved roofing sheets used in industrial sheds, warehouses, and stadiums.",
        "description": "The Automatic Roofing Sheet Crimping Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is a high-speed hydraulic curved profile forming machine designed for bending pre-painted galvanized iron (PPGI), galvanized steel (GP), and aluminium roofing panels into smooth, uniform curved arches. Extensively deployed for constructing curved factory sheds, warehouse barrel canopies, petrol pump forecourts, aircraft hangars, agricultural grain silos, and modern architectural curved roofing, the machine accepts pre-profiled trapezoidal or corrugated sheets up to 1250 mm width and 0.3 mm to 0.8 mm thickness. Utilizing a precision CNC-contoured upper and lower crimping tool set driven by a 5.0 HP heavy hydraulic power pack, the machine introduces sequential micro-crimps at mathematically calibrated pitches to produce smooth, non-kinked circular arcs from a 2-meter radius up to infinity. A centralized Delta/Siemens PLC touchscreen interface allows the operator to input the building span, arch height, sheet length, and desired radius; the automated feed table then automatically steps the sheet through the crimping jaws with micrometer-level step indexing. Engineered with hardened alloy steel dies that prevent paint cracking or zinc coating peeling, this crimper delivers unmatched arch consistency and structural rigidity for heavy commercial roofing fabricators across India and global export markets.",
        "specs": {
                    "Sheet Width Supported": "Up to 1250 mm Standard Trapezoidal & Corrugated Profiles",
                    "Material Gauge Capacity": "0.30 mm to 0.80 mm (PPGI, GP, Aluminium, Galvalume)",
                    "Minimum Crimping Radius": "2.0 Meters (Curvature adjustable from 2m to infinity)",
                    "Crimping Mechanism": "High-Force Hydraulic Pressing Jaw with Synchronized Stepping",
                    "Die Tooling Material": "Cr12 Forged Alloy Steel, Vacuum Hardened (58–60 HRC)",
                    "Hydraulic Power Unit": "5.0 HP Power Pack with Yuken Control Valves",
                    "Feed Drive": "High-Torque Stepper / Servo Motor Driven Feeding Table",
                    "Step Indexing Accuracy": "± 0.2 mm per crimp step",
                    "Control Interface": "Delta / Siemens PLC Color Touchscreen with Radius Calculator",
                    "Cycle Speed": "25 to 35 crimps per minute (Continuous Automatic Cycle)",
                    "Paint Protection": "Polished Tooling Contours guarantee Zero Paint Cracking on PPGI",
                    "Sheet Support": "Dual 6-Meter Roller Infeed and Outfeed Support Tables",
                    "Total Connected Load": "Approx. 7.5 HP (3-Phase 415V, 50Hz)",
                    "Application": "Curved warehouse roofs, petrol pump canopies, stadium canopies, arch sheds",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "How does the machine calculate the crimping steps for a specific curved roof radius?",
                                "a": "The operator enters the target arc radius or shed span into the PLC touchscreen, which automatically calculates the required step distance and crimp depth."
                    },
                    {
                                "q": "Does crimping cause paint peeling or micro-cracking on colour-coated PPGI sheets?",
                                "a": "No. The Cr12 die contours are mirror-polished and radiused to distribute compressive bending smoothly, preventing micro-fractures in paint or zinc layers."
                    },
                    {
                                "q": "What sheet widths and profile shapes are compatible with this crimping machine?",
                                "a": "It accommodates standard profiled roofing sheets up to 1250 mm width, including trapezoidal box profiles and round-wave corrugated profiles."
                    },
                    {
                                "q": "What is the tightest curve radius that can be formed?",
                                "a": "The machine can form curves down to a tight 2.0-meter radius, extending all the way to gentle architectural arcs."
                    },
                    {
                                "q": "What is the production rate of curved panels per hour?",
                                "a": "Operating at 25 to 35 crimps per minute, a standard 6-meter curved roofing sheet is completed in approximately 2 to 3 minutes."
                    },
                    {
                                "q": "What warranty and after-sales support are provided?",
                                "a": "Gagan Engineering Works provides a 1-year comprehensive warranty, complete tooling spares, and on-site operator commissioning."
                    }
        ],
    },
    {
        "id": "corrugated-sheets-making-machine",
        "name": "Corrugated Sheets Making Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
        "images": [
                    "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
                    "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png"
        ],
        "alternateName": [
            "Tata Nali Sheet Making Machine",
            "GC Sheet Machine",
            "Galvanized Corrugated Sheet Roll Forming Machine",
            "Roofing Sheet Making Machine",
            "Liner Roofing Sheet Machine",
            "Tata Nali Roll Former",
            "Nali Sheet Machine"
        ],
        "keywords": "Tata Nali Sheet Making Machine, GC Sheet Machine, Corrugated Sheets Making Machine, Roofing Sheet Making Machine, Liner Roofing Sheet Machine, Galvanized Corrugated Sheet Roll Forming, Tata Nali Machine Price India, GC Sheet Machine Manufacturer Khopoli Maharashtra, Nali Patra Machine",
        "tagline": "Tata Nali & GC Corrugated Sheet Roll Forming Machine — High-Speed Sinusoidal Wave Profile Line for Industrial Roofing Sheets",
        "shortDesc": "Continuous 16–18 station sinusoidal wave roll forming line (Tata Nali & GC sheet profile) with hydraulic post-cut shear and PLC touchscreen control for GI, GP, PPGI, and liner roofing sheets.",
        "description": "The Corrugated Sheets Making Machine (widely known in India as the Tata Nali Sheet Making Machine or GC Sheet Machine) manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an industrial-grade continuous roll forming line designed for high-speed production of sinusoidal round-wave metal roofing, cladding, and liner panels. Engineered to process Galvanized Iron (GI), Pre-Painted Galvanized Iron (PPGI), Galvalume, and Aluminium coils from 0.15 mm to 0.80 mm thickness, the machine features 16 to 18 precision forming roller stations crafted from EN31/Cr12 forged tool steel with hard chrome electroplating (0.05 mm) to guarantee scratch-free finish on colour-coated stock. Producing the traditional high-demand Tata Nali circular wave profile (76 mm pitch, 18 mm depth) as well as commercial GC sheet and industrial liner roofing profiles, the machine is driven by a 7.5 HP heavy-duty motor through precision chain/gearbox transmission and paired with a high-speed hydraulic post-cut shear (Cr12MoV vacuum heat-treated blade) achieving line speeds of 15 to 20 meters per minute. A centralized Delta/Siemens PLC touchscreen console allows operators to program sheet batches with ±1.0 mm cutting precision. Widely used across India for manufacturing industrial factory sheds, warehouse roofing, agricultural poultry sheds, disaster relief housing, PEB wall liners, and perimeter barricading.",
        "specs": {
                    "Profile Type": "Standard Sinusoidal Corrugated Round Wave (Tata Nali / GC Profile: Pitch 76 mm, Depth 18 mm)",
                    "Raw Material": "GI, GP, PPGI, Galvalume, Colour-Coated Steel, Liner Sheet Coils, Aluminium",
                    "Sheet Thickness Capacity": "0.15 mm – 0.80 mm",
                    "Suitable Coil Width": "914 mm / 1000 mm / 1220 mm / 1250 mm",
                    "Effective Formed Width": "800 mm / 900 mm / 1050 mm (Customizable)",
                    "Roll Forming Stations": "16 to 18 Progressive Forming Stages",
                    "Roller Material": "Hardened EN31 / Cr12 Forged Alloy Steel with Hard Chrome (0.05 mm)",
                    "Shaft Diameter": "70 mm / 75 mm Solid 40Cr Alloy Steel",
                    "Forming Speed": "15 – 20 meters per minute (VFD Regulated)",
                    "Main Drive Motor": "7.5 HP Geared Motor with Heavy-Duty Transmission",
                    "Hydraulic Station": "5.0 HP Power Pack with Yuken Valves & Continuous Cooling",
                    "Shearing Mechanism": "Hydraulic Post-Cut Stop-to-Shear (Cr12MoV Blade, 60–62 HRC)",
                    "Control System": "Delta / Siemens PLC Touchscreen with High-Accuracy Encoder",
                    "Cutting Length Tolerance": "± 1.0 mm per 10-meter sheet",
                    "Decoiler Compatibility": "5-Ton Manual / 10-Ton Motorized Hydraulic Decoiler",
                    "Application": "Tata Nali roofing, GC sheets, liner roofing sheets, factory cladding, warehouse sheds",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Mumbai Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "What raw materials and sheet thicknesses can this corrugated sheet roll forming machine process?",
                                "a": "Our machine is engineered to form Galvanized Iron (GI), Pre-Painted Galvanized Iron (PPGI), Galvalume (Alu-Zinc), and Aluminium coils with thickness ranging from 0.15 mm up to 0.80 mm. The heavy-duty 40Cr shafts ensure rigidity across the full thickness spectrum."
                    },
                    {
                                "q": "What is the daily production capacity and output speed of this machine?",
                                "a": "Operating at continuous speeds of 15 to 20 meters per minute, a standard 8-hour shift easily yields 7,000 to 9,000 linear meters of corrugated roofing panels (approximately 15 to 20 metric tons depending on sheet gauge)."
                    },
                    {
                                "q": "How does the machine prevent scratching on colour-coated and printed roofing coils?",
                                "a": "All 16–18 forming rollers are CNC precision-contoured, heat-treated, and electroplated with 0.05 mm hard chrome mirror polish. This eliminates friction scuffing and ensures 100% scratch-free profile forming on pre-painted coils."
                    },
                    {
                                "q": "Can the machine automatically cut different custom sheet lengths on the fly?",
                                "a": "Yes. The integrated Delta/Siemens PLC touchscreen console allows the operator to pre-program multiple batch quantities with variable lengths (e.g. 100 sheets at 3.0 m, 50 sheets at 4.5 m). An optical rotary encoder ensures ±1.0 mm precision cutting without manual marking."
                    },
                    {
                                "q": "What decoiler / uncoiler should be used with this corrugated roll forming line?",
                                "a": "For entry-level or mobile workshops, a 5-ton passive manual uncoiler is standard. For continuous high-volume industrial lines, we integrate our 10-Ton Motorized Hydraulic Decoiler with motorized mandrel expansion and pneumatic tension braking."
                    },
                    {
                                "q": "What warranty and after-sales support does Gagan Engineering Works provide?",
                                "a": "We provide a 1-year comprehensive manufacturer warranty covering mechanical drives, hydraulic power packs, and PLC electronics. Our factory technicians provide on-site installation, commissioning, and operator training across all Indian states and overseas export markets."
                    }
        ],
    },
    {
        "id": "tata-nali-sheet-making-machine",
        "name": "Tata Nali Sheet Making Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
        "images": [
                    "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
                    "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png"
        ],
        "alternateName": [
            "Tata Nali Roll Forming Machine",
            "Tata Nali Machine",
            "Nali Patra Machine",
            "GC Sheet Making Machine",
            "Tata Nali Patra Roll Former",
            "Sinusoidal Wave Nali Sheet Line"
        ],
        "keywords": "Tata Nali Sheet Making Machine, Tata Nali Machine Price in India, Tata Nali Roll Forming Machine, Nali Patra Machine, GC Sheet Machine, Tata Shaktee Type Nali Sheet Machine Khopoli Maharashtra, Nali Patra Banane Ki Machine",
        "tagline": "Heavy-Duty 16–18 Station Tata Nali Roll Forming Line — Precision Sinusoidal Wave Roofing Profile",
        "shortDesc": "Continuous 16–18 station roll forming line designed specifically for producing high-tensile Tata Nali sinusoidal round-wave corrugated roofing sheets and GC sheets with hydraulic cut-to-length shear and PLC control.",
        "description": "The Tata Nali Sheet Making Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an industrial-grade continuous roll forming machine designed specifically to produce the widely used Indian 'Tata Nali' sinusoidal wave corrugated roofing sheets. Engineered to process Galvanized Iron (GI), Pre-Painted Galvanized Iron (PPGI), Galvalume, and Aluminium coils from 0.15 mm to 0.80 mm thickness, the line forms the exact traditional circular wave pitch (76 mm) and wave depth (18 mm). Featuring 16 to 18 progressive forming stations with mirror-polished hard chrome rollers (EN31/Cr12 alloy steel), solid 75 mm 40Cr alloy shafts, and a heavy-duty hydraulic post-cut shear, the machine delivers a continuous output speed of 15 to 20 meters per minute with ±1.0 mm cut accuracy. Ideal for industrial shed roofing, warehouse roofing, poultry sheds, and rural residential construction across India.",
        "specs": {
                    "Profile Type": "Standard Sinusoidal Wave (Tata Nali Profile: Pitch 76 mm / 3\", Depth 18 mm)",
                    "Material Capability": "GI, GP, PPGI, Galvalume, Colour-Coated Steel, Aluminium",
                    "Sheet Thickness": "0.15 mm – 0.80 mm",
                    "Coil Width Supported": "914 mm / 1000 mm / 1220 mm / 1250 mm",
                    "Forming Stations": "16 to 18 Progressive Forming Stages",
                    "Roller Tooling": "Cr12 / EN31 Forged Tool Steel, Vacuum Hardened & 0.05 mm Chrome Plated",
                    "Shaft Diameter": "75 mm Solid 40Cr Forged Alloy Steel",
                    "Production Speed": "15 – 20 meters per minute (VFD Regulated)",
                    "Main Drive Motor": "7.5 HP Geared Motor with Heavy-Duty Double Chain Drive",
                    "Hydraulic Station": "5.0 HP Power Pack with Yuken Directional Valves",
                    "Shearing Mechanism": "Hydraulic Profile Post-Cut Guillotine (Cr12MoV Blade, 60–62 HRC)",
                    "Control System": "Delta / Siemens PLC Touchscreen with Optical Rotary Encoder",
                    "Cutting Length Accuracy": "± 1.0 mm per 10-meter sheet",
                    "Decoiler Compatibility": "5-Ton Manual / 10-Ton Motorized Hydraulic Decoiler",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Mumbai Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "What is the price of a Tata Nali sheet making machine in India?",
                                "a": "Prices for an industrial Tata Nali roll forming machine typically range between ₹8,50,000 and ₹18,50,000 depending on automation grade (semi-automatic vs fully automatic PLC line), number of forming stations (16 vs 18 stations), and whether an uncoiler/decoiler is included."
                    },
                    {
                                "q": "What are the exact pitch and wave depth dimensions of the Tata Nali profile?",
                                "a": "The standard Tata Nali profile produced by this machine features a 76 mm (3-inch) pitch from crest to crest and an 18 mm wave depth, conforming to Indian Bureau of Indian Standards (BIS) industrial roofing specifications."
                    },
                    {
                                "q": "What raw material coils can be processed on this Tata Nali machine?",
                                "a": "The machine processes Galvanized Iron (GI), Pre-Painted Galvanized Iron (PPGI), Galvalume (Alu-Zinc 550 MPa), and Aluminium coils with thickness ranging from 0.15 mm to 0.80 mm."
                    },
                    {
                                "q": "How many sheets can this machine produce in an 8-hour shift?",
                                "a": "Operating at 15 to 20 meters per minute, an 8-hour production shift yields approximately 7,000 to 9,000 linear meters of finished Tata Nali roofing panels (approx. 15 to 22 metric tons)."
                    },
                    {
                                "q": "How does the machine prevent scratching on colour-coated coils?",
                                "a": "All rollers are CNC contour-turned and electroplated with 0.05 mm hard chrome mirror plating. This eliminates friction scuffing and guarantees scratch-free forming on pre-painted and printed stock."
                    },
                    {
                                "q": "What commissioning support does Gagan Engineering Works provide?",
                                "a": "We provide complete foundation layout drawings, on-site mechanical alignment, electrical commissioning, and operator training across all Indian states and overseas export markets with a 1-year comprehensive warranty."
                    }
        ],
    },
    {
        "id": "peb-roofing-sheet-making-machine",
        "name": "PEB Roofing Sheet Making Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png",
        "images": [
                    "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png",
                    "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg"
        ],
        "alternateName": [
            "PEB Roofing Sheet Roll Forming Line",
            "Industrial Shed Roofing Sheet Machine",
            "PEB Trapezoidal Profile Machine",
            "PEB Liner Roofing Sheet Machine",
            "Pre-Engineered Building Sheet Former"
        ],
        "keywords": "PEB Roofing Sheet Making Machine, PEB Roofing Line Price India, Industrial Shed Sheet Machine, PEB Liner Sheet Roll Former, Trapezoidal Roofing Sheet Machine Khopoli Maharashtra, Industrial PEB Sheet Line",
        "tagline": "Industrial Roll Forming Line for Pre-Engineered Building (PEB) Roofing, Liner & Cladding Panels",
        "shortDesc": "Automated continuous roll forming line engineered for industrial Pre-Engineered Building (PEB) roofing panels, interior liner sheets, and warehouse cladding with hydraulic post-cut guillotine and PLC automation.",
        "description": "The PEB Roofing Sheet Making Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an automated continuous roll forming line specifically designed for manufacturing Pre-Engineered Building (PEB) roofing sheets, interior wall liner panels, and warehouse cladding. Engineered to process high-tensile 550 MPa Galvalume, Zincalume, Pre-Painted Galvanized Iron (PPGI), and colour-coated steel coils from 0.30 mm to 0.80 mm gauge, the line features 18 to 22 precision roll forming stations driven by an 11 kW heavy motor. Equipped with a hydraulic post-cut shear with Cr12MoV vacuum heat-treated blades and an optical rotary encoder, the machine delivers line speeds of 18 to 25 meters per minute with cutting length tolerances within ±1.0 mm. Supported by dual infeed guides, run-out collection tables, and optional 10-Ton motorized hydraulic decoilers, it is the primary choice for PEB steel building contractors, industrial shed fabricators, and commercial roofing suppliers across India and export markets.",
        "specs": {
                    "Profile Type": "Industrial PEB Trapezoidal Rib / Liner Profile (Standard 1000 mm / 1050 mm cover)",
                    "Raw Material": "PPGI, Pre-Painted Galvalume (AZ150), High-Tensile 550 MPa Steel, Aluminium",
                    "Material Thickness": "0.30 mm to 0.80 mm",
                    "Infeed Coil Width": "1220 mm / 1250 mm Standard Steel Coils",
                    "Roll Forming Stations": "18 to 22 Progressive Forming Stations",
                    "Roller Tooling Material": "Forged EN31 / Cr12 Tool Steel with 0.05 mm Hard Chrome Finish",
                    "Shaft Diameter": "75 mm / 80 mm Solid 40Cr Alloy Steel",
                    "Operating Line Speed": "18 – 25 meters per minute (Continuous VFD Speed)",
                    "Main Motor Power": "11 kW (15 HP) Helical Geared Motor with VFD Inverter",
                    "Cutting Mechanism": "Hydraulic Profile Stop-Cut Guillotine (Cr12MoV Blade, 60–62 HRC)",
                    "Hydraulic Unit": "5.5 kW Heavy-Duty Power Pack with Integrated Oil Cooler",
                    "Control System": "Delta / Siemens PLC Touchscreen with Job Memory & Batch Counter",
                    "Cutting Tolerance": "± 1.0 mm Length Tolerance on 12-Meter Industrial Sheets",
                    "Decoiler Compatibility": "10-Ton Motorized Hydraulic Decoiler with Mandrel Expansion",
                    "Application": "PEB industrial warehouses, factory sheds, agricultural buildings, airport hangars",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Mumbai Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "What makes this machine suitable for Pre-Engineered Building (PEB) projects?",
                                "a": "PEB structures require high-tensile 550 MPa steel sheets with precise overlapping crests, anti-capillary grooves, and exact length tolerances for watertight roof sealing. This line is specifically calibrated for these rigorous engineering standards."
                    },
                    {
                                "q": "Can this line produce both roof panels and wall liner cladding?",
                                "a": "Yes. With tooling adjustments or dual-deck configurations, the line produces primary roof profiles as well as shallow-rib interior liner sheets widely used in insulated PEB buildings."
                    },
                    {
                                "q": "What is the typical production speed and output capacity?",
                                "a": "The line operates at 18 to 25 meters per minute, yielding 8,000 to 12,000 linear meters (approx. 20 to 30 metric tons) per 8-hour shift."
                    },
                    {
                                "q": "What decoiler is recommended for a continuous PEB sheet line?",
                                "a": "For continuous production, our 10-Ton Motorized Hydraulic Decoiler with hydraulic mandrel expansion and pneumatic tension brake is recommended to handle full commercial mother coils."
                    },
                    {
                                "q": "What warranty and after-sales support are provided?",
                                "a": "Gagan Engineering Works provides a 1-year comprehensive warranty, foundation engineering support, on-site alignment, and lifelong technical assistance from our Khopoli engineering team."
                    }
        ],
    },
    {
        "id": "semi-automatic-pipe-counter-boring-and-facing-machine",
        "name": "Semi-Automatic Pipe Counter Boring and Facing Machine",
        "category": "Roll Forming & Sheet Metal",
        "categorySlug": "roll-forming-sheet-metal",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550582531/TR/XN/QZ/4175789/product-jpeg-500x500.jpg",
        "images": [
                    "https://5.imimg.com/data5/ANDROID/Default/2025/10/550582531/TR/XN/QZ/4175789/product-jpeg-500x500.jpg"
        ],
        "tagline": "Precision Pipe End Facing, Chamfering & Counter Boring Up to 60 mm OD with Hydraulic Clamping and VFD Speed Control",
        "shortDesc": "Heavy-duty semi-automatic pipe counter boring and facing machine for accurate tube end preparation and beveling up to 60 mm OD.",
        "description": "The Semi-Automatic Pipe Counter Boring and Facing Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an industrial end-finishing machine designed for high-precision end facing, external chamfering, and internal counter-boring of steel, stainless steel, brass, and aluminium round pipes up to 60 mm Outside Diameter (OD). Powered by a 5.0 HP heavy-duty spindle motor with Variable Frequency Drive (VFD) speed regulation from 100 to 1450 RPM, the machine features a dedicated 1.0 HP hydraulic power pack (60-litre capacity) driving dual self-centering V-jaw hydraulic clamps that rigidly secure the tube without surface marring or wall ovality. A multi-tool cutter head equipped with standard indexable carbide inserts simultaneously faces the pipe end perpendicular to the centerline, applies an external weld prep bevel (30° / 37.5° / 45°), and counter-bores the internal diameter to strict dimensional tolerances (±0.05 mm) in a single rapid 8 to 15-second cycle. An automated length stop and hydraulic feed cylinder ensure repeatable machining depths across high-volume production runs. Widely deployed in automotive exhaust plants, shock absorber manufacturing, boiler tube fabrication, scaffolding tube processing, and furniture tube factories across India and global export markets.",
        "specs": {
                    "Max Pipe Outside Diameter": "Up to 60 mm OD (Minimum 15 mm OD)",
                    "Pipe Wall Thickness": "0.8 mm to 6.0 mm",
                    "Machining Capabilities": "End Facing, External Chamfering, Internal Counter-Boring",
                    "Spindle Drive Motor": "5.0 HP (3.7 kW, 1450 RPM) Heavy-Duty Spindle Motor",
                    "Speed Regulation": "100 to 1450 RPM via Variable Frequency Drive (VFD)",
                    "Tool Head Configuration": "Multi-Tool Holder with Standard Indexable Carbide Inserts",
                    "Clamping Mechanism": "Rigid Self-Centering Hydraulic V-Jaw Clamping",
                    "Feed Mechanism": "Hydraulic Automated Feed Stroke with Micrometer Depth Stop",
                    "Machining Cycle Time": "8 to 15 seconds per pipe end",
                    "Machining Tolerance": "± 0.05 mm End Perpendicularity & Depth Repeatability",
                    "Hydraulic System": "1.0 HP Power Pack (60-Litre Reservoir with Level Indicator)",
                    "Machine Bed": "Cast Iron Stress-Relieved Bed with Precision Linear Guide Ways",
                    "Coolant System": "Integrated Flood Coolant Pump with Chip Collection Tray",
                    "Operating Mode": "Manual, Semi-Automatic & Auto Cycle with Foot Switch Control",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "What pipe outer diameter and wall thickness range can this machine handle?",
                                "a": "It handles round pipes and industrial tubes from 15 mm up to 60 mm Outside Diameter (OD) with wall thicknesses from 0.8 mm up to 6.0 mm."
                    },
                    {
                                "q": "Does the machine face, chamfer, and counter-bore simultaneously in one stroke?",
                                "a": "Yes. The custom multi-tool cutter head carries three indexable carbide tool holders that perform facing, ID counter-boring, and OD chamfering in a single automated hydraulic feed cycle."
                    },
                    {
                                "q": "What cutting tool inserts are used and how easy are they to replace?",
                                "a": "It uses standard ISO industrial indexable carbide inserts that can be indexed or swapped in under 2 minutes without removing the cutter head."
                    },
                    {
                                "q": "How does the hydraulic clamping prevent pipe deformation or ovality on thin tubes?",
                                "a": "The self-centering V-jaws distribute hydraulic pressure symmetrically, and the clamping hydraulic regulator can be fine-tuned to prevent crushing thin-walled tubing."
                    },
                    {
                                "q": "What is the production throughput per 8-hour shift?",
                                "a": "With a cycle time of 8 to 15 seconds per end, a single operator processes 1,500 to 2,400 pipe ends per 8-hour shift."
                    },
                    {
                                "q": "What warranty and spare parts availability does Gagan Engineering guarantee?",
                                "a": "We provide a 1-year comprehensive manufacturer warranty, genuine replacement tool holders, hydraulic seals, and rapid technician support."
                    }
        ],
    },
    {
        "id": "double-head-electric-bra-cup-moulding-machine",
        "name": "Double Head Electric Bra Cup Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg",
        "images": [
                    "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg"
        ],
        "tagline": "Twin-Station High-Output Bra Cup Moulding Machine with Digital PID Thermal Regulators",
        "shortDesc": "Double-station electric moulding press engineered for seamless bra cup manufacturing with PID thermal control.",
        "description": "The Double Head Electric Bra Cup Moulding Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is the industry benchmark twin-station thermal moulding press designed for high-volume intimate apparel, swimwear, and sports lingerie manufacturing. Featuring two independent pressing heads mounted on a heavy-duty stress-relieved steel frame, the machine allows a single operator to load and unload one station while the opposing station undergoes heated compression dwell—effectively doubling production throughput to 400–600 pairs per 8-hour shift without increasing factory floor footprint. Each pressing station is equipped with precision top-and-bottom heating platens controlled by dual-zone microprocessor PID digital temperature regulators (ambient to 250°C) with ±1.5°C thermal stability, ensuring uniform heat transfer through polyurethane (PU) foam, memory foam, spacer fabric, and laminated microfibers. A heavy-duty pneumatic cylinder delivers 6 to 8 bar clamping pressure with programmable digital dwell timers and dual-hand optical safety push-buttons to protect the operator. Interchangeable CNC-machined aluminium bullet dies allow quick changeover across cup sizes 28A to 44DD in under 15 minutes. Trusted by premier intimate wear manufacturers across India, Sri Lanka, Bangladesh, Vietnam, and international export markets.",
        "specs": {
                    "Configuration": "Twin-Station Double-Head Independent Thermal Press",
                    "Production Capacity": "400 to 600 pairs / 8-hour shift (Single Operator)",
                    "Cup Size Range": "28A to 44DD (Full range of interchangeable CNC moulds)",
                    "Heating System": "Top & Bottom Heating with Dual-Zone Digital PID Regulators",
                    "Temperature Range": "Ambient to 250°C (±1.5°C Precision Stability)",
                    "Heating Power": "4.5 kW to 6.0 kW Connected Electrical Load",
                    "Clamping Force": "High-Force Pneumatic Clamping Cylinder (6–8 bar)",
                    "Cycle Dwell Timer": "Digital Timer Programmable from 5 to 99 seconds",
                    "Platen Metallurgy": "High-Grade Hardened Tool Steel with Mirror Buffing",
                    "Mould Material": "High-Conductivity Aircraft-Grade CNC Aluminium Alloys",
                    "Safety Mechanism": "Dual-Hand Synchronous Start Buttons + Emergency Stop",
                    "Material Compatibility": "PU Foam, Memory Foam, Laminated Spandex, Polyester Fiberfill",
                    "Electrical Standard": "3-Phase 415V AC, 50Hz (Customizable for 220V/380V/480V 60Hz)",
                    "Compressed Air Requirement": "6 to 8 kg/cm² Clean Compressed Air Supply",
                    "Application": "Seamless bra cups, swimwear cups, sports bra inserts, bridal lingerie",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "What is the daily output capacity of this double head machine?",
                                "a": "A single operator produces approximately 400 to 600 pairs of seamless bra cups per 8-hour shift depending on foam thickness and dwell time."
                    },
                    {
                                "q": "Can the moulding dies/cups be changed for different sizes?",
                                "a": "Yes, our CNC moulds are fully interchangeable. You can swap cup sizes (from 28A to 44DD) in less than 15 minutes using standard quick-lock bolts."
                    },
                    {
                                "q": "How does the PID temperature controller prevent yellowing or burning on delicate foam?",
                                "a": "Microprocessor-driven PID controllers maintain temperature within ±1.5°C of setpoint, preventing thermal overshoot that causes PU foam scorching or yellowing."
                    },
                    {
                                "q": "What power connection and compressed air are required at the factory?",
                                "a": "It operates on standard 3-Phase 415V AC electricity (or 220V on request) with 6–8 bar clean, dry compressed air supply."
                    },
                    {
                                "q": "Does the machine support push-up pads and laminated fabric cups?",
                                "a": "Yes, the high-force pneumatic clamping and deep platen clearance accommodate flat foam, graduated push-up pads, and pre-laminated fabric blanks."
                    },
                    {
                                "q": "What warranty and operator training does Gagan Engineering Works provide?",
                                "a": "We provide a 1-year comprehensive manufacturer warranty, complete mould set documentation, and on-site operator training across India and export markets."
                    }
        ],
    },
    {
        "id": "bra-cup-fabric-moulding-machine",
        "name": "Bra Cup Fabric Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550584110/ET/BP/NY/4175789/product-jpeg-500x500.jpg",
        "images": [
                    "https://5.imimg.com/data5/ANDROID/Default/2025/10/550584110/ET/BP/NY/4175789/product-jpeg-500x500.jpg"
        ],
        "tagline": "Precise Fabric Cup Shaping with Consistent Edge Finish and Zero Wrinkling",
        "shortDesc": "Specialized press for moulding laminated and woven fabrics into seamless bra cup profiles.",
        "description": "The Bra Cup Fabric Moulding Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an intimate apparel thermal press engineered specifically for shaping woven fabrics, microfibers, cotton-spandex, knitted laces, and laminated textiles into seamless, wrinkle-free bra cup covers and contour panels. Fabric moulding requires delicate thermal regulation and perimeter tension control to prevent fabric puckering, scorch discoloration, or grain distortion. This machine features interchangeable CNC-machined aluminium bullet and bowl dies paired with a perimeter pneumatic fabric clamping ring that holds the fabric under uniform radial tension throughout the thermal forming stroke. Powered by dual-zone digital PID heating controllers (ambient to 240°C) with optional non-stick Teflon-coated platens, it preserves delicate pastel, white, and sheer fabrics with zero thermal degradation. With cycle times of just 20 to 35 seconds per press, a single operator achieves outputs of 500 to 700 pieces per shift. Extensively deployed in lingerie factories across India and global export centers for producing seamless T-shirt bras, sports brassieres, activewear contour inserts, and swimwear covers.",
        "specs": {
                    "Material Compatibility": "Woven fabrics, microfibers, cotton-spandex, knitted lace, polyester",
                    "Mould Tooling": "Interchangeable Aircraft-Grade CNC Aluminium Bullet & Bowl Dies",
                    "Tensioning System": "Perimeter Pneumatic Fabric Clamp Ring for Wrinkle-Free Shaping",
                    "Pressing Cycle Time": "20 to 35 seconds per cycle (500–700 pcs / 8-hour shift)",
                    "Heating System": "Top & Bottom Heating with Digital Dual-Zone PID Thermostats",
                    "Temperature Range": "Ambient to 240°C (±1°C Sensitive Control for Synthetic Fabrics)",
                    "Platen Coating": "High-Temperature Industrial Teflon Coating (Prevents Scorch Marks)",
                    "Clamping Pressure": "Pneumatic Cylinder with Precision Pressure Regulator (5–7 kg/cm²)",
                    "Cycle Control": "Programmable Digital Countdown Timer with Auto-Release",
                    "Operator Safety": "Dual-Hand Safety Interlock + Emergency Stop Switch",
                    "Power Connection": "Single-Phase 220V AC or 3-Phase 415V AC (3.5 kW Connected Load)",
                    "Cup Size Range": "Accommodates standard cup sizes from 28A up to 44DD",
                    "Air Consumption": "Approx. 0.3 m³/min at 6 bar",
                    "Application": "Seamless T-shirt bras, sports bra covers, activewear inserts, swimwear",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "How does this machine prevent wrinkling or puckering on thin, stretchy fabrics?",
                                "a": "A synchronized perimeter pneumatic clamp ring holds the fabric uniformly around the die perimeter, applying radial tension as the bullet mould advances."
                    },
                    {
                                "q": "Does this machine prevent fabric burning or discoloration on light fabrics?",
                                "a": "Yes, the precision digital temperature regulator and teflon-coated platen options prevent scorch marks on white and delicate pastel fabrics."
                    },
                    {
                                "q": "What is the production cycle time and throughput per shift?",
                                "a": "Cycle times range from 20 to 35 seconds, allowing an operator to produce 500 to 700 finished fabric cup covers per 8-hour shift."
                    },
                    {
                                "q": "Can dies be swapped out for different cup shapes and bra sizes?",
                                "a": "Yes, CNC aluminium bullet and bowl dies are quick-detach, enabling size changes between 28A and 44DD in under 10 minutes."
                    },
                    {
                                "q": "What power supply and compressor pressure are needed?",
                                "a": "It operates on single-phase 220V or 3-phase 415V with 5–7 kg/cm² compressed air supply."
                    },
                    {
                                "q": "What warranty and after-sales service are included?",
                                "a": "We provide a 1-year comprehensive warranty, spare heating elements, and on-site commissioning across all textile manufacturing hubs."
                    }
        ],
    },
    {
        "id": "foam-bra-cup-moulding-machine",
        "name": "Foam Bra Cup Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586856/YP/VU/KK/4175789/product-jpeg-500x500.jpg",
        "images": [
                    "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586856/YP/VU/KK/4175789/product-jpeg-500x500.jpg"
        ],
        "tagline": "Polyurethane & Memory Foam Hot-Press Cup Forming with Permanent Shape Retention",
        "shortDesc": "Thermal compression machine for forming high-density PU and memory foam bra cups.",
        "description": "The Foam Bra Cup Moulding Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is a heavy-duty thermal compression press engineered for hot-press moulding of polyurethane (PU) foam, high-resilience (HR) foam, memory foam, and spacer fabric sheets into ergonomic, dimensionally stable bra cup shapes. The machine utilizes high-temperature dual upper and lower heated platens equipped with high-conductivity aluminium moulding bullet dies that distribute heat uniformly throughout the foam core. This uniform thermal profile ensures permanent molecular shape retention, consistent cup depth, and perfectly even wall thickness across the entire cup perimeter without cell collapse or foam hardening. Controlled by digital PID temperature controllers (ambient to 260°C) with programmable heating dwell timers and high-force pneumatic clamping cylinders, the machine delivers repeatable outputs up to 500 pieces per shift. Widely used across intimate apparel, sportswear, swimwear, and orthopedic padding manufacturing plants across India, Sri Lanka, Bangladesh, and overseas markets.",
        "specs": {
                    "Supported Foam Types": "Polyurethane (PU) Foam, Memory Foam, High-Resilience (HR) Foam, Spacer Fabric",
                    "Production Capacity": "350 to 500 pieces / 8-hour shift",
                    "Heating Configuration": "Independent Upper & Lower Heated Platens",
                    "Temperature Range": "50°C to 260°C Adjustable with ±1.5°C Microprocessor Precision",
                    "Heating Power": "4.5 kW to 6.5 kW Connected Electrical Load",
                    "Clamping Mechanism": "High-Force Pneumatic Cylinder with Guided Tie-Rods",
                    "Operating Pressure": "6 to 8 bar Compressed Air Supply",
                    "Mould Metallurgy": "High-Thermal Conductivity CNC Aluminium Alloy Bullet Moulds",
                    "Dwell Timer": "Digital Electronic Timer (10 to 99 seconds with Auto Release)",
                    "Cup Sizing Flexibility": "Interchangeable Mould Dies for Cups 28A through 44DD",
                    "Operator Safety": "Synchronous Two-Hand Push Button Start & Safety Guard",
                    "Electrical Requirement": "3-Phase 415V AC, 50Hz (Customizable for Global Grids)",
                    "Machine Construction": "Rigid Fabricated Heavy Steel Plate Structure (Low Vibration)",
                    "Application": "Moulded PU foam bra cups, memory foam inserts, shoulder pads, sports padding",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "Can this machine handle memory foam and high-density foam?",
                                "a": "Yes, the dual-heated platens allow controlled heat penetration ideal for memory foam, dense PU foam, and breathable spacer fabrics."
                    },
                    {
                                "q": "How does the dual-heating system prevent foam yellowing or cell burning?",
                                "a": "Precision digital PID temperature regulators maintain platen temperature within ±1.5°C, ensuring optimal thermal dwell without scorching the polymer matrix."
                    },
                    {
                                "q": "What is the production capacity per 8-hour shift?",
                                "a": "A single operator produces 350 to 500 pieces per 8-hour shift depending on foam thickness and dwell time."
                    },
                    {
                                "q": "How long does it take to change moulds between different cup sizes?",
                                "a": "Mould changeover takes under 15 minutes using standard quick-clamp fixtures, accommodating cup sizes 28A through 44DD."
                    },
                    {
                                "q": "What utilities are required for installation?",
                                "a": "It requires standard 3-Phase 415V AC power supply and 6–8 bar compressed air connection."
                    },
                    {
                                "q": "What warranty and commissioning support are provided by Gagan Engineering?",
                                "a": "We offer a 1-year comprehensive warranty, technical tooling drawings, and on-site operator commissioning across Pan-India."
                    }
        ],
    },
    {
        "id": "padded-bra-cup-moulding-machine",
        "name": "Padded Bra Cup Moulding Machine",
        "category": "Bra Cup Moulding Machine",
        "categorySlug": "bra-cup-moulding-machine",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/5/608537665/KG/TS/VJ/4175789/padded-bra-cup-moulding-machine-500x500.png",
        "images": [
                    "https://5.imimg.com/data5/SELLER/Default/2026/5/608537665/KG/TS/VJ/4175789/padded-bra-cup-moulding-machine-500x500.png"
        ],
        "tagline": "Multi-Layer Padded Cup Moulding Combining Foam, Fabric, and Inner Lining in One Cycle",
        "shortDesc": "Specialized multi-layer press designed for premium push-up and graduated padded bra cups.",
        "description": "The Padded Bra Cup Moulding Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is a multi-layer composite thermal moulding press designed specifically for manufacturing premium push-up bra cups, graduated contour pads, and laminated multi-layer intimate wear. Unlike standard single-layer foam presses, this specialized machine synchronizes heat penetration and graduated compression across three distinct composite layers—outer decorative fabric, variable-thickness PU foam core, and inner soft cotton/polyester lining—in a single, unified pressing cycle. This single-shot thermal fusion eliminates intermediate adhesive spraying, guarantees zero layer delamination, and produces smooth, wrinkle-free push-up pads with seamless graduated thickness transitions from a thick lower cup base to an ultra-thin feather edge. Controlled by independent top-and-bottom digital PID thermostats (up to 260°C) with programmable dwell timers and dual-hand optical safety interlocks, the machine delivers outputs of 300 to 450 pairs per shift. Extensively utilized by premier intimate apparel brands and export garment factories across India, Sri Lanka, and international markets.",
        "specs": {
                    "Moulding Capability": "Multi-Layer Composite Fusion (Fabric + PU Foam + Inner Lining)",
                    "Pad Style Support": "Graduated Push-Up Pads, Demi Cups, Balconette, Contour T-Shirt Bras",
                    "Production Output": "300 to 450 pairs / 8-hour shift",
                    "Heating System": "Independent Top & Bottom Heated Platens with Dual PID Controllers",
                    "Temperature Range": "Ambient to 260°C (±1.5°C Microprocessor Accuracy)",
                    "Cycle Timer": "Programmable Digital Countdown Timer (20 to 60 seconds dwell)",
                    "Clamping System": "Heavy-Duty Guided Pneumatic Cylinder (6 to 8 bar)",
                    "Mould Metallurgy": "Aircraft-Grade CNC Aluminium Graduated Push-Up Moulds",
                    "Layer Bonding": "Thermal Compression Fusion (Eliminates Delamination & Adhesive Odours)",
                    "Operator Safety": "Dual-Hand Start Buttons + Transparent Polycarbonate Safety Enclosure",
                    "Connected Electrical Load": "5.0 kW to 7.5 kW (3-Phase 415V AC, 50Hz)",
                    "Cup Size Range": "Interchangeable Tooling for Push-Up Sizes 30A through 40D",
                    "Machine Frame": "Heavy ISMB Steel Box Section Frame with Heavy Platen Guides",
                    "Application": "Push-up bras, padded swimwear, bridal contour lingerie, shapewear",
                    "Origin & Port": "Khopoli, Maharashtra (65 km from Nhava Sheva / JNPT Port)"
        },
        "featured": True,
        "faqs": [
                    {
                                "q": "Can this machine mould graduated push-up cups?",
                                "a": "Yes, custom graduated CNC moulds can be installed to create push-up pads with varying bottom-to-top thickness."
                    },
                    {
                                "q": "How does it bond outer fabric, foam, and inner lining in a single cycle?",
                                "a": "Controlled top and bottom heating platens activate thermoset adhesives or adhesive mesh uniformly, fusing all 3 layers under pneumatic pressure."
                    },
                    {
                                "q": "Does single-shot thermal moulding eliminate the need for toxic spray adhesives?",
                                "a": "Yes, it supports thermal adhesive films and pre-laminated composite blanks, significantly reducing solvent fumes and airborne spray odours."
                    },
                    {
                                "q": "What cup shapes and push-up pad profiles can be produced?",
                                "a": "It produces graduated contour pads, demi-cup push-ups, plunge pads, and balcony silhouettes across sizes 30A through 40D."
                    },
                    {
                                "q": "What are the power and air requirements for factory installation?",
                                "a": "It requires 3-Phase 415V AC power (5.0 to 7.5 kW connected load) and 6–8 bar compressed air."
                    },
                    {
                                "q": "What warranty and technical after-sales support does Gagan Engineering offer?",
                                "a": "We provide a 1-year comprehensive warranty, complete die engineering support, and rapid on-site commissioning across India."
                    }
        ],
    },
]

SEED_CATEGORIES = [
    {"id": "all", "name": "All Machinery"},
    {"id": "roll-forming-sheet-metal", "name": "Roll Forming & Sheet Metal"},
    {"id": "cut-to-length-line", "name": "Cut To Length Line"},
    {"id": "bra-cup-moulding-machine", "name": "Bra Cup Moulding Machine"},
    {"id": "bending-machines", "name": "Bending Machines"},
    {"id": "facing-machines", "name": "Facing Machines"},
    {"id": "threading-machines", "name": "Threading Machines"},
    {"id": "recoiling-decoiling-machines", "name": "Re-coiling & De-coiling Machines"},
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
    image: Optional[str] = ""
    tagline: Optional[str] = ""
    shortDesc: Optional[str] = ""
    description: Optional[str] = ""
    specs: Optional[Dict[str, str]] = {}
    featured: Optional[bool] = False
    faqs: Optional[List[FAQItem]] = []
    images: Optional[List[str]] = []    # up to 5 ordered photo URLs
    video_url: Optional[str] = None    # YouTube URL only

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
    images: Optional[List[str]] = None  # up to 5 ordered photo URLs
    video_url: Optional[str] = None    # YouTube URL only

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
    website_hp: Optional[str] = None  # Honeypot field for bot detection

class AIQuestionRequest(BaseModel):
    question: str


# ----------------- Blog Models -----------------
try:
    from api.seed_blogs import SEED_BLOGS
except Exception:
    try:
        from seed_blogs import SEED_BLOGS
    except Exception:
        SEED_BLOGS = []

_mem_blogs = list(SEED_BLOGS)

class BlogContentItem(BaseModel):
    type: str = "section"  # "section" or "table"
    id: Optional[str] = None
    heading: str = ""
    text: Optional[str] = ""
    items: Optional[List[str]] = []
    headers: Optional[List[str]] = []
    rows: Optional[List[List[str]]] = []

class BlogTOCItem(BaseModel):
    id: str
    title: str

class BlogArticleCreate(BaseModel):
    slug: Optional[str] = None
    title: str
    summary: str
    category: Optional[str] = "Engineering & Machinery"
    categorySlug: Optional[str] = "engineering-machinery"
    date: Optional[str] = None
    readTime: Optional[str] = "6 min read"
    author: Optional[str] = "Gagan Engineering Works Technical Desk"
    image: Optional[str] = ""
    tags: Optional[List[str]] = []
    targetKeywords: Optional[str] = ""
    relatedProducts: Optional[List[str]] = []
    tableOfContents: Optional[List[BlogTOCItem]] = []
    content: Optional[List[BlogContentItem]] = []
    published: Optional[bool] = True

class BlogArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    categorySlug: Optional[str] = None
    date: Optional[str] = None
    readTime: Optional[str] = None
    author: Optional[str] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = None
    targetKeywords: Optional[str] = None
    relatedProducts: Optional[List[str]] = None
    tableOfContents: Optional[List[BlogTOCItem]] = None
    content: Optional[List[BlogContentItem]] = None
    published: Optional[bool] = None


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

    valid_users = [
        "admin",
        os.environ.get("ADMIN_USERNAME", "admin").strip()
    ]
    valid_passwords = [
        "Enrique7",
        "gaganworks2006",
        os.environ.get("ADMIN_PASSWORD", "Enrique7").strip(),
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
    """Merge seed products with authoritative DB records and deletion markers."""
    products = {p["id"]: p for p in _mem_products}
    if db is not None:
        try:
            docs = await db["products"].find({}, {"_id": 0}).to_list(length=None)
            products.update({p["id"]: p for p in docs})
        except Exception as e:
            logger.warning(f"Error fetching products from DB: {e}")
            raise HTTPException(status_code=503, detail="Product storage is unavailable. Please try again later.") from e
    return [p for p in products.values() if not p.get("deleted")]

async def get_product_by_id(product_id: str) -> Optional[Dict]:
    """Use a seed only when the product is genuinely absent from the DB."""
    product = None
    if db is not None:
        try:
            product = await db["products"].find_one({"id": product_id}, {"_id": 0})
        except Exception as e:
            logger.warning(f"Error fetching product {product_id} from DB: {e}")
            raise HTTPException(status_code=503, detail="Product storage is unavailable. Please try again later.") from e
    if product is None:
        product = next((p for p in _mem_products if p["id"] == product_id), None)
    return product if product and not product.get("deleted") else None

async def get_blogs_from_db(published_only: bool = True) -> List[Dict]:
    """Merge seeds with authoritative DB publishing state before filtering."""
    articles = {b["slug"]: b for b in _mem_blogs}
    if db is not None:
        try:
            # Drafts and deletion tombstones must also override their seed versions.
            docs = await db["blogs"].find({}, {"_id": 0}).to_list(length=None)
            articles.update({b["slug"]: b for b in docs})
        except Exception as e:
            logger.warning(f"Error fetching blogs from DB: {e}")
            raise HTTPException(status_code=503, detail="Blog storage is unavailable. Please try again later.") from e
    visible = [b for b in articles.values() if not b.get("deleted") and (not published_only or b.get("published", True))]
    return sorted(visible, key=lambda b: str(b.get("date", "")), reverse=True)

async def get_blog_by_slug(slug: str, published_only: bool = False) -> Optional[Dict]:
    """Fetch a DB article, falling back only when the slug is genuinely absent."""
    doc = None
    if db is not None:
        try:
            doc = await db["blogs"].find_one({"slug": slug}, {"_id": 0})
        except Exception as e:
            logger.warning(f"Error fetching blog {slug} from DB: {e}")
            raise HTTPException(status_code=503, detail="Blog storage is unavailable. Please try again later.") from e
    if doc is None:
        doc = next((b for b in _mem_blogs if b.get("slug") == slug), None)
    if doc is None or doc.get("deleted") or (published_only and not doc.get("published", True)):
        return None
    return doc


# ----------------- Startup Seeder -----------------
@app.on_event("startup")
async def seed_database():
    """Seed database with default products and blogs if collections are empty or missing records."""
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
            for p in SEED_PRODUCTS:
                if await db["products"].count_documents({"id": p["id"]}) == 0:
                    await db["products"].insert_one({**p})
                    logger.info(f"Auto-seeded missing product: {p['id']}")
        
        for b in SEED_BLOGS:
            # Insert missing seeds without replacing edits, drafts or deletion tombstones.
            await db["blogs"].update_one({"slug": b["slug"]}, {"$setOnInsert": dict(b)}, upsert=True)
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
        email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
        if not isinstance(email_id, str) or not email_id.strip():
            raise ValueError("Email provider did not return a confirmation ID.")
        email_id = email_id.strip()
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
            email_id = data.get("id") if isinstance(data, dict) else None
            if not isinstance(email_id, str) or not email_id.strip():
                raise ValueError("Email provider did not return a confirmation ID.")
            email_id = email_id.strip()
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

_rate_limit_map: Dict[str, List[float]] = {}

@api_router.post("/contact")
async def submit_contact(payload: ContactLeadCreate, request: Request):
    # 1. Honeypot check: Bots fill hidden fields automatically
    if payload.website_hp:
        logger.info("Bot lead submission trapped by honeypot.")
        return {
            "status": "success",
            "message": "Thank you! Your quotation request has been received. Our chief engineer will contact you within 24 hours.",
            "lead_id": str(uuid.uuid4()),
            "email_sent": True,
            "email_id": "hp_trap",
            "email_error": None,
        }

    # 2. Rate limiting check: Max 5 requests per 10 minutes per IP
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    if client_ip != "unknown":
        timestamps = [t for t in _rate_limit_map.get(client_ip, []) if now - t < 600]
        if len(timestamps) >= 5:
            raise HTTPException(
                status_code=429,
                detail="Too many quotation requests from your network. Please wait a few minutes or contact us directly via WhatsApp."
            )
        timestamps.append(now)
        _rate_limit_map[client_ip] = timestamps

    clean_payload = payload.model_dump(exclude={"website_hp"})
    lead = ContactLead(**clean_payload)
    lead_dict = lead.model_dump()
    lead_dict["created_at"] = lead.created_at.isoformat()

    lead_saved = False
    if db is not None:
        try:
            result = await db["contact_leads"].insert_one(lead.model_dump())
            lead_saved = result.acknowledged
        except Exception as e:
            logger.warning(f"Failed to save lead to MongoDB: {e}")

    try:
        email_id, err_detail = await send_lead_email_with_diagnostics(lead)
    except Exception as e:
        logger.warning(f"Failed to send lead email: {e}")
        email_id, err_detail = None, "Email delivery is temporarily unavailable."

    if not lead_saved and not email_id:
        raise HTTPException(
            status_code=503,
            detail="We couldn't receive your quotation request. Please retry in a few minutes or contact us directly via phone or WhatsApp."
        )

    _mem_leads.insert(0, lead_dict)

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

@api_router.get("/blogs")
async def list_public_blogs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100)
):
    blogs = await get_blogs_from_db(published_only=True)
    if category and category != "all":
        blogs = [b for b in blogs if b.get("categorySlug") == category or b.get("category", "").lower() == category.lower()]
    if tag:
        t = tag.lower()
        blogs = [b for b in blogs if any(t in str(x).lower() for x in b.get("tags", []))]
    if search:
        s = search.lower()
        blogs = [
            b for b in blogs
            if s in b.get("title", "").lower()
            or s in b.get("summary", "").lower()
            or any(s in str(x).lower() for x in b.get("tags", []))
        ]
    total = len(blogs)
    start = (page - 1) * limit
    paginated = blogs[start:start + limit]
    return {"articles": paginated, "total": total, "page": page, "limit": limit}

@api_router.get("/blogs/{slug}")
async def get_public_blog(slug: str):
    blog = await get_blog_by_slug(slug, published_only=True)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog article not located")
    return {"article": blog}


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

def _validate_youtube_url(url: Optional[str]) -> Optional[str]:
    """Returns clean URL if valid YouTube, raises HTTPException otherwise."""
    import re
    if not url:
        return None
    url = url.strip()
    if not re.search(r'(youtube\.com/(watch|shorts)|youtu\.be/)', url):
        raise HTTPException(status_code=422, detail="video_url must be a valid YouTube URL (youtube.com/watch?v=..., youtu.be/..., or youtube.com/shorts/...).")
    return url

@admin_router.post("/products", status_code=201)
async def admin_create_product(payload: ProductCreate, username: str = Depends(verify_admin)):
    if db is None:
        raise HTTPException(status_code=503, detail="Product storage is unavailable. Nothing was saved.")
    product_id = payload.id or payload.name.lower().replace(" ", "-").replace("/", "-").replace("&", "and")
    import re
    product_id = re.sub(r'[^a-z0-9-]', '', re.sub(r'\s+', '-', product_id.lower()))

    # Check uniqueness
    existing = await get_product_by_id(product_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Product with id '{product_id}' already exists")

    # Validate media fields
    images = payload.images or []
    if len(images) > 5:
        raise HTTPException(status_code=422, detail="Maximum 5 photos allowed per product.")
    video_url = _validate_youtube_url(payload.video_url)

    new_product = {
        **payload.model_dump(),
        "id": product_id,
        "images": images,
        "video_url": video_url,
        "faqs": [f.model_dump() for f in (payload.faqs or [])],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }

    try:
        # Reuse a deletion marker when restoring a product ID.
        await db["products"].replace_one({"id": product_id}, dict(new_product), upsert=True)
    except Exception as e:
        logger.warning(f"Failed to save product to MongoDB: {e}")
        raise HTTPException(status_code=503, detail="The product save could not be confirmed. Refresh before retrying.") from e

    return {"status": "created", "product": new_product}

@admin_router.put("/products/{product_id}")
async def admin_update_product(product_id: str, payload: ProductUpdate, username: str = Depends(verify_admin)):
    if db is None:
        raise HTTPException(status_code=503, detail="Product storage is unavailable. Nothing was saved.")
    existing = await get_product_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if "faqs" in update_data:
        update_data["faqs"] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in update_data["faqs"]]

    # Validate media fields if provided
    if "images" in update_data:
        if len(update_data["images"]) > 5:
            raise HTTPException(status_code=422, detail="Maximum 5 photos allowed per product.")
    if "video_url" in update_data:
        update_data["video_url"] = _validate_youtube_url(update_data["video_url"])

    update_data["updatedAt"] = datetime.now(timezone.utc)

    updated = {**existing, **update_data}
    try:
        await db["products"].update_one({"id": product_id}, {"$set": updated}, upsert=True)
    except Exception as e:
        logger.warning(f"MongoDB product update failed: {e}")
        raise HTTPException(status_code=503, detail="The product save could not be confirmed. Refresh before retrying.") from e
    return {"status": "updated", "product": updated}

@admin_router.delete("/products/{product_id}")
async def admin_delete_product(product_id: str, username: str = Depends(verify_admin)):
    if db is None:
        raise HTTPException(status_code=503, detail="Product storage is unavailable. Nothing was deleted.")
    existing = await get_product_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        await db["products"].update_one({"id": product_id}, {"$set": {
            "deleted": True, "updatedAt": datetime.now(timezone.utc)
        }}, upsert=True)
    except Exception as e:
        logger.warning(f"MongoDB product delete failed: {e}")
        raise HTTPException(status_code=503, detail="The product deletion could not be confirmed. Refresh before retrying.") from e

    return {"status": "deleted", "id": product_id}

@admin_router.post("/products/import")
async def admin_import_products(products: List[ProductCreate], username: str = Depends(verify_admin)):
    """Bulk import products from JSON array. Skips duplicates by ID."""
    if db is None:
        raise HTTPException(status_code=503, detail="Product storage is unavailable. Nothing was saved.")
    import re
    created = []
    skipped = []

    for payload in products:
        product_id = payload.id or payload.name.lower()
        product_id = re.sub(r'[^a-z0-9-]', '', re.sub(r'\s+', '-', product_id.lower()))

        try:
            await admin_create_product(payload.model_copy(update={"id": product_id}), username=username)
        except HTTPException as e:
            if e.status_code == 409:
                skipped.append(product_id)
                continue
            if created:
                raise HTTPException(status_code=e.status_code, detail={
                    "message": "Import stopped. Earlier products were saved; review these IDs before retrying.",
                    "error": e.detail, "created_ids": created, "skipped_ids": skipped
                }) from e
            raise

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
        unique_name = f"upload_{uuid.uuid4().hex[:12]}{clean_ext}"
        dest_path = UPLOAD_DIR / unique_name
        contents = await file.read()
        with open(dest_path, "wb") as f:
            f.write(contents)
        return {"url": f"/images/uploads/{unique_name}", "filename": unique_name}
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

# ----------------- Admin Blog Endpoints -----------------
@admin_router.get("/blogs")
async def admin_list_blogs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    published: Optional[bool] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, le=200),
    username: str = Depends(verify_admin)
):
    blogs = await get_blogs_from_db(published_only=False)
    if category and category != "all":
        blogs = [b for b in blogs if b.get("categorySlug") == category or b.get("category", "").lower() == category.lower()]
    if published is not None:
        blogs = [b for b in blogs if b.get("published", True) == published]
    if search:
        s = search.lower()
        blogs = [
            b for b in blogs
            if s in b.get("title", "").lower()
            or s in b.get("summary", "").lower()
            or s in b.get("slug", "").lower()
            or any(s in str(t).lower() for t in b.get("tags", []))
        ]
    total = len(blogs)
    start = (page - 1) * limit
    paginated = blogs[start:start + limit]
    return {"articles": paginated, "total": total, "page": page, "limit": limit}

@admin_router.get("/blogs/{slug}")
async def admin_get_blog(slug: str, username: str = Depends(verify_admin)):
    blog = await get_blog_by_slug(slug, published_only=False)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog article not found")
    return {"article": blog}

@admin_router.post("/blogs", status_code=201)
async def admin_create_blog(payload: BlogArticleCreate, username: str = Depends(verify_admin)):
    if db is None:
        raise HTTPException(status_code=503, detail="Blog storage is unavailable. Nothing was saved.")
    import re
    slug = payload.slug or payload.title.lower()
    slug = re.sub(r'[^a-z0-9-]', '', re.sub(r'[\s_]+', '-', slug.lower())).strip('-')
    if not slug:
        slug = f"post-{int(datetime.now(timezone.utc).timestamp())}"

    existing = await get_blog_by_slug(slug, published_only=False)
    if existing:
        raise HTTPException(status_code=409, detail=f"Blog article with slug '{slug}' already exists")

    now = datetime.now(timezone.utc)
    new_article = {
        **payload.model_dump(),
        "slug": slug,
        "date": payload.date or now.strftime("%Y-%m-%d"),
        "createdAt": now,
        "updatedAt": now,
    }

    try:
        # Reuse a deleted slug's tombstone rather than inserting a duplicate document.
        await db["blogs"].replace_one({"slug": slug}, dict(new_article), upsert=True)
    except Exception as e:
        logger.warning(f"Failed to save blog to MongoDB: {e}")
        raise HTTPException(status_code=503, detail="The blog save could not be confirmed. Refresh before retrying.") from e

    return {"status": "created", "article": new_article}

@admin_router.put("/blogs/{slug}")
async def admin_update_blog(slug: str, payload: BlogArticleUpdate, username: str = Depends(verify_admin)):
    if db is None:
        raise HTTPException(status_code=503, detail="Blog storage is unavailable. Nothing was saved.")
    existing = await get_blog_by_slug(slug, published_only=False)
    if not existing:
        raise HTTPException(status_code=404, detail="Blog article not found")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updatedAt"] = datetime.now(timezone.utc)

    updated = {**existing, **update_data}
    try:
        # A fallback seed may not exist in MongoDB yet; persist the complete article.
        await db["blogs"].update_one({"slug": slug}, {"$set": updated}, upsert=True)
    except Exception as e:
        logger.warning(f"MongoDB blog update failed: {e}")
        raise HTTPException(status_code=503, detail="The blog save could not be confirmed. Refresh before retrying.") from e
    return {"status": "updated", "article": updated}

@admin_router.delete("/blogs/{slug}")
async def admin_delete_blog(slug: str, username: str = Depends(verify_admin)):
    if db is None:
        raise HTTPException(status_code=503, detail="Blog storage is unavailable. Nothing was deleted.")
    existing = await get_blog_by_slug(slug, published_only=False)
    if not existing:
        raise HTTPException(status_code=404, detail="Blog article not found")

    try:
        # Retain a durable marker so fallback merging and startup cannot restore it.
        await db["blogs"].update_one({"slug": slug}, {"$set": {
            "published": False, "deleted": True, "updatedAt": datetime.now(timezone.utc)
        }}, upsert=True)
    except Exception as e:
        logger.warning(f"MongoDB delete blog failed: {e}")
        raise HTTPException(status_code=503, detail="The blog deletion could not be confirmed. Refresh before retrying.") from e

    return {"status": "deleted", "slug": slug}

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
        "db_connected": db is not None,
        "sender_email": sender_mail,
        "business_email": biz_mail,
    }

@admin_router.get("/db-health")
async def admin_db_health(username: str = Depends(verify_admin)):
    """Live diagnostic check for MongoDB Atlas cloud connectivity and latency."""
    if db is None:
        return {
            "status": "in_memory",
            "connected": False,
            "message": "MONGO_URL is not set or unreachable. Running in ephemeral in-memory mode."
        }
    try:
        t0 = time.time()
        await client.admin.command('ping')
        latency_ms = round((time.time() - t0) * 1000, 2)
        prod_count = await db["products"].count_documents({})
        lead_count = await db["contact_leads"].count_documents({})
        return {
            "status": "healthy",
            "connected": True,
            "latency_ms": latency_ms,
            "products_in_db": prod_count,
            "leads_in_db": lead_count,
            "database_name": db.name,
            "message": "MongoDB Atlas connection is live, verified, and operational."
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e),
            "message": "MongoDB ping failed."
        }



# ----------------- SEO Endpoints -----------------
_raw_site_url = os.environ.get("WEBSITE_URL") or os.environ.get("VERCEL_PROJECT_PRODUCTION_URL") or "https://www.gaganengineerings.in"
WEBSITE_URL = _raw_site_url if _raw_site_url.startswith("http") else f"https://{_raw_site_url}"

PRODUCT_SKUS = {
    "10-tons-hydraulic-decoiler": "GSK-DEC-10T",
    "automatic-ctl-machine": "GSK-CTL-01",
    "c-z-purlin-roll-forming-machine": "GSK-PUR-CZ",
    "automatic-roofing-sheet-crimping-machine": "GSK-ROOF-CRM",
    "corrugated-sheets-making-machine": "GSK-CORR-01",
    "tata-nali-sheet-making-machine": "GSK-NALI-01",
    "peb-roofing-sheet-making-machine": "GSK-PEB-01",
    "semi-automatic-pipe-counter-boring-and-facing-machine": "GSK-PCB-60M",
    "double-head-electric-bra-cup-moulding-machine": "GSK-BRA-DH",
    "bra-cup-fabric-moulding-machine": "GSK-BRA-FAB",
    "foam-bra-cup-moulding-machine": "GSK-BRA-FOAM",
    "padded-bra-cup-moulding-machine": "GSK-BRA-PAD",
}

def get_product_sku(p_id: str) -> str:
    if not p_id:
        return "GSK-MACH-01"
    if p_id in PRODUCT_SKUS:
        return PRODUCT_SKUS[p_id]
    import re
    clean = re.sub(r'[^a-zA-Z0-9]', '', p_id).upper()
    return f"GSK-{clean[:16]}"

def _content_lastmod(record):
    """Use recorded content dates; never claim a request changed the page."""
    for key in ("updatedAt", "updated_at", "dateModified", "date", "createdAt"):
        value = record.get(key)
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
            except ValueError:
                continue
    return None


@app.get("/sitemap.xml", response_class=Response)
async def sitemap():
    import xml.etree.ElementTree as ET
    from urllib.parse import quote
    products = await get_products_from_db()
    blogs = await get_blogs_from_db(published_only=True)
    sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    image_ns = "http://www.google.com/schemas/sitemap-image/1.1"
    ET.register_namespace("", sitemap_ns)
    ET.register_namespace("image", image_ns)
    root = ET.Element(f"{{{sitemap_ns}}}urlset")

    def add_url(path, record=None):
        node = ET.SubElement(root, f"{{{sitemap_ns}}}url")
        ET.SubElement(node, f"{{{sitemap_ns}}}loc").text = f"{WEBSITE_URL.rstrip('/')}/{path}"
        lastmod = _content_lastmod(record or {})
        if lastmod:
            ET.SubElement(node, f"{{{sitemap_ns}}}lastmod").text = lastmod
        return node

    for path in PAGE_META:
        add_url(path)
    for slug in CATEGORY_SEO:
        add_url(f"products/category/{slug}")
    for blog in blogs:
        if blog.get("slug"):
            add_url(f"blog/{quote(str(blog['slug']), safe='')}", blog)
    for product in products:
        if not product.get("id"):
            continue
        node = add_url(f"products/{quote(str(product['id']), safe='')}", product)
        if product.get("image"):
            image = ET.SubElement(node, f"{{{image_ns}}}image")
            ET.SubElement(image, f"{{{image_ns}}}loc").text = _absolute_image_url(product["image"])
            ET.SubElement(image, f"{{{image_ns}}}title").text = str(product.get("name", ""))
    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return Response(content=xml, media_type="application/xml", headers={"Cache-Control": "public, max-age=3600"})


@app.get("/google-merchant-feed.xml", response_class=Response)
@app.get("/google-shopping-feed.xml", response_class=Response)
async def google_merchant_feed():
    # These machines are sold by quotation, with no public purchasable offers.
    # Keep the feed valid but empty until verified price/availability data exists.
    import xml.etree.ElementTree as ET
    root = ET.Element("rss", {"version": "2.0", "xmlns:g": "http://base.google.com/ns/1.0"})
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "Gagan Engineering Works - Machinery Catalogue Feed"
    ET.SubElement(channel, "link").text = WEBSITE_URL
    ET.SubElement(channel, "description").text = "Quotation-based industrial machinery; no public shopping offers."
    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return Response(content=xml, media_type="application/xml", headers={"Cache-Control": "public, max-age=3600"})

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


# ----------------- SEO Prerender for Crawlers -----------------
# Static page SEO metadata
PAGE_META = {
    "": {
        "title": "Gagan Engineering Works | Corrugated Sheet Making Machines & Industrial Machinery Manufacturer | Khopoli India",
        "description": "Premier Indian manufacturer of Corrugated Sheets Making Machines, Bra Cup Moulding Machines, 10-Ton Hydraulic Decoilers, C/Z Purlin Roll Forming Machines, and Automatic Cut-To-Length Lines from Khopoli, Maharashtra.",
        "keywords": "Corrugated Sheet Making Machine, Corrugated Sheet Making Machine Manufacturer India, Bra Cup Moulding Machine, Hydraulic Decoiler, Roll Forming Machine, Cut To Length Line, Khopoli Maharashtra"
    },
    "products": {
        "title": "Industrial Machinery Catalogue | Corrugated Sheet Machines, Roll Forming & CTL Lines | Gagan Engineering",
        "description": "Browse heavy-duty industrial machinery: Corrugated Sheet Making Machines, 10-Ton Hydraulic Decoilers, Automatic Cut-To-Length Lines, C/Z Purlin Roll Forming Machines, and Bra Cup Moulding Presses from Khopoli.",
        "keywords": "Corrugated Sheet Making Machine India, Industrial Machinery Catalogue, Roll Forming Machine, CTL Line, Bra Cup Moulding Machine, Hydraulic Decoiler, Gagan Engineering"
    },
    "about": {
        "title": "About Gagan Engineering Works | 19+ Years Machinery Manufacturing | Khopoli Maharashtra",
        "description": "Established in 2006, Gagan Engineering Works is a precision industrial machinery manufacturer in Khopoli, Maharashtra with 19+ years of engineering excellence, ISO certified, serving Pan-India and global markets.",
        "keywords": "Gagan Engineering Works, Industrial Machinery Manufacturer Khopoli, About Us, ISO Certified Machinery"
    },
    "factory": {
        "title": "Factory Tour | Gagan Engineering Works Manufacturing Facility | Khopoli Maharashtra",
        "description": "Tour our state-of-the-art machinery manufacturing facility in Khopoli, Maharashtra. See our heavy fabrication bays, CNC machining centers, and quality inspection areas.",
        "keywords": "Factory Tour, Manufacturing Facility Khopoli, Machinery Workshop, Heavy Engineering India"
    },
    "contact": {
        "title": "Contact Gagan Engineering Works | Request Quotation | +91 83294 65245",
        "description": "Request a price quotation for industrial machinery. Contact us at +91 83294 65245 or email gaganengineerings@gmail.com. Located on Mumbai-Pune Highway, Khopoli, Maharashtra.",
        "keywords": "Contact Gagan Engineering, Machinery Quotation, RFQ Industrial Machinery, Khopoli Maharashtra"
    },
    "blog": {
        "title": "Engineering Knowledge Hub | Technical Guides & Machinery Articles | Gagan Engineering",
        "description": "Expert technical articles on bra cup moulding machines, cut-to-length lines, C/Z purlin roll forming, hydraulic decoilers, and industrial machinery export from India.",
        "keywords": "Machinery Blog, Engineering Guides, Industrial Machinery Articles, Manufacturing Technology India"
    },
    "return-policy": {
        "title": "Warranty & Return Policy | Gagan Engineering Works",
        "description": "Warranty terms, return policy, and after-sales support information for machinery purchased from Gagan Engineering Works.",
        "keywords": "Warranty Policy, Return Policy, Machinery Warranty, After Sales Support"
    },
    "privacy-policy": {
        "title": "Privacy Policy | Gagan Engineering Works",
        "description": "Privacy policy for Gagan Engineering Works website and services.",
        "keywords": "Privacy Policy, Data Protection"
    },
    "terms": {
        "title": "Terms & Conditions | Gagan Engineering Works",
        "description": "Terms and conditions for machinery purchase, delivery, and services from Gagan Engineering Works.",
        "keywords": "Terms and Conditions, Machinery Purchase Terms"
    }
}

CATEGORY_SEO = {
    "roll-forming-sheet-metal": {
        "name": "Roll Forming & Sheet Metal",
        "title": "Roll Forming & Sheet Metal Machinery Manufacturer",
        "description": "Heavy-duty C/Z purlin roll formers, 10-ton hydraulic decoilers, and automatic roofing sheet crimping machines for industrial fabrication.",
        "keywords": "Roll Forming Machine India, C Z Purlin Machine, 10 Ton Hydraulic Decoiler, Roofing Sheet Crimping Machine, Sheet Metal Machinery",
        "matches": ("Roll", "Decoiler", "Roofing"),
    },
    "cut-to-length-line": {
        "name": "Cut To Length Line",
        "title": "Automatic Cut To Length (CTL) Lines Manufacturer",
        "description": "Precision automated cut-to-length lines with hydraulic decoiling, 9-roll EN31 leveling, and optical encoder PLC shearing for coils up to 6mm.",
        "keywords": "Cut to Length Line Manufacturer, Automatic CTL Machine, Coil Processing Line, Heavy Sheet Leveler Khopoli Maharashtra",
        "matches": ("Cut", "CTL"),
    },
    "bra-cup-moulding-machine": {
        "name": "Bra Cup Moulding Machine",
        "title": "Bra Cup Moulding Machines Manufacturer & Exporter",
        "description": "High-precision electric, foam, fabric, and padded bra cup moulding presses for intimate wear lingerie manufacturing in India and export.",
        "keywords": "Bra Cup Moulding Machine Manufacturer, Bra Cup Fabric Moulding, Foam Bra Cup Machine, Intimate Wear Machinery, Lingerie Moulding Press India",
        "matches": ("Bra Cup",),
    },
    "bending-machines": {
        "name": "Bending Machines",
        "title": "Industrial Bending Machines Manufacturer India",
        "description": "Heavy-duty hydraulic and mechanical bending machines for precision metal bending, pipe bending, and plate bending operations in industrial fabrication.",
        "keywords": "Bending Machine Manufacturer India, Hydraulic Bending Machine, Pipe Bending Machine, Metal Bending Machine, Plate Bending Machine Khopoli",
        "matches": ("Bending",),
    },
    "facing-machines": {
        "name": "Facing Machines",
        "title": "Facing Machines Manufacturer & Supplier India",
        "description": "Precision pipe facing, counter boring, and end-finishing machines for accurate surface preparation in pipeline, boiler, and heavy engineering industries.",
        "keywords": "Facing Machine Manufacturer India, Pipe Facing Machine, Counter Boring Machine, End Facing Machine, Pipe End Preparation Machine",
        "matches": ("Facing",),
    },
    "threading-machines": {
        "name": "Threading Machines",
        "title": "Industrial Threading Machines Manufacturer India",
        "description": "High-performance pipe threading, bolt threading, and rebar threading machines for precision thread cutting in oil & gas, construction, and manufacturing sectors.",
        "keywords": "Threading Machine Manufacturer India, Pipe Threading Machine, Bolt Threading Machine, Rebar Threading Machine, Thread Cutting Machine",
        "matches": ("Threading",),
    },
    "recoiling-decoiling-machines": {
        "name": "Re-coiling & De-coiling Machines",
        "title": "Re-coiling & De-coiling Machines Manufacturer India",
        "description": "Heavy-duty motorized re-coiling and de-coiling machines for steel coil handling, tension-controlled unwinding, and rewinding in metal processing lines.",
        "keywords": "Recoiling Machine Manufacturer India, Decoiling Machine, Coil Rewinding Machine, Steel Coil Handling Machine, Motorized Decoiler",
        "matches": ("Recoil", "Decoil", "Re-coil", "De-coil"),
    },
}


def _products_for_category(products, slug):
    meta = CATEGORY_SEO[slug]
    return [p for p in products if p.get("categorySlug") == slug or any(
        word in (p.get("category") or "") for word in meta["matches"]
    )]


def _html_escape(text):
    from html import escape
    return escape(str(text), quote=True) if text is not None else ""


def _schema_json(value):
    import json
    # JSON-LD data may contain user-authored text, including closing script tags.
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def _absolute_image_url(image):
    from urllib.parse import urljoin
    return urljoin(f"{WEBSITE_URL.rstrip('/')}/", image or "logo.png")


def _build_org_schema():
    """Build the Organization JSON-LD schema."""
    return _schema_json({
        "@context": "https://schema.org",
        "@type": ["Organization", "LocalBusiness"],
        "@id": f"{WEBSITE_URL}/#organization",
        "name": "Gagan Engineering Works",
        "legalName": "Gagan Engineering Works",
        "url": WEBSITE_URL,
        "logo": f"{WEBSITE_URL}/logo.png",
        "description": "Premier Indian manufacturer & exporter of Bra Cup Moulding Machines, Roll Forming Lines, Hydraulic Decoilers, and Cut-To-Length Lines from Khopoli, Maharashtra.",
        "telephone": "+918329465245",
        "email": "gaganengineerings@gmail.com",
        "foundingDate": "2006",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Mumbai Pune Highway, Near Star Garage, Navanath Colony, Yashwant Nagar",
            "addressLocality": "Khopoli",
            "addressRegion": "Maharashtra",
            "postalCode": "410203",
            "addressCountry": "IN"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "18.7903",
            "longitude": "73.3444"
        },
        "areaServed": [
            {"@type": "Country", "name": "India"},
            {"@type": "Country", "name": "United Arab Emirates"},
            {"@type": "Country", "name": "Saudi Arabia"},
            {"@type": "Country", "name": "Bangladesh"},
            {"@type": "Country", "name": "Sri Lanka"}
        ],
        "priceRange": "₹₹₹",
        "sameAs": ["https://www.indiamart.com/gaganengineeringworks/"]
    })


def _build_product_schema(product, canonical_url):
    """Describe catalogue products without inventing offers or review evidence."""
    schemas = []
    
    p_id = product.get("id", "")
    p_name = product.get("name", "")
    p_desc = product.get("description") or product.get("tagline", "")
    p_sku = get_product_sku(p_id)
    p_img = _absolute_image_url(product.get("image"))
    
    prod_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p_name,
        "image": [p_img],
        "description": p_desc,
        "sku": p_sku,
        "mpn": p_sku,
        "category": product.get("category", "Industrial Machinery"),
        "brand": {"@type": "Brand", "name": "Gagan Engineering Works"},
        "manufacturer": {"@type": "Organization", "name": "Gagan Engineering Works", "url": WEBSITE_URL},
    }
    if product.get("alternateName"):
        prod_schema["alternateName"] = product["alternateName"]
    if product.get("keywords"):
        prod_schema["keywords"] = product["keywords"]
    
    schemas.append(prod_schema)
    # FAQ schema
    faqs = product.get("faqs", [])
    if faqs:
        schemas.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]
        })
    
    # Breadcrumb schema
    schemas.append({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": WEBSITE_URL},
            {"@type": "ListItem", "position": 2, "name": "Machinery Catalogue", "item": f"{WEBSITE_URL}/products"},
            {"@type": "ListItem", "position": 3, "name": p_name, "item": canonical_url}
        ]
    })
    
    return _schema_json(schemas)


def _generate_nav_html():
    """Generate consistent navigation for all prerendered pages."""
    return f"""<header>
    <nav aria-label="Main navigation" style="padding:15px 20px;border-bottom:1px solid #ddd">
        <a href="/" style="font-weight:bold;font-size:18px;color:#333;text-decoration:none">Gagan Engineering Works</a>
        <span style="margin:0 10px">|</span>
        <a href="/products" style="color:#333;text-decoration:none">Machinery Catalogue</a>
        <span style="margin:0 5px">·</span>
        <a href="/about" style="color:#333;text-decoration:none">About</a>
        <span style="margin:0 5px">·</span>
        <a href="/factory" style="color:#333;text-decoration:none">Factory Tour</a>
        <span style="margin:0 5px">·</span>
        <a href="/blog" style="color:#333;text-decoration:none">Engineering Blog</a>
        <span style="margin:0 5px">·</span>
        <a href="/contact" style="color:#333;text-decoration:none">Contact / RFQ</a>
    </nav>
</header>"""


def _generate_footer_html(products, blogs):
    """Generate footer with internal links for crawlability."""
    from urllib.parse import quote
    product_links = "\n".join(
        f'        <li><a href="/products/{_html_escape(quote(str(p.get("id", "")), safe=""))}">{_html_escape(p.get("name", ""))}</a></li>'
        for p in products
    )
    blog_links = "\n".join(
        f'        <li><a href="/blog/{_html_escape(quote(str(b["slug"]), safe=""))}">{_html_escape(b["title"])}</a></li>'
        for b in blogs
    )
    return f"""<footer style="border-top:1px solid #ddd;padding:30px 20px;margin-top:40px;font-size:14px;color:#666">
    <div style="max-width:960px;margin:0 auto">
        <h3>All Machinery by Gagan Engineering Works</h3>
        <ul>
{product_links}
        </ul>
        <h3>Engineering Knowledge Hub</h3>
        <ul>
{blog_links}
        </ul>
        <h3>Quick Links</h3>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/products">Full Machinery Catalogue</a></li>
            <li><a href="/about">About Our Khopoli Works</a></li>
            <li><a href="/factory">Factory Tour</a></li>
            <li><a href="/contact">Request Quotation (RFQ)</a></li>
            <li><a href="/return-policy">Warranty & Return Policy</a></li>
            <li><a href="/privacy-policy">Privacy Policy</a></li>
            <li><a href="/terms">Terms & Conditions</a></li>
        </ul>
        <h3>Contact Gagan Engineering Works</h3>
        <p><strong>Phone:</strong> <a href="tel:+918329465245">+91 83294 65245</a></p>
        <p><strong>Email:</strong> <a href="mailto:gaganengineerings@gmail.com">gaganengineerings@gmail.com</a></p>
        <p><strong>WhatsApp:</strong> <a href="https://wa.me/918329465245">Chat on WhatsApp</a></p>
        <p><strong>Address:</strong> Mumbai-Pune Highway, Near Star Garage, Navanath Colony, Khopoli, Maharashtra 410203, India</p>
        <p><strong>Hours:</strong> Monday – Saturday: 9:00 AM – 7:30 PM IST</p>
        <p style="margin-top:20px">© 2026 Gagan Engineering Works. All Rights Reserved. Manufactured in Khopoli, India.</p>
    </div>
</footer>"""


def _generate_product_html(product, all_products, blogs):
    """Generate full HTML for a product detail page."""
    from urllib.parse import quote
    p_id = product.get("id", "")
    p_name = _html_escape(product.get("name", ""))
    p_desc = _html_escape(product.get("description") or product.get("tagline", ""))
    p_img = _absolute_image_url(product.get("image"))
    p_category = _html_escape(product.get("category", ""))
    canonical_url = f"{WEBSITE_URL}/products/{quote(str(p_id), safe='')}"
    
    title = f"{product.get('name', '')} Manufacturer India | Gagan Engineering Works"
    description = f"Specifications & price for {product.get('name', '')}. {(product.get('description') or '')[:200]}. Manufactured by Gagan Engineering Works, Khopoli Maharashtra."
    keywords = f"{product.get('name', '')}, {product.get('category', '')}, Industrial Machinery Manufacturer India, Gagan Engineering Khopoli, {product.get('name', '')} price"
    
    # Specs table
    specs = product.get("specs", {})
    spec_rows = "\n".join(
        f"            <tr><td style='padding:8px 12px;border-bottom:1px solid #eee;font-weight:600;width:40%'>{_html_escape(k)}</td><td style='padding:8px 12px;border-bottom:1px solid #eee'>{_html_escape(v)}</td></tr>"
        for k, v in specs.items()
    )
    
    # FAQs
    faqs = product.get("faqs", [])
    faq_html = ""
    if faqs:
        faq_items = "\n".join(
            f"        <div style='margin-bottom:15px;padding:15px;border:1px solid #eee;border-radius:4px'>\n            <h3 style='font-size:16px;margin:0 0 8px'>{_html_escape(f['q'])}</h3>\n            <p style='margin:0;color:#555'>{_html_escape(f['a'])}</p>\n        </div>"
            for f in faqs
        )
        faq_html = f"""
        <section style="margin-top:40px">
            <h2>Frequently Asked Questions — {p_name}</h2>
{faq_items}
        </section>"""
    
    # Related products
    cat_slug = product.get("categorySlug", "")
    related = [p for p in all_products if p.get("categorySlug") == cat_slug and p.get("id") != p_id][:4]
    related_html = ""
    if related:
        related_items = "\n".join(
            f'            <li><a href="/products/{_html_escape(quote(str(r.get("id", "")), safe=""))}">{_html_escape(r.get("name", ""))}</a> — {_html_escape(r.get("tagline", ""))}</li>'
            for r in related
        )
        related_html = f"""
        <section style="margin-top:40px">
            <h2>Related Machinery</h2>
            <ul>
{related_items}
            </ul>
        </section>"""
    
    schemas = _build_product_schema(product, canonical_url)
    org_schema = _build_org_schema()
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_html_escape(title)}</title>
    <meta name="description" content="{_html_escape(description)}">
    <meta name="keywords" content="{_html_escape(keywords)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="author" content="Gagan Engineering Works">
    <meta name="geo.region" content="IN-MH">
    <meta name="geo.placename" content="Khopoli, Maharashtra, India">
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:title" content="{_html_escape(title)}">
    <meta property="og:description" content="{_html_escape(description)}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="{_html_escape(p_img)}">
    <meta property="og:type" content="product">
    <meta property="og:site_name" content="Gagan Engineering Works">
    <meta property="og:locale" content="en_IN">
    <meta property="product:brand" content="Gagan Engineering Works">
    <meta property="product:condition" content="new">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{_html_escape(title)}">
    <meta name="twitter:description" content="{_html_escape(description)}">
    <meta name="twitter:image" content="{_html_escape(p_img)}">
    <link rel="alternate" hreflang="x-default" href="{canonical_url}">
    <link rel="alternate" hreflang="en" href="{canonical_url}">
    <link rel="alternate" hreflang="en-IN" href="{canonical_url}">
    <link rel="icon" type="image/png" href="/logo.png">
    <meta name="google-site-verification" content="QEGoiaBEcRKf2zkIZu9kBOEnvWdghWxictCIfTUy8CM">
    <meta name="theme-color" content="#050505">
    <script type="application/ld+json">{schemas}</script>
    <script type="application/ld+json">{org_schema}</script>
</head>
<body style="font-family:Inter,system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;color:#333;line-height:1.6">
{_generate_nav_html()}
    <main>
        <nav aria-label="breadcrumb" style="font-size:13px;color:#888;margin:20px 0">
            <a href="/">Home</a> / <a href="/products">Machinery Catalogue</a> / <span style="color:#FF5722">{p_name}</span>
        </nav>
        
        <article>
            <h1 style="font-size:28px;line-height:1.2;margin-bottom:10px">{p_name}</h1>
            <p style="font-size:13px;color:#888;margin-bottom:20px">Category: {p_category} | Manufactured by Gagan Engineering Works, Khopoli, Maharashtra</p>
            
            <img src="{_html_escape(p_img)}" alt="{p_name} manufactured by Gagan Engineering Works Khopoli Maharashtra India" width="500" height="500" loading="lazy" style="max-width:100%;height:auto;border-radius:4px">
            
            <p style="margin-top:20px;font-size:16px">{p_desc}</p>
            
            <section style="margin-top:30px">
                <h2>Technical Specifications — {p_name}</h2>
                <table style="width:100%;border-collapse:collapse;border:1px solid #ddd;margin-top:10px">
                    <thead>
                        <tr style="background:#f5f5f5">
                            <th style="padding:10px 12px;text-align:left;border-bottom:2px solid #ddd">Specification</th>
                            <th style="padding:10px 12px;text-align:left;border-bottom:2px solid #ddd">Value</th>
                        </tr>
                    </thead>
                    <tbody>
{spec_rows}
                    </tbody>
                </table>
            </section>
            
            <section style="margin-top:30px;padding:20px;background:#f9f9f9;border-radius:4px">
                <h2>Request Price Quotation for {p_name}</h2>
                <p>Get direct manufacturer pricing, delivery timeline, and custom specifications from Gagan Engineering Works:</p>
                <ul>
                    <li><strong>Phone:</strong> <a href="tel:+918329465245">+91 83294 65245</a></li>
                    <li><strong>Email:</strong> <a href="mailto:gaganengineerings@gmail.com">gaganengineerings@gmail.com</a></li>
                    <li><strong>WhatsApp:</strong> <a href="https://wa.me/918329465245?text=Hi%20Gagan%20Engineering%2C%20I%20need%20a%20quote%20for%20{p_name.replace(' ', '%20')}">Chat on WhatsApp</a></li>
                    <li><strong>Online RFQ:</strong> <a href="/contact?product={p_name.replace(' ', '%20')}">Submit Quotation Request</a></li>
                </ul>
                <p><strong>Warranty:</strong> 1 Year Comprehensive Manufacturer Warranty with Pan-India On-Site Commissioning</p>
                <p><strong>Export:</strong> Worldwide shipping from JNPT Mumbai Port. Custom voltage (220V/380V/415V/480V, 50Hz/60Hz)</p>
            </section>
{faq_html}
{related_html}
        </article>
    </main>
{_generate_footer_html(all_products, blogs)}
</body>
</html>"""


def _render_blog_text(text):
    """Render the seed's small bold/link syntax while treating author text as data."""
    import re
    from urllib.parse import urlsplit
    text = str(text or "")
    parts = []
    offset = 0
    for match in re.finditer(r"\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)]+)\)", text):
        parts.append(_html_escape(text[offset:match.start()]))
        if match.group(1) is not None:
            parts.append(f"<strong>{_html_escape(match.group(1))}</strong>")
        else:
            label, url = match.group(2), match.group(3).strip()
            try:
                valid_url = (url.startswith("/") and not url.startswith("//")) or urlsplit(url).scheme in ("http", "https")
            except ValueError:
                valid_url = False
            if valid_url:
                parts.append(f'<a href="{_html_escape(url)}">{_html_escape(label)}</a>')
            else:
                parts.append(_html_escape(match.group(0)))
        offset = match.end()
    parts.append(_html_escape(text[offset:]))
    return "".join(parts).replace("\n", "<br>\n")


def _render_blog_content(blog):
    sections = []
    for section in blog.get("content") or []:
        if not isinstance(section, dict):
            continue
        heading = _html_escape(section.get("heading", ""))
        section_id = _html_escape(section.get("id", ""))
        content = [f'<section id="{section_id}">', f"<h2>{heading}</h2>" if heading else ""]
        if section.get("text"):
            content.append(f'<p>{_render_blog_text(section["text"])}</p>')
        if section.get("type") == "table":
            headers = "".join(f'<th scope="col">{_html_escape(cell)}</th>' for cell in (section.get("headers") or []))
            rows = "".join("<tr>" + "".join(f"<td>{_html_escape(cell)}</td>" for cell in row) + "</tr>" for row in (section.get("rows") or []))
            content.append(f'<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>')
        if section.get("items"):
            content.append("<ul>" + "".join(f"<li>{_render_blog_text(item)}</li>" for item in section["items"]) + "</ul>")
        content.append("</section>")
        sections.append("\n".join(content))
    # Admin-created articles can also carry explicit FAQs alongside their sections.
    faqs = blog.get("faqs") or []
    if faqs:
        sections.append('<section><h2>Frequently Asked Questions</h2>' + "".join(
            f'<h3>{_html_escape(faq.get("q", ""))}</h3><p>{_render_blog_text(faq.get("a", ""))}</p>'
            for faq in faqs if isinstance(faq, dict)
        ) + '</section>')
    return "\n".join(sections)


def _generate_blog_html(blog, all_products, blogs):
    """Render the same published article sections/tables used by the browser."""
    from urllib.parse import quote
    canonical_url = f"{WEBSITE_URL}/blog/{quote(str(blog['slug']), safe='')}"
    title = f"{blog['title']} | Gagan Engineering Works"
    description = blog.get("summary") or blog.get("description", "")
    keywords = blog.get("targetKeywords") or blog.get("tags") or ""
    if isinstance(keywords, (list, tuple)):
        keywords = ", ".join(keywords)
    image = _absolute_image_url(blog.get("image"))
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": blog["title"],
        "description": description,
        "image": image,
        "author": {"@type": "Organization", "name": blog.get("author") or "Gagan Engineering Works"},
        "publisher": {"@type": "Organization", "name": "Gagan Engineering Works", "logo": {"@type": "ImageObject", "url": f"{WEBSITE_URL}/logo.png"}},
        "mainEntityOfPage": canonical_url,
    }
    if blog.get("date"):
        article_schema["datePublished"] = blog["date"]
    modified = _content_lastmod({key: blog.get(key) for key in ("updatedAt", "updated_at", "dateModified")})
    if modified:
        article_schema["dateModified"] = modified
    schemas = [article_schema, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": WEBSITE_URL},
            {"@type": "ListItem", "position": 2, "name": "Engineering Blog", "item": f"{WEBSITE_URL}/blog"},
            {"@type": "ListItem", "position": 3, "name": blog["title"], "item": canonical_url},
        ],
    }]
    related = [product for product in all_products if product.get("id") in (blog.get("relatedProducts") or [])]
    related_html = ""
    if related:
        related_html = '<section><h2>Related Machinery</h2><ul>' + "".join(
            f'<li><a href="/products/{_html_escape(quote(str(product["id"]), safe=""))}">{_html_escape(product.get("name", ""))}</a></li>'
            for product in related
        ) + '</ul></section>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_html_escape(title)}</title>
    <meta name="description" content="{_html_escape(description)}">
    <meta name="keywords" content="{_html_escape(keywords)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="author" content="{_html_escape(blog.get('author') or 'Gagan Engineering Works')}">
    <link rel="canonical" href="{_html_escape(canonical_url)}">
    <meta property="og:title" content="{_html_escape(title)}">
    <meta property="og:description" content="{_html_escape(description)}">
    <meta property="og:url" content="{_html_escape(canonical_url)}">
    <meta property="og:image" content="{_html_escape(image)}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Gagan Engineering Works">
    <meta property="article:published_time" content="{_html_escape(blog.get('date', ''))}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{_html_escape(title)}">
    <meta name="twitter:description" content="{_html_escape(description)}">
    <meta name="twitter:image" content="{_html_escape(image)}">
    <link rel="alternate" hreflang="x-default" href="{_html_escape(canonical_url)}">
    <link rel="alternate" hreflang="en" href="{_html_escape(canonical_url)}">
    <link rel="icon" type="image/png" href="/logo.png">
    <meta name="google-site-verification" content="QEGoiaBEcRKf2zkIZu9kBOEnvWdghWxictCIfTUy8CM">
    <script type="application/ld+json">{_schema_json(schemas)}</script>
    <script type="application/ld+json">{_build_org_schema()}</script>
</head>
<body style="font-family:Inter,system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;color:#333;line-height:1.6">
{_generate_nav_html()}
    <main>
        <nav aria-label="breadcrumb">
            <a href="/">Home</a> / <a href="/blog">Engineering Blog</a> / <span>{_html_escape(blog['title'])}</span>
        </nav>
        <article>
            <h1>{_html_escape(blog['title'])}</h1>
            <p>Published: {_html_escape(blog.get('date', ''))} | By {_html_escape(blog.get('author') or 'Gagan Engineering Works')}</p>
            <img src="{_html_escape(image)}" alt="{_html_escape(blog['title'])}" width="600" loading="lazy" style="max-width:100%;height:auto">
            <p>{_html_escape(description)}</p>
{_render_blog_content(blog)}
{related_html}
        </article>
    </main>
{_generate_footer_html(all_products, blogs)}
</body>
</html>"""


def _generate_generic_page_html(path, all_products, blogs):
    """Generate HTML for static pages (home, about, contact, etc.)."""
    from urllib.parse import quote
    clean_path = path.strip("/")
    meta = PAGE_META.get(clean_path, {})
    canonical_url = f"{WEBSITE_URL}/{clean_path}" if clean_path else WEBSITE_URL
    title = meta.get("title", "Gagan Engineering Works | Machinery Manufacturer")
    description = meta.get("description", "")
    keywords = meta.get("keywords", "")
    
    # For category pages
    cat_slug = ""
    if clean_path.startswith("products/category/"):
        cat_slug = clean_path.replace("products/category/", "")
        cat_meta = CATEGORY_SEO.get(cat_slug, {})
        if cat_meta:
            title = cat_meta["title"]
            description = cat_meta["description"]
            keywords = cat_meta["keywords"]
    
    filtered = _products_for_category(all_products, cat_slug) if cat_slug else all_products

    # Keep visible category products and its ItemList identical.
    product_list_html = "\n".join(
        f'        <li><a href="/products/{_html_escape(quote(str(p.get("id", "")), safe=""))}">{_html_escape(p.get("name", ""))}</a> — {_html_escape(p.get("tagline", ""))}</li>'
        for p in filtered
    )
    listing_heading = "Our Industrial Machinery"
    if clean_path == "blog":
        listing_heading = "Engineering Articles"
        product_list_html = "\n".join(
            f'<li><a href="/blog/{_html_escape(quote(str(b.get("slug", "")), safe=""))}">{_html_escape(b.get("title", ""))}</a><p>{_html_escape(b.get("summary") or b.get("description", ""))}</p></li>'
            for b in blogs
        )
    
    breadcrumb_name = clean_path.replace("-", " ").replace("/", " > ").title() or "Home"
    schemas = [{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": WEBSITE_URL}
        ] + ([{"@type": "ListItem", "position": 2, "name": breadcrumb_name, "item": canonical_url}] if clean_path else [])
    }]
    
    # Add ItemList for product pages
    if clean_path in ("products", "") or clean_path.startswith("products/category/"):
        schemas.append({
            "@context": "https://schema.org",
            "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i+1, "url": f"{WEBSITE_URL}/products/{quote(str(p.get('id','')), safe='')}", "name": p.get("name","")}
                for i, p in enumerate(filtered)
            ]
        })
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_html_escape(title)}</title>
    <meta name="description" content="{_html_escape(description)}">
    <meta name="keywords" content="{_html_escape(keywords)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="author" content="Gagan Engineering Works">
    <meta name="geo.region" content="IN-MH">
    <meta name="geo.placename" content="Khopoli, Maharashtra, India">
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:title" content="{_html_escape(title)}">
    <meta property="og:description" content="{_html_escape(description)}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="{WEBSITE_URL}/logo.png">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Gagan Engineering Works">
    <meta property="og:locale" content="en_IN">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{_html_escape(title)}">
    <meta name="twitter:description" content="{_html_escape(description)}">
    <meta name="twitter:image" content="{WEBSITE_URL}/logo.png">
    <link rel="alternate" hreflang="x-default" href="{canonical_url}">
    <link rel="alternate" hreflang="en" href="{canonical_url}">
    <link rel="alternate" hreflang="en-IN" href="{canonical_url}">
    <link rel="icon" type="image/png" href="/logo.png">
    <meta name="google-site-verification" content="QEGoiaBEcRKf2zkIZu9kBOEnvWdghWxictCIfTUy8CM">
    <meta name="theme-color" content="#050505">
    <script type="application/ld+json">{_schema_json(schemas)}</script>
    <script type="application/ld+json">{_build_org_schema()}</script>
</head>
<body style="font-family:Inter,system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;color:#333;line-height:1.6">
{_generate_nav_html()}
    <main>
        <h1>{_html_escape(title.split('|')[0].strip())}</h1>
        <p>{_html_escape(description)}</p>
        
        <h2>{listing_heading}</h2>
        <ul>
{product_list_html}
        </ul>
    </main>
{_generate_footer_html(all_products, blogs)}
</body>
</html>"""


def _prerender_response(html, request, status_code=200):
    headers = {
        "Cache-Control": "public, max-age=3600" if status_code == 200 else "public, max-age=60",
        "X-Prerender": "1",
    }
    if status_code == 404:
        headers["X-Robots-Tag"] = "noindex, follow"
    response = Response(content=html, status_code=status_code, media_type="text/html", headers=headers)
    if request.method == "HEAD":
        response.body = b""
    return response


@app.api_route("/_seo/{path:path}", methods=["GET", "HEAD"], response_class=Response)
async def seo_prerender(path: str, request: Request):
    """Render published public routes; unknown URLs remain genuine missing pages."""
    products = await get_products_from_db()
    blogs = await get_blogs_from_db(published_only=True)
    clean_path = path.strip("/")
    html = None
    if clean_path.startswith("products/category/"):
        category = clean_path.removeprefix("products/category/")
        if category in CATEGORY_SEO:
            html = _generate_generic_page_html(clean_path, products, blogs)
    elif clean_path.startswith("products/"):
        product_id = clean_path.removeprefix("products/")
        product = next((p for p in products if p.get("id") == product_id), None)
        if product:
            html = _generate_product_html(product, products, blogs)
    elif clean_path.startswith("blog/"):
        slug = clean_path.removeprefix("blog/")
        blog = await get_blog_by_slug(slug, published_only=True)
        if blog:
            html = _generate_blog_html(blog, products, blogs)
    elif clean_path in PAGE_META:
        html = _generate_generic_page_html(clean_path, products, blogs)
    if html is None:
        html = f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Page Not Found | Gagan Engineering Works</title><meta name="robots" content="noindex, follow"></head><body>{_generate_nav_html()}<main><h1>Page Not Found</h1><p>The requested page could not be found.</p><a href="/products">Browse machinery</a></main></body></html>'
        return _prerender_response(html, request, status_code=404)
    return _prerender_response(html, request)


# Middleware to intercept __seo_path query parameter from Vercel rewrites
@app.middleware("http")
async def seo_path_middleware(request: Request, call_next):
    seo_path = request.query_params.get("__seo_path")
    if seo_path is not None and request.method in ("GET", "HEAD"):
        # Rewrite the request to the /_seo/ endpoint
        new_path = f"/_seo/{seo_path.lstrip('/')}"
        request.scope["path"] = new_path
        # Remove __seo_path from query string
        query_params = dict(request.query_params)
        query_params.pop("__seo_path", None)
        if query_params:
            from urllib.parse import urlencode
            request.scope["query_string"] = urlencode(query_params).encode()
        else:
            request.scope["query_string"] = b""
    return await call_next(request)


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return f"""User-agent: *
Allow: /
Allow: /products
Allow: /products/
Allow: /blog
Allow: /blog/
Allow: /about
Allow: /factory
Allow: /contact
Allow: /return-policy
Allow: /privacy-policy
Allow: /terms
Disallow: /admin
Disallow: /admin/*
Disallow: /api/admin/
Disallow: /api/admin/*

# Google
User-agent: Googlebot
Allow: /
Disallow: /admin
Disallow: /api/admin/

# Bing
User-agent: Bingbot
Allow: /
Disallow: /admin
Disallow: /api/admin/

# AI Crawlers
User-agent: GPTBot
Allow: /
Disallow: /admin

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Anthropic-ai
Allow: /

User-agent: OAI-SearchBot
Allow: /

Sitemap: {WEBSITE_URL}/sitemap.xml
"""


# ----------------- App Setup -----------------
app.include_router(api_router)
app.include_router(admin_router)

# Also include routes with stripped prefix for Vercel Python runtime
app.include_router(api_router, prefix="")
app.include_router(admin_router, prefix="")

ALLOWED_ORIGINS = [
    "https://www.gaganengineerings.in",
    "https://gaganengineerings.in",
    "https://gagan-engineering-website.vercel.app",
    "https://gagan-engineering-website-six.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
custom_cors = os.environ.get("CORS_ORIGINS", "")
if custom_cors:
    for origin in custom_cors.split(","):
        clean_origin = origin.strip()
        if clean_origin and clean_origin not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(clean_origin)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
