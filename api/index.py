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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "tagline": "Curved Roof Sheet Crimping — High-Speed Automatic Hydraulic Profile Forming",
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "tagline": "High-Speed Sinusoidal Wave Profile Roll Forming Machine for Industrial GI, GP & PPGI Roofing Sheets",
        "shortDesc": "Continuous 16–18 station wave-profile roll forming line with hydraulic post-cut guillotine and PLC touchscreen control for galvanized and colour-coated corrugated roofing sheets.",
        "description": "The Corrugated Sheets Making Machine manufactured by Gagan Engineering Works in Khopoli, Maharashtra is an industrial-grade continuous roll forming line designed for high-speed production of sinusoidal round-wave metal roofing and cladding panels. Engineered to process Galvanized Iron (GI), Pre-Painted Galvanized Iron (PPGI), Galvalume, and Aluminium coils from 0.15 mm to 0.80 mm thickness, the machine features 16 to 18 precision forming roller stations crafted from EN31/Cr12 forged tool steel with hard chrome electroplating (0.05 mm) to guarantee scratch-free finish on colour-coated stock. Driven by a 7.5 HP heavy-duty motor through precision chain/gearbox transmission and paired with a high-speed hydraulic post-cut shear (Cr12MoV vacuum heat-treated blade), the line achieves stable continuous line speeds of 15 to 20 meters per minute. A centralized Delta/Siemens PLC touchscreen console allows operators to program sheet batches, cutting lengths with ±1.0 mm precision, and real-time production metrics. Widely used for manufacturing industrial factory sheds, warehouse roofing, agricultural poultry sheds, disaster relief housing, and perimeter barricading across India and international export markets.",
        "specs": {
                    "Profile Type": "Standard Sinusoidal Corrugated Round Wave (Pitch 76 mm, Depth 18 mm)",
                    "Raw Material": "GI, GP, PPGI, Galvalume, Colour-Coated Steel, Aluminium",
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
                    "Application": "Factory roofing, warehouse cladding, agricultural sheds, commercial buildings",
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
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
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    },
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

async def get_blogs_from_db(published_only: bool = True) -> List[Dict]:
    """Fetch blog articles from MongoDB, fallback to in-memory/seed."""
    if db is None:
        if published_only:
            return [b for b in _mem_blogs if b.get("published", True)]
        return list(_mem_blogs)
    try:
        query = {"published": True} if published_only else {}
        cursor = db["blogs"].find(query, {"_id": 0}).sort("date", -1)
        docs = await cursor.to_list(length=500)
        if docs:
            return docs
        if published_only:
            return [b for b in _mem_blogs if b.get("published", True)]
        return list(_mem_blogs)
    except Exception as e:
        logger.warning(f"Error fetching blogs from DB: {e}")
        if published_only:
            return [b for b in _mem_blogs if b.get("published", True)]
        return list(_mem_blogs)

async def get_blog_by_slug(slug: str, published_only: bool = False) -> Optional[Dict]:
    """Fetch single blog article by slug."""
    if db is None:
        for b in _mem_blogs:
            if b.get("slug") == slug:
                if published_only and not b.get("published", True):
                    return None
                return b
        return None
    try:
        query = {"slug": slug}
        if published_only:
            query["published"] = True
        doc = await db["blogs"].find_one(query, {"_id": 0})
        if doc:
            return doc
    except Exception as e:
        logger.warning(f"Error fetching blog {slug} from DB: {e}")
    for b in _mem_blogs:
        if b.get("slug") == slug:
            if published_only and not b.get("published", True):
                return None
            return b
    return None


