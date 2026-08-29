// Centralized Catalogue Data with comprehensive technical specifications for SEO, Frontend, and AI Advisor
export const CATALOGUE_PRODUCTS = [
  // Heavy Engineering, Coil Processing & Roll Forming Lines (Priority / Top)
  {
    id: "10-tons-hydraulic-decoiler",
    name: "10 Tons Hydraulic Decoiler",
    category: "Roll Forming & Sheet Metal",
    categorySlug: "roll-forming-sheet-metal",
    image: "https://5.imimg.com/data5/ANDROID/Default/2026/3/590380757/WL/UR/BT/4175789/product-jpeg-500x500.jpg",
    tagline: "Heavy-duty 10,000 kg capacity hydraulic uncoiler for roll forming lines",
    shortDesc: "Industrial motorized hydraulic decoiler with 10-ton capacity, hydraulic expansion, and pneumatic braking.",
    description: "10-ton capacity hydraulic decoiler built for steel and aluminium coil feeding into high-speed roll-forming, slitting, and CTL lines. Features hydraulic mandrel expansion, motorized forward/reverse rotation, hydraulic coil loading car (optional), and pneumatic disc brake for controlled tension unwinding.",
    specs: {
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
    featured: true,
    faqs: [
      {
        q: "What coil weights can this decoiler support?",
        a: "It is rated for continuous duty with metal coils weighing up to 10 Metric Tons (10,000 kg)."
      },
      {
        q: "Is the mandrel expansion motorized or hydraulic?",
        a: "Mandrel expansion is powered by a dedicated hydraulic cylinder with sensor-based pressure retention."
      }
    ]
  },
  {
    id: "automatic-ctl-machine",
    name: "Automatic Cut To Length (CTL) Machine",
    category: "Cut To Length Line",
    categorySlug: "cut-to-length-line",
    image: "/automatic-ctl.png",
    images: ["/automatic-ctl.png"],
    tagline: "High-speed precision Cut-to-Length Line for heavy-duty metal coil processing up to 6mm",
    shortDesc: "Complete automated cut-to-length line with 10-ton decoiler, 9-roll leveler, and hydraulic shear.",
    description: "The Automatic CTL (Cut-to-Length) Line is engineered for heavy-duty, high-accuracy metal sheet processing. It processes metal coils continuously through automatic decoiling, precision 9-roll leveling, encoder-based length measurement, heavy mechanical/hydraulic shearing, and exit conveyance. Equipped with touch-screen PLC controls and Yuken hydraulics, it minimizes scrap and guarantees tight sheet length tolerances.",
    specs: {
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
    featured: false,
    faqs: [
      {
        q: "What is the cutting length accuracy of this CTL line?",
        a: "The optical encoder feedback system maintains length accuracy within ±0.5 mm across batch runs."
      },
      {
        q: "What maximum coil thickness can it level and cut?",
        a: "This model is engineered for sheets up to 6.0 mm thickness, powered by hardened EN31 9-roll levelers and a 7.5 HP drive."
      }
    ]
  },
  {
    id: "c-z-purlin-roll-forming-machine",
    name: "C / Z Purlin Roll Forming Machine",
    category: "Roll Forming & Sheet Metal",
    categorySlug: "roll-forming-sheet-metal",
    image: "https://5.imimg.com/data5/ANDWEB/Default/2026/3/591020192/NG/CE/TB/4175789/product-jpeg-500x500.jpeg",
    tagline: "Interchangeable C & Z section purlin line with automated size change and punching",
    shortDesc: "High-speed roll forming line producing structural C and Z purlins for Pre-Engineered Buildings (PEB).",
    description: "Quick-change C and Z section roll forming machine. Integrated hydraulic hole punching, roll forming, and automatic flying shear cutting in a single continuous line. Used in pre-engineered steel buildings (PEB), solar mounting structures, warehouses, and industrial infrastructure.",
    specs: {
      "Section Types": "C-Purlin (100–300 mm) & Z-Purlin (100–300 mm)",
      "Material Thickness": "1.5 mm to 3.0 mm Galvanized / HR Steel",
      "Line Speed": "10–18 meters per minute",
      "Roller Stations": "16–20 Forming Stations (Cr12 / EN31 Tool Steel)",
      "Control System": "Delta/Siemens PLC + Touch Screen HMI",
      "Shearing": "Hydraulic Post-Cut System (No waste profile cut)",
      "Punching": "Multi-head hydraulic hole & slot punching unit",
      "Total Power": "Approx. 25–30 HP connected load"
    },
    featured: true,
    faqs: [
      {
        q: "How long does it take to switch from C-purlin to Z-purlin profile?",
        a: "Our quick-adjust roller assembly allows changeover between C and Z profiles in under 30 minutes with minimal manual wrenching."
      }
    ]
  },
  {
    id: "automatic-roofing-sheet-crimping-machine",
    name: "Automatic Roofing Sheet Crimping Machine",
    category: "Roll Forming & Sheet Metal",
    categorySlug: "roll-forming-sheet-metal",
    image: "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png",
    tagline: "Curved roof sheet crimping — high-speed automatic hydraulic profile forming",
    shortDesc: "Automated crimping machine for curved roofing sheets used in industrial sheds, warehouses, and stadiums.",
    description: "Engineered to form curved and crimped arch profiles in pre-painted galvanized iron (PPGI), GP, or aluminium roofing sheets. Widely deployed across India for curved industrial sheds, warehouse canopies, airport hangars, and sports stadium roofing projects.",
    specs: {
      "Sheet Width Supported": "Up to 1250 mm standard profile",
      "Material Thickness": "0.3 mm to 0.8 mm",
      "Compatible Sheets": "PPGI, GP, Aluminium, Colour-Coated Steel",
      "Drive Mechanism": "Electric Motor + Hydraulic Crimping Unit",
      "Crimping Radius": "Adjustable arc radius from 2m to infinity",
      "Control System": "PLC with Touchscreen HMI Interface",
      "Application": "Curved warehouse roofing, petrol pump canopies, industrial arch buildings"
    },
    featured: true,
    faqs: [
      {
        q: "Can the crimping curve radius be adjusted?",
        a: "Yes, the crimp pitch and bending angle are programmable via the PLC touchscreen to achieve any desired curvature radius."
      }
    ]
  },
  {
    id: "corrugated-sheets-making-machine",
    name: "Corrugated Sheets Making Machine",
    category: "Roll Forming & Sheet Metal",
    categorySlug: "roll-forming-sheet-metal",
    image: "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg",
    tagline: "High-yield corrugated wave profile roll former for industrial shed roofing",
    shortDesc: "Continuous wave-profile roll forming line for galvanized and colour-coated corrugated roofing sheets.",
    description: "Engineered for rapid continuous forming of standard wave-corrugated roofing sheets from coil stock. Features high-strength chrome-plated forming rollers, synchronous hydraulic shearing, and programmable length control for industrial and agricultural roofing.",
    specs: {
      "Profile Type": "Standard Sinusoidal Corrugated Wave",
      "Raw Material": "GI, GP, PPGI, Colour-Coated Galvanized Steel",
      "Forming Speed": "12–18 meters per minute",
      "Roller Material": "Hardened 45# Steel with Hard Chrome Plating",
      "Shearing Method": "Hydraulic Post-Cut Guillotine",
      "Control System": "Microprocessor PLC with length counter",
      "Application": "Industrial factory sheds, agricultural roofing, boundary fencing"
    },
    featured: false,
    faqs: [
      {
        q: "Can this machine run pre-painted colour-coated coils without scratching?",
        a: "Yes, all forming rollers are precision CNC-machined and hard chrome-plated to ensure zero scratching on paint finishes."
      }
    ]
  },
  {
    id: "semi-automatic-pipe-counter-boring-and-facing-machine",
    name: "Semi-Automatic Pipe Counter Boring and Facing Machine",
    category: "Roll Forming & Sheet Metal",
    categorySlug: "roll-forming-sheet-metal",
    image: "https://5.imimg.com/data5/SELLER/Default/2026/4/596257189/PL/SJ/DO/4175789/456-500x500.png",
    tagline: "Precision pipe end facing & counter boring up to 60 mm OD with hydraulic clamping and VFD speed control",
    shortDesc: "Heavy-duty semi-automatic pipe counter boring and facing machine for accurate tube end preparation and beveling up to 60 mm OD.",
    description: "The Semi-Automatic Pipe Counter Boring and Facing Machine manufactured by Gagan Engineering Works in Khopoli is designed for high-precision end facing, chamfering, and internal counter boring of round pipes and industrial tubes up to 60 mm outer diameter. Powered by a 5 HP main drive with variable frequency control (100–1450 RPM) and a dedicated 1 HP hydraulic power pack (60-litre capacity), the machine delivers rigid hydraulic clamping, smooth automated feed stroke, and accurate length repeat cycles for continuous manufacturing operations.",
    specs: {
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
    featured: true,
    faqs: [
      {
        q: "What is the maximum pipe diameter handled by this machine?",
        a: "This semi-automatic machine handles pipes and tubes up to 60 mm Outside Diameter (OD) with rigid hydraulic clamping."
      },
      {
        q: "Does this machine offer variable speed control?",
        a: "Yes, it is equipped with a Variable Frequency Drive (VFD) offering smooth spindle speed adjustment between 100 and 1450 RPM."
      },
      {
        q: "What warranty and service support are provided?",
        a: "Gagan Engineering Works provides a 1-year comprehensive manufacturer warranty and on-site commissioning across India."
      }
    ]
  },

  // Intimate Wear & Lingerie Bra Cup Moulding Machinery (Bottom / Last)
  {
    id: "double-head-electric-bra-cup-moulding-machine",
    name: "Double Head Electric Bra Cup Moulding Machine",
    category: "Bra Cup Moulding Machine",
    categorySlug: "bra-cup-moulding-machine",
    image: "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg",
    tagline: "Twin-station high-output cup moulding for industrial lingerie production lines",
    shortDesc: "Double-station electric moulding press engineered for seamless bra cup manufacturing with PID thermal control.",
    description: "A heavy-duty double-head electric press engineered for continuous moulding of seamless bra cups. Twin stations allow operators to load one side while the other moulds — doubling throughput without doubling floor area. Built with hardened steel platens, precision digital PID temperature control, and timer-based pneumatic clamping for zero distortion and consistent cup depth.",
    specs: {
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
    featured: true,
    faqs: [
      {
        q: "What is the daily output capacity of this double head machine?",
        a: "A single operator can produce approximately 400 to 600 pairs of bra cups per 8-hour shift depending on foam thickness and heating dwell time."
      },
      {
        q: "Can the moulding dies/cups be changed for different sizes?",
        a: "Yes, our moulds are fully interchangeable. You can swap cup sizes (from 28A to 44DD) in less than 15 minutes."
      },
      {
        q: "What power connection is required at the factory?",
        a: "It operates on standard Indian 3-Phase 415V AC electricity with standard compressed air supply (6–8 bar) for pneumatic clamping."
      }
    ]
  },
  {
    id: "bra-cup-fabric-moulding-machine",
    name: "Bra Cup Fabric Moulding Machine",
    category: "Bra Cup Moulding Machine",
    categorySlug: "bra-cup-moulding-machine",
    image: "https://5.imimg.com/data5/ANDROID/Default/2025/10/550584110/ET/BP/NY/4175789/product-jpeg-500x500.jpg",
    tagline: "Precise fabric cup shaping with consistent edge finish and zero wrinkling",
    shortDesc: "Specialized press for moulding laminated and woven fabrics into seamless bra cup profiles.",
    description: "Engineered specifically for moulding laminated and woven fabrics into seamless cup shapes without scorch marks or fabric distortion. Features interchangeable CNC-machined aluminium moulds ensuring razor-sharp cup definition, smooth contouring, and clean edges across all batch runs.",
    specs: {
      "Material Compatibility": "Woven fabrics, cotton-spandex, polyester blends, microfibers",
      "Mould Type": "Interchangeable CNC Aluminium Moulds",
      "Cycle Time": "25–40 seconds per pressing cycle",
      "Temperature Control": "Dual Zone Digital Thermostat",
      "Power Connection": "Single Phase 220V or 3-Phase 415V (customizable)",
      "Air Pressure": "5–7 kg/cm²",
      "Application": "Lingerie, activewear, shapewear, intimate apparel",
      "Warranty": "1 Year Comprehensive Warranty"
    },
    featured: true,
    faqs: [
      {
        q: "Does this machine prevent fabric burning or discoloration on light fabrics?",
        a: "Yes, the precision digital temperature regulator and teflon-coated platen options prevent scorch marks on white and delicate pastel fabrics."
      }
    ]
  },
  {
    id: "foam-bra-cup-moulding-machine",
    name: "Foam Bra Cup Moulding Machine",
    category: "Bra Cup Moulding Machine",
    categorySlug: "bra-cup-moulding-machine",
    image: "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586856/YP/VU/KK/4175789/product-jpeg-500x500.jpg",
    tagline: "Polyurethane & memory foam hot-press cup forming with permanent shape retention",
    shortDesc: "Thermal compression machine for forming high-density PU and memory foam bra cups.",
    description: "Built for hot-press moulding of polyurethane (PU), memory foam, and polyester foam sheets into ergonomic cup shapes. Uniform heating plates and high-force pneumatic clamping deliver repeatable shape memory and even wall thickness across the entire cup curve.",
    specs: {
      "Foam Types Supported": "PU Foam, High-Resilience Foam, Memory Foam, Spacer Fabric",
      "Heating System": "Top & Bottom Heated Platens",
      "Pressure System": "High-Force Pneumatic Clamping Cylinder",
      "Output": "Up to 500 pieces per shift",
      "Temperature Range": "50°C to 260°C adjustable",
      "Automation": "Semi-Automatic with Push Button & Foot Switch",
      "Application": "Bra cups, shoulder pads, sports bra pads"
    },
    featured: false,
    faqs: [
      {
        q: "Can this machine handle memory foam and high-density foam?",
        a: "Yes, the dual-heated platens allow controlled heat penetration ideal for memory foam and high-density PU materials."
      }
    ]
  },
  {
    id: "padded-bra-cup-moulding-machine",
    name: "Padded Bra Cup Moulding Machine",
    category: "Bra Cup Moulding Machine",
    categorySlug: "bra-cup-moulding-machine",
    image: "https://5.imimg.com/data5/SELLER/Default/2026/5/608537665/KG/TS/VJ/4175789/padded-bra-cup-moulding-machine-500x500.png",
    tagline: "Multi-layer padded cup moulding combining foam, fabric, and inner lining in one cycle",
    shortDesc: "Specialized multi-layer press designed for premium push-up and graduated padded bra cups.",
    description: "Specialised multi-layer press designed for composite padded cups combining foam, outer fabric, and inner lining in a single synchronized press cycle. Ideal for premium push-up bras, graduated padding, and seamless contour lingerie manufacturing.",
    specs: {
      "Layering Capability": "Multi-layer composite (Fabric + Foam + Lining)",
      "Heating": "Dual-side independent temperature control",
      "Cycle Programmability": "Programmable timer (20–60 seconds)",
      "Power Requirement": "3-Phase 415V AC",
      "Safety Mechanism": "Dual hand start safety interlock",
      "Application": "Push-up cups, padded T-shirt bras, bridal intimate wear"
    },
    featured: false,
    faqs: [
      {
        q: "Can it mould graduated push-up cups?",
        a: "Yes, custom graduated CNC moulds can be installed to create push-up pads with varying bottom-to-top thickness."
      }
    ]
  }
];

export const CATEGORIES = [
  { id: "all", name: "All Machinery" },
  { id: "roll-forming-sheet-metal", name: "Roll Forming & Sheet Metal" },
  { id: "cut-to-length-line", name: "Cut To Length Line" },
  { id: "bra-cup-moulding-machine", name: "Bra Cup Moulding Machine" }
];

export function getLiveCatalogueProducts() {
  try {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("gagan_custom_products");
      if (stored) {
        const custom = JSON.parse(stored);
        if (Array.isArray(custom) && custom.length > 0) {
          const merged = [...CATALOGUE_PRODUCTS];
          custom.forEach((c) => {
            const idx = merged.findIndex((m) => m.id === c.id);
            if (idx >= 0) {
              merged[idx] = { ...merged[idx], ...c };
            } else {
              merged.push(c);
            }
          });
          return merged;
        }
      }
    }
  } catch (e) {}
  return CATALOGUE_PRODUCTS;
}

// ----------------- Media Helpers -----------------

/**
 * Automatically converts Google Drive, Dropbox, and other cloud share links
 * into direct embeddable image CDN URLs.
 */
export function normalizeImageUrl(url) {
  if (!url || typeof url !== "string") return url;
  const trimmed = url.trim();

  // Google Drive conversion (file/d/ID, open?id=ID, uc?id=ID, thumbnail?id=ID)
  const driveMatch =
    trimmed.match(/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)/) ||
    trimmed.match(/drive\.google\.com\/open\?id=([a-zA-Z0-9_-]+)/) ||
    trimmed.match(/drive\.google\.com\/uc\?(?:.*&)?id=([a-zA-Z0-9_-]+)/) ||
    trimmed.match(/drive\.google\.com\/thumbnail\?(?:.*&)?id=([a-zA-Z0-9_-]+)/);
  if (driveMatch && driveMatch[1]) {
    return `https://lh3.googleusercontent.com/d/${driveMatch[1]}`;
  }

  // Dropbox conversion (?dl=0 -> ?raw=1)
  if (trimmed.includes("dropbox.com") && trimmed.includes("dl=0")) {
    return trimmed.replace("dl=0", "raw=1");
  }

  return trimmed;
}

/**
 * Returns an ordered array of image URLs for a product.
 * Normalises old single-image products (p.image) and new multi-image products (p.images[]),
 * while converting cloud share links (like Google Drive) into embeddable direct links.
 */
export function getProductImages(p) {
  if (!p) return [];
  let list = [];
  if (Array.isArray(p.images) && p.images.length > 0) list = p.images;
  else if (p.image) list = [p.image];
  return list.map(normalizeImageUrl);
}

/**
 * Extracts the YouTube video ID from a product's video_url.
 * Handles youtube.com/watch?v=, youtu.be/, youtube.com/shorts/.
 * Returns null if no valid video URL is set.
 */
export function getProductVideoId(p) {
  const url = p?.video_url;
  if (!url) return null;
  const m =
    url.match(/[?&]v=([^&#]+)/) ||
    url.match(/youtu\.be\/([^?&#]+)/) ||
    url.match(/\/shorts\/([^?&#]+)/);
  return m ? m[1] : null;
}