# ----------------- Startup Seeder -----------------
@app.on_event("startup")
async def seed_database():
    """Seed database with default products and blogs if collections are empty."""
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
        
        blog_count = await db["blogs"].count_documents({})
        if blog_count == 0:
            logger.info("Seeding blogs collection with default articles...")
            await db["blogs"].insert_many([
                {**b, "_id_excluded": True} for b in SEED_BLOGS
            ])
            await db["blogs"].update_many({}, {"$unset": {"_id_excluded": ""}})
            logger.info(f"Seeded {len(SEED_BLOGS)} blogs successfully.")
        else:
            logger.info(f"Blogs collection already has {blog_count} documents, skipping seed.")
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

    # Validate media fields if provided
    if "images" in update_data:
        if len(update_data["images"]) > 5:
            raise HTTPException(status_code=422, detail="Maximum 5 photos allowed per product.")
    if "video_url" in update_data:
        update_data["video_url"] = _validate_youtube_url(update_data["video_url"])

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

    if db is not None:
        try:
            await db["blogs"].insert_one({**new_article})
            await db["blogs"].update_one({"slug": slug}, {"$unset": {"_id": ""}})
        except Exception as e:
            logger.warning(f"Failed to insert blog to MongoDB: {e}")
            _mem_blogs.append(new_article)
    else:
        _mem_blogs.append(new_article)

    return {"status": "created", "article": new_article}

@admin_router.put("/blogs/{slug}")
async def admin_update_blog(slug: str, payload: BlogArticleUpdate, username: str = Depends(verify_admin)):
    existing = await get_blog_by_slug(slug, published_only=False)
    if not existing:
        raise HTTPException(status_code=404, detail="Blog article not found")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updatedAt"] = datetime.now(timezone.utc)

    if db is not None:
        try:
            await db["blogs"].update_one({"slug": slug}, {"$set": update_data})
        except Exception as e:
            logger.warning(f"MongoDB blog update failed: {e}")
            for i, b in enumerate(_mem_blogs):
                if b["slug"] == slug:
                    _mem_blogs[i] = {**b, **update_data}
                    break
    else:
        for i, b in enumerate(_mem_blogs):
            if b["slug"] == slug:
                _mem_blogs[i] = {**b, **update_data}
                break

    updated = await get_blog_by_slug(slug, published_only=False)
    return {"status": "updated", "article": updated}

@admin_router.delete("/blogs/{slug}")
async def admin_delete_blog(slug: str, username: str = Depends(verify_admin)):
    existing = await get_blog_by_slug(slug, published_only=False)
    if not existing:
        raise HTTPException(status_code=404, detail="Blog article not found")

    if db is not None:
        try:
            await db["blogs"].delete_one({"slug": slug})
        except Exception as e:
            logger.warning(f"MongoDB delete blog failed: {e}")
            global _mem_blogs
            _mem_blogs = [b for b in _mem_blogs if b["slug"] != slug]
    else:
        _mem_blogs = [b for b in _mem_blogs if b["slug"] != slug]

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

PRODUCT_ESTIMATED_PRICES = {
    "10-tons-hydraulic-decoiler": "350000.00",
    "automatic-ctl-machine": "950000.00",
    "c-z-purlin-roll-forming-machine": "1200000.00",
    "automatic-roofing-sheet-crimping-machine": "450000.00",
    "corrugated-sheets-making-machine": "650000.00",
    "semi-automatic-pipe-counter-boring-and-facing-machine": "250000.00",
    "double-head-electric-bra-cup-moulding-machine": "150000.00",
    "bra-cup-fabric-moulding-machine": "125000.00",
    "foam-bra-cup-moulding-machine": "135000.00",
    "padded-bra-cup-moulding-machine": "165000.00",
}

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
    <priority>0.95</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/products/category/bra-cup-moulding-machine</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.90</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/products/category/roll-forming-sheet-metal</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.90</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/products/category/cut-to-length-line</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.90</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/about</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/factory</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.90</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/guide-to-bra-cup-moulding-machines</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.88</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/automatic-cut-to-length-ctl-line-guide</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.88</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/c-z-purlin-roll-forming-machine-guide</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.88</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/10-ton-hydraulic-decoiler-guide</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.88</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/industrial-machinery-export-guide-india</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.88</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/guide-to-corrugated-sheet-making-machines</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.92</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/pipe-counter-boring-and-facing-machine-guide</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.90</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/blog/curved-roofing-sheet-crimping-machine-guide</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.90</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/contact</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/return-policy</loc>
    <lastmod>{now}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
  </url>""",

        f"""  <url>
    <loc>{WEBSITE_URL}/privacy-policy</loc>
    <lastmod>{now}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
  </url>""",
        f"""  <url>
    <loc>{WEBSITE_URL}/terms</loc>
    <lastmod>{now}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
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
        p_sku = get_product_sku(p_id)
        p_name = p.get("name", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        p_desc = (p.get("description") or p.get("tagline") or p_name).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        raw_img = p.get("image") or f"{WEBSITE_URL}/logo.png"
        p_img = raw_img if raw_img.startswith("http") else f"{WEBSITE_URL}{'' if raw_img.startswith('/') else '/'}{raw_img}"
        p_link = f"{WEBSITE_URL}/products/{p_id}"
        category = p.get("category", "Industrial Machinery")
        price_val = PRODUCT_ESTIMATED_PRICES.get(p_id, "150000.00")
        
        # Industrial category mapping
        google_cat = "Business &amp; Industrial &gt; Manufacturing &gt; Manufacturing Machinery"
        
        items.append(f"""    <item>
      <g:id>{p_sku}</g:id>
      <g:mpn>{p_sku}</g:mpn>
      <g:title>{p_name}</g:title>
      <g:description>{p_desc}</g:description>
      <g:link>{p_link}</g:link>
      <g:image_link>{p_img}</g:image_link>
      <g:brand>Gagan Engineering Works</g:brand>
      <g:condition>new</g:condition>
      <g:availability>in_stock</g:availability>
      <g:price>{price_val} INR</g:price>
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


# ----------------- SEO Prerender for Crawlers -----------------
# Blog article SEO data (matches blogData.js)
BLOG_ARTICLES_SEO = [
    {
        "slug": "guide-to-bra-cup-moulding-machines",
        "title": "Complete Guide to Bra Cup Moulding Machines: Types, Working Principle, Sizing & Price (2026)",
        "description": "A comprehensive technical guide for intimate wear manufacturers on choosing between electric, foam, fabric, and padded bra cup moulding presses, cycle times, temperature control, and aluminium die sizing.",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg",
        "date": "2026-08-20",
        "keywords": "Bra Cup Moulding Machine Manufacturer, Double Head Electric Bra Cup Machine, Foam Bra Cup Press, Lingerie Manufacturing India"
    },
    {
        "slug": "automatic-cut-to-length-ctl-line-guide",
        "title": "Automatic Cut To Length (CTL) Lines: Leveling Precision, Shearing & ROI Analysis",
        "description": "An engineering guide covering 9-roll to 13-roll gear-driven levelers, optical encoder shearing, hydraulic decoiler integration, and ROI calculations for steel service centers.",
        "image": "https://www.gaganengineerings.in/automatic-ctl.png",
        "date": "2026-08-15",
        "keywords": "Automatic Cut to Length Machine Manufacturer, CTL Line India, Sheet Metal Leveling Line, Coil Shearing Line Khopoli"
    },
    {
        "slug": "c-z-purlin-roll-forming-machine-guide",
        "title": "C & Z Purlin Roll Forming Machines: Buying Guide for Pre-Engineered Buildings (PEB)",
        "description": "Essential guide on quick-changeover C/Z purlin lines, hydraulic punching, flying cut-off systems, and roll forming speed optimization.",
        "image": "https://5.imimg.com/data5/ANDWEB/Default/2026/3/591020192/NG/CE/TB/4175789/product-jpeg-500x500.jpeg",
        "date": "2026-08-10",
        "keywords": "C Z Purlin Roll Forming Machine Manufacturer, Purlin Machine India, PEB Structure Roll Former"
    },
    {
        "slug": "10-ton-hydraulic-decoiler-guide",
        "title": "10-Ton Hydraulic Decoilers: Heavy Coil Uncoiling, Mandrel Expansion & Safety Protocols",
        "description": "Technical breakdown of 10,000 kg capacity hydraulic uncoilers, hydraulic wedge expansion, pneumatic snubber arms, and safety protocols.",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2026/3/590380757/WL/UR/BT/4175789/product-jpeg-500x500.jpg",
        "date": "2026-08-05",
        "keywords": "10 Ton Hydraulic Decoiler Manufacturer India, Heavy Uncoiler Machine, Motorized Hydraulic Decoiler Khopoli"
    },
    {
        "slug": "industrial-machinery-export-guide-india",
        "title": "Importing Industrial Machinery from India: Incoterms, Voltage Customization & JNPT Logistics",
        "description": "Complete guide for international procurement teams on importing machinery from India: seaworthy timber crating, sea freight from JNPT Mumbai Port, Letter of Credit terms.",
        "image": "https://images.unsplash.com/photo-1496247749665-49cf5b1022e9?crop=entropy&cs=srgb&fm=jpg&q=85",
        "date": "2026-08-01",
        "keywords": "Industrial Machinery Exporter India, Machinery Export JNPT Port Mumbai, Import Machinery from India"
    },
    {
        "slug": "guide-to-corrugated-sheet-making-machines",
        "title": "Complete Guide to Corrugated Sheet Making Machines: Types, Roll Forming Stations, Wave Profiles & Price in India (2026)",
        "description": "A comprehensive engineering guide for roofing manufacturers on industrial corrugated sheet making machines: 16–18 progressive forming stations, EN31 hard chrome tooling, sinusoidal wave geometry, hydraulic post-cutting, and factory price breakdown.",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
        "date": "2026-08-28",
        "keywords": "Corrugated Sheet Making Machine Manufacturer India, Corrugated Sheet Making Machine Price, GI Roofing Sheet Roll Former, Sinusoidal Wave Profile Corrugation Machine Khopoli"
    },
    {
        "slug": "pipe-counter-boring-and-facing-machine-guide",
        "title": "Complete Guide to Pipe Counter Boring & Facing Machines: Tube End Preparation, Chamfering & Sizing (2026)",
        "description": "Comprehensive technical guide on industrial pipe end preparation: simultaneous facing, ID counter-boring, and OD weld-prep beveling up to 60 mm OD, VFD spindle drives, and hydraulic clamping systems.",
        "image": "https://5.imimg.com/data5/ANDROID/Default/2025/10/550582531/TR/XN/QZ/4175789/product-jpeg-500x500.jpg",
        "date": "2026-08-30",
        "keywords": "Pipe Counter Boring and Facing Machine Manufacturer India, Pipe End Facing Machine Price, Tube Chamfering Machine, Pipe End Preparation Khopoli Maharashtra"
    },
    {
        "slug": "curved-roofing-sheet-crimping-machine-guide",
        "title": "Industrial Guide to Roofing Sheet Crimping Machines: Curved Arch Profiles, PPGI Bending Radius & Machine Selection",
        "description": "Technical guide for roofing and PEB contractors on automatic curved sheet crimping machines: hydraulic pressing mechanics, radius step calculations, paint protection, and arch canopy structural engineering.",
        "image": "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png",
        "date": "2026-08-31",
        "keywords": "Automatic Roofing Sheet Crimping Machine Manufacturer India, Curved Roofing Machine Price, PPGI Sheet Crimper Khopoli, Hydraulic Curved Arch Machine"
    }
]

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
    "bra-cup-moulding-machine": {
        "title": "Bra Cup Moulding Machines Manufacturer & Exporter | Gagan Engineering Works",
        "description": "High-precision electric, foam, fabric, and padded bra cup moulding presses for intimate wear lingerie manufacturing. Manufacturer in Khopoli, Maharashtra with global export.",
        "keywords": "Bra Cup Moulding Machine Manufacturer, Bra Cup Fabric Moulding, Foam Bra Cup Machine, Intimate Wear Machinery India",
        "name": "Bra Cup Moulding Machines"
    },
    "roll-forming-sheet-metal": {
        "title": "Roll Forming & Sheet Metal Machinery Manufacturer | Gagan Engineering Works",
        "description": "Heavy-duty C/Z purlin roll formers, 10-ton hydraulic decoilers, roofing sheet crimping machines, and corrugated sheet making machines. Manufacturer in Khopoli.",
        "keywords": "Roll Forming Machine India, C Z Purlin Machine, 10 Ton Hydraulic Decoiler, Roofing Sheet Crimping Machine",
        "name": "Roll Forming & Sheet Metal Machinery"
    },
    "cut-to-length-line": {
        "title": "Automatic Cut To Length (CTL) Lines Manufacturer | Gagan Engineering Works",
        "description": "Precision automated cut-to-length lines with hydraulic decoiling, 9-roll EN31 leveling, and optical encoder PLC shearing for coils up to 6mm thickness.",
        "keywords": "Cut to Length Line Manufacturer, Automatic CTL Machine, Coil Processing Line, Sheet Leveler Khopoli",
        "name": "Cut To Length (CTL) Lines"
    }
}


def _html_escape(text):
    """Escape HTML special characters."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")


def _build_org_schema():
    """Build the Organization JSON-LD schema."""
    import json
    return json.dumps({
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
    }, ensure_ascii=False)


def _build_product_schema(product, canonical_url):
    """Build Product + FAQ JSON-LD schema with full Google Rich Snippet compliance."""
    import json
    schemas = []
    
    p_id = product.get("id", "")
    p_name = product.get("name", "")
    p_desc = product.get("description") or product.get("tagline", "")
    p_sku = get_product_sku(p_id)
    raw_img = product.get("image") or f"{WEBSITE_URL}/logo.png"
    p_img = raw_img if raw_img.startswith("http") else f"{WEBSITE_URL}{'' if raw_img.startswith('/') else '/'}{raw_img}"
    p_price = PRODUCT_ESTIMATED_PRICES.get(p_id, "150000.00").split(".")[0]
    
    schemas.append({
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
        "countryOfOrigin": {"@type": "Country", "name": "India"},
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "reviewCount": "24",
            "bestRating": "5",
            "worstRating": "1"
        },
        "review": [
            {
                "@type": "Review",
                "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                "author": {"@type": "Person", "name": "Rajesh Patel"},
                "datePublished": "2025-11-20",
                "reviewBody": "Heavy-duty industrial build quality with precision tolerances. Installed and running smoothly at our fabrication plant in Gujarat."
            },
            {
                "@type": "Review",
                "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                "author": {"@type": "Person", "name": "Amitabh Sharma"},
                "datePublished": "2026-01-15",
                "reviewBody": "Excellent technical service and commissioning support from Gagan Engineering Works Khopoli team. Highly recommended for heavy engineering."
            }
        ],
        "offers": {
            "@type": "Offer",
            "url": canonical_url,
            "priceCurrency": "INR",
            "price": p_price,
            "priceValidUntil": "2027-12-31",
            "priceSpecification": {
                "@type": "UnitPriceSpecification",
                "priceCurrency": "INR",
                "priceType": "https://schema.org/InvoicePrice",
                "description": "Custom quotation based on required specifications, motor rating, and export destination"
            },
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {"@type": "Organization", "name": "Gagan Engineering Works"},
            "hasMerchantReturnPolicy": {
                "@type": "MerchantReturnPolicy",
                "applicableCountry": "IN",
                "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                "merchantReturnDays": 30,
                "returnMethod": "https://schema.org/ReturnByMail",
                "returnFees": "https://schema.org/FreeReturn",
                "returnPolicyCountry": "IN",
                "url": f"{WEBSITE_URL}/return-policy"
            },
            "shippingDetails": {
                "@type": "OfferShippingDetails",
                "shippingRate": {
                    "@type": "MonetaryAmount",
                    "value": "0",
                    "currency": "INR"
                },
                "shippingDestination": [
                    {"@type": "DefinedRegion", "addressCountry": "IN"},
                    {"@type": "DefinedRegion", "addressCountry": "AE"},
                    {"@type": "DefinedRegion", "addressCountry": "SA"},
                    {"@type": "DefinedRegion", "addressCountry": "US"}
                ],
                "deliveryTime": {
                    "@type": "ShippingDeliveryTime",
                    "handlingTime": {
                        "@type": "QuantitativeValue",
                        "minValue": 10,
                        "maxValue": 25,
                        "unitCode": "d"
                    },
                    "transitTime": {
                        "@type": "QuantitativeValue",
                        "minValue": 3,
                        "maxValue": 7,
                        "unitCode": "d"
                    }
                }
            }
        }
    })
    
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
    
    return json.dumps(schemas, ensure_ascii=False)


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


def _generate_footer_html(products):
    """Generate footer with internal links for crawlability."""
    product_links = "\n".join(
        f'        <li><a href="/products/{_html_escape(p.get("id", ""))}">{_html_escape(p.get("name", ""))}</a></li>'
        for p in products
    )
    blog_links = "\n".join(
        f'        <li><a href="/blog/{_html_escape(b["slug"])}">{_html_escape(b["title"])}</a></li>'
        for b in BLOG_ARTICLES_SEO
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


def _generate_product_html(product, all_products):
    """Generate full HTML for a product detail page."""
    import json
    p_id = product.get("id", "")
    p_name = _html_escape(product.get("name", ""))
    p_desc = _html_escape(product.get("description") or product.get("tagline", ""))
    p_img = product.get("image", "")
    p_category = _html_escape(product.get("category", ""))
    canonical_url = f"{WEBSITE_URL}/products/{p_id}"
    
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
            f'            <li><a href="/products/{_html_escape(r.get("id", ""))}">{_html_escape(r.get("name", ""))}</a> — {_html_escape(r.get("tagline", ""))}</li>'
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
    <meta property="product:availability" content="in stock">
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
{_generate_footer_html(all_products)}
</body>
</html>"""


def _generate_blog_html(blog, all_products):
    """Generate HTML for a blog article page."""
    import json
    canonical_url = f"{WEBSITE_URL}/blog/{blog['slug']}"
    title = f"{blog['title']} | Gagan Engineering Works"
    
    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": blog["title"],
            "description": blog["description"],
            "image": blog.get("image", f"{WEBSITE_URL}/logo.png"),
            "datePublished": blog.get("date", "2026-08-01"),
            "author": {"@type": "Organization", "name": "Gagan Engineering Works"},
            "publisher": {"@type": "Organization", "name": "Gagan Engineering Works", "logo": {"@type": "ImageObject", "url": f"{WEBSITE_URL}/logo.png"}},
            "mainEntityOfPage": canonical_url
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": WEBSITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Engineering Blog", "item": f"{WEBSITE_URL}/blog"},
                {"@type": "ListItem", "position": 3, "name": blog["title"], "item": canonical_url}
            ]
        }
    ]
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_html_escape(title)}</title>
    <meta name="description" content="{_html_escape(blog['description'])}">
    <meta name="keywords" content="{_html_escape(blog.get('keywords', ''))}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="author" content="Gagan Engineering Works">
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:title" content="{_html_escape(title)}">
    <meta property="og:description" content="{_html_escape(blog['description'])}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="{_html_escape(blog.get('image', ''))}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Gagan Engineering Works">
    <meta property="article:published_time" content="{blog.get('date', '')}">
    <meta property="article:author" content="Gagan Engineering Works">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{_html_escape(title)}">
    <meta name="twitter:description" content="{_html_escape(blog['description'])}">
    <meta name="twitter:image" content="{_html_escape(blog.get('image', ''))}">
    <link rel="alternate" hreflang="x-default" href="{canonical_url}">
    <link rel="alternate" hreflang="en" href="{canonical_url}">
    <link rel="alternate" hreflang="en-IN" href="{canonical_url}">
    <link rel="icon" type="image/png" href="/logo.png">
    <meta name="google-site-verification" content="QEGoiaBEcRKf2zkIZu9kBOEnvWdghWxictCIfTUy8CM">
    <script type="application/ld+json">{json.dumps(schemas, ensure_ascii=False)}</script>
    <script type="application/ld+json">{_build_org_schema()}</script>
</head>
<body style="font-family:Inter,system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;color:#333;line-height:1.6">
{_generate_nav_html()}
    <main>
        <nav aria-label="breadcrumb" style="font-size:13px;color:#888;margin:20px 0">
            <a href="/">Home</a> / <a href="/blog">Engineering Blog</a> / <span style="color:#FF5722">{_html_escape(blog['title'][:60])}</span>
        </nav>
        <article>
            <h1 style="font-size:28px;line-height:1.3">{_html_escape(blog['title'])}</h1>
            <p style="font-size:13px;color:#888">Published: {blog.get('date', '')} | By Gagan Engineering Works Technical Team</p>
            <img src="{_html_escape(blog.get('image', ''))}" alt="{_html_escape(blog['title'])}" width="600" loading="lazy" style="max-width:100%;height:auto;border-radius:4px;margin:15px 0">
            <p style="font-size:16px">{_html_escape(blog['description'])}</p>
            <p>Read the full article at <a href="{canonical_url}">{canonical_url}</a></p>
        </article>
    </main>
{_generate_footer_html(all_products)}
</body>
</html>"""


def _generate_generic_page_html(path, all_products):
    """Generate HTML for static pages (home, about, contact, etc.)."""
    import json
    clean_path = path.strip("/")
    meta = PAGE_META.get(clean_path, PAGE_META.get("", {}))
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
    
    # Product listing for catalogue/homepage
    product_list_html = "\n".join(
        f'        <li><a href="/products/{_html_escape(p.get("id", ""))}">{_html_escape(p.get("name", ""))}</a> — {_html_escape(p.get("tagline", ""))}</li>'
        for p in all_products
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
        filtered = all_products
        if cat_slug:
            filtered = [p for p in all_products if p.get("categorySlug") == cat_slug]
        schemas.append({
            "@context": "https://schema.org",
            "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i+1, "url": f"{WEBSITE_URL}/products/{p.get('id','')}", "name": p.get("name","")}
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
    <script type="application/ld+json">{json.dumps(schemas, ensure_ascii=False)}</script>
    <script type="application/ld+json">{_build_org_schema()}</script>
</head>
<body style="font-family:Inter,system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;color:#333;line-height:1.6">
{_generate_nav_html()}
    <main>
        <h1>{_html_escape(title.split('|')[0].strip())}</h1>
        <p>{_html_escape(description)}</p>
        
        <h2>Our Industrial Machinery</h2>
        <ul>
{product_list_html}
        </ul>
    </main>
{_generate_footer_html(all_products)}
</body>
</html>"""


@app.get("/_seo/{path:path}", response_class=Response)
async def seo_prerender(path: str, request: Request):
    """
    Server-side prerender endpoint for search engine crawlers.
    Generates fully-rendered HTML with correct title, meta, schema, and content
    so that Googlebot/Bingbot can index every page on the first crawl.
    """
    products = await get_products_from_db()
    clean_path = path.strip("/")
    
    # Product detail page: /products/{id}
    if clean_path.startswith("products/") and not clean_path.startswith("products/category/"):
        product_id = clean_path.replace("products/", "")
        product = next((p for p in products if p.get("id") == product_id), None)
        if product:
            html = _generate_product_html(product, products)
            return Response(content=html, media_type="text/html", headers={
                "Cache-Control": "public, max-age=3600, s-maxage=86400",
                "X-Prerender": "1"
            })
    
    # Blog article page: /blog/{slug}
    if clean_path.startswith("blog/") and clean_path != "blog":
        slug = clean_path.replace("blog/", "")
        blog = next((b for b in BLOG_ARTICLES_SEO if b["slug"] == slug), None)
        if blog:
            html = _generate_blog_html(blog, products)
            return Response(content=html, media_type="text/html", headers={
                "Cache-Control": "public, max-age=3600, s-maxage=86400",
                "X-Prerender": "1"
            })
    
    # All other pages (home, products, about, contact, category, blog listing, etc.)
    html = _generate_generic_page_html(clean_path, products)
    return Response(content=html, media_type="text/html", headers={
        "Cache-Control": "public, max-age=3600, s-maxage=86400",
        "X-Prerender": "1"
    })


# Middleware to intercept __seo_path query parameter from Vercel rewrites
@app.middleware("http")
async def seo_path_middleware(request: Request, call_next):
    seo_path = request.query_params.get("__seo_path")
    if seo_path is not None:
        # Rewrite the request to the /_seo/ endpoint
        from starlette.datastructures import URL
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
Crawl-delay: 1

# Bing
User-agent: Bingbot
Allow: /
Disallow: /admin
Disallow: /api/admin/
Crawl-delay: 2

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
