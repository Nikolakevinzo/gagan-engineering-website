import { useState } from "react";
import { Link } from "react-router-dom";
import { Factory, ShieldCheck, CheckCircle2, Video, ArrowRight, Phone, MessageCircle, Wrench, Cpu, Award, MapPin } from "lucide-react";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BUSINESS } from "@/lib/business";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";

const WORKSHOP_STATIONS = [
  {
    title: "Heavy Machining & Turning Bay",
    description: "Equipped with heavy lathe machines and horizontal boring setups for precision machining of solid EN8/EN9 shafts and EN31 tool steel rollers.",
    specs: ["EN31 Hardened Alloy Steel (50–52 HRC)", "Tolerance: ±0.02 mm on Bearing Journals", "100% Ultrasonic Flaw Inspection"]
  },
  {
    title: "Hydraulic Power Pack Assembly",
    description: "Dedicated testing bench for assembling hydraulic power packs, integrating Yuken/Rexroth compatible directional valves, pressure relief valves, and 60–100L oil reservoirs.",
    specs: ["Operating Pressure: Up to 210 bar", "Dual-Stage Gear & Vane Pumps", "Zero-Leak Pilot Check Valves"]
  },
  {
    title: "Electrical & PLC Automation Panel Wiring",
    description: "Cleanroom electrical wiring station where Delta, Siemens, and Schneider PLCs, VFD frequency inverters, and digital PID temperature modules are custom wired for global voltages.",
    specs: ["Voltage Multi-Grid: 220V–480V (50/60Hz)", "Delta / Siemens Touchscreen HMIs", "IP55 Dust-Resistant Control Enclosures"]
  },
  {
    title: "48-Hour Continuous Production Stress Run",
    description: "Before factory dispatch, every machine undergoes active mechanical stress testing with actual raw coil or foam stock to verify thermal stability, shearing precision, and cycle repeats.",
    specs: ["48-Hour Continuous Test Run", "Optical Encoder Length Validation", "Factory Acceptance Test (FAT) Sign-off"]
  }
];

export default function FactoryTour() {
  const [activeVideo, setActiveVideo] = useState(0);

  const breadcrumbs = [
    { name: "Home", url: BUSINESS.websiteUrl },
    { name: "Factory Tour & Workshop", url: `${BUSINESS.websiteUrl}/factory` }
  ];

  return (
    <div className="bg-[#050505] min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24 text-white">
      <SEO
        title="Factory Tour & Workshop Infrastructure"
        description="Explore the Gagan Engineering Works manufacturing facility in Khopoli, Maharashtra. 100% in-house CNC machining, hydraulic power pack assembly, and quality inspection protocols."
        keywords="Gagan Engineering Factory Khopoli, Machinery Workshop Maharashtra, Industrial Machine Assembly, Factory Acceptance Testing India"
        canonicalUrl={`${BUSINESS.websiteUrl}/factory`}
        breadcrumbs={breadcrumbs}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Breadcrumb */}
        <div className="flex items-center gap-1.5 sm:gap-2 mono text-[10px] sm:text-[11px] text-white/50 mb-6 sm:mb-8 uppercase tracking-wider">
          <Link to="/" className="hover:text-white transition-colors">Home</Link>
          <span>/</span>
          <span className="text-[#FF5722]">Factory Tour & Workshop</span>
        </div>

        {/* Section Header */}
        <SectionHeader
          as="h1"
          overline="// Khopoli Manufacturing Works"
          title="Inside Our Heavy Machinery Facility"
          description="A look at our precision machining bays, hydraulic power pack integration, electrical control wiring, and quality inspection protocols along the Mumbai-Pune industrial corridor."
        />

        {/* Hero Workshop Overview */}
        <div className="mt-8 sm:mt-12 grid lg:grid-cols-12 gap-8 lg:gap-12 items-center bg-[#09090B] border border-white/10 p-6 sm:p-8 lg:p-12 rounded-xs shadow-2xl">
          <div className="lg:col-span-7 space-y-4 sm:space-y-6">
            <div className="inline-flex items-center gap-2 bg-[#FF5722]/10 border border-[#FF5722]/40 px-3 py-1 rounded-xs mono text-[10px] sm:text-xs uppercase tracking-widest text-[#FF5722]">
              <Factory className="w-3.5 h-3.5" />
              <span>Estd. 2006 · 19+ Years In-House Manufacturing</span>
            </div>

            <h2 className="font-display text-3xl sm:text-4xl text-white uppercase tracking-wide leading-tight">
              100% In-House Engineering & Quality Control
            </h2>

            <p className="text-white/70 text-sm sm:text-base leading-relaxed font-normal">
              Located strategically on the Mumbai-Pune Highway, our Khopoli workshop is engineered for heavy machine assembly. From turning high-tensile EN31 roller banks to assembling high-pressure hydraulic manifolds, every critical process is handled in-house to guarantee tight tolerances and decades of 24/7 industrial service.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 mono text-xs">
              <div className="bg-black/40 border border-white/10 p-3 rounded-xs text-center">
                <div className="font-display text-xl text-[#FF5722]">65 km</div>
                <div className="text-[10px] text-white/50 uppercase mt-0.5">To JNPT Sea Port</div>
              </div>
              <div className="bg-black/40 border border-white/10 p-3 rounded-xs text-center">
                <div className="font-display text-xl text-white">100%</div>
                <div className="text-[10px] text-white/50 uppercase mt-0.5">In-House Machining</div>
              </div>
              <div className="bg-black/40 border border-white/10 p-3 rounded-xs text-center col-span-2 sm:col-span-1">
                <div className="font-display text-xl text-emerald-400">48-Hr</div>
                <div className="text-[10px] text-white/50 uppercase mt-0.5">Stress Testing</div>
              </div>
            </div>

            <div className="pt-2 flex flex-wrap gap-3">
              <Link to="/contact" className="btn-primary">
                Schedule a Factory Visit <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href={`tel:${BUSINESS.phone}`}
                className="btn-ghost"
              >
                <Phone className="w-4 h-4 text-[#FF5722]" /> Call Works: {BUSINESS.phoneDisplay}
              </a>
            </div>
          </div>

          <div className="lg:col-span-5 space-y-3">
            <div className="aspect-[4/3] bg-[#0c0c0e] border border-white/10 rounded-xs overflow-hidden shadow-2xl">
              <img
                src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?crop=entropy&cs=srgb&fm=jpg&q=85"
                alt="Precision CNC Machining at Gagan Engineering Works"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="mono text-[10px] text-white/40 text-center">
              Heavy CNC turning and roller machining bay at Khopoli works.
            </div>
          </div>
        </div>

        {/* 4 Manufacturing Bays */}
        <div className="mt-16 sm:mt-20">
          <SectionHeader
            overline="// Workshop Infrastructure"
            title="4 Specialized Manufacturing Bays"
            description="How raw alloy steel is transformed into fully synchronized automated production lines."
          />

          <div className="mt-8 sm:mt-12 grid sm:grid-cols-2 gap-6">
            {WORKSHOP_STATIONS.map((station, idx) => (
              <div
                key={idx}
                className="bg-[#09090B] border border-white/10 hover:border-[#FF5722]/50 p-6 sm:p-8 rounded-xs space-y-4 transition-all shadow-xl"
              >
                <div className="flex items-center justify-between">
                  <span className="mono text-xs text-[#FF5722] font-semibold">Bay 0{idx + 1}</span>
                  <span className="mono text-[10px] text-white/40 uppercase">Khopoli Works</span>
                </div>

                <h3 className="font-display text-xl sm:text-2xl text-white uppercase tracking-wider">
                  {station.title}
                </h3>

                <p className="text-white/70 text-xs sm:text-sm leading-relaxed">
                  {station.description}
                </p>

                <div className="pt-2 border-t border-white/5 space-y-1.5">
                  {station.specs.map((sp, sidx) => (
                    <div key={sidx} className="flex items-center gap-2 text-xs mono text-white/60">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{sp}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Video Demonstration Showcase */}
        <div className="mt-16 sm:mt-20 bg-[#09090B] border border-white/10 p-6 sm:p-10 rounded-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <SectionHeader
              overline="// Live Demonstrations"
              title="Machinery in Production Operation"
              description="Observe our bra cup presses, cut to length lines, and roll formers operating under continuous factory loads."
            />
            <Link to="/products" className="btn-ghost shrink-0">
              Browse All 10 Models →
            </Link>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 pt-4">
            {CATALOGUE_PRODUCTS.slice(0, 3).map((p) => (
              <div key={p.id} className="bg-black/60 border border-white/10 rounded-xs overflow-hidden group">
                <div className="aspect-[16/10] bg-[#0c0c0e] relative overflow-hidden flex items-center justify-center p-4">
                  <img
                    src={p.image}
                    alt={p.name}
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Link
                      to={`/products/${p.id}`}
                      className="bg-[#FF5722] text-white p-3 rounded-full shadow-2xl"
                    >
                      <Video className="w-5 h-5" />
                    </Link>
                  </div>
                </div>
                <div className="p-4 space-y-2">
                  <div className="mono text-[10px] text-[#FF5722] uppercase">{p.category}</div>
                  <h4 className="font-semibold text-sm text-white line-clamp-1">{p.name}</h4>
                  <Link
                    to={`/products/${p.id}`}
                    className="text-xs text-white/50 hover:text-[#FF5722] mono inline-flex items-center gap-1 transition-colors"
                  >
                    View Specs & Video Demo →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Factory Visit Appointment Banner */}
        <div className="mt-16 sm:mt-20 bg-gradient-to-br from-[#0c1418] via-[#09090B] to-[#070709] border border-sky-500/30 p-8 sm:p-12 rounded-xs shadow-2xl grid lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-8 space-y-4">
            <div className="inline-flex items-center gap-2 bg-sky-500/10 border border-sky-500/40 px-3 py-1 rounded-xs mono text-[10px] uppercase tracking-widest text-sky-400">
              <MapPin className="w-3.5 h-3.5" />
              <span>Khopoli, Maharashtra · 9:00 AM – 7:30 PM (Mon–Sat)</span>
            </div>
            <h3 className="font-display text-3xl sm:text-4xl text-white uppercase tracking-wide">
              Schedule an On-Site Factory Trial & Inspection
            </h3>
            <p className="text-white/70 text-sm leading-relaxed">
              We welcome factory owners, plant managers, and international procurement teams to visit our Khopoli facility for live machine demonstrations, raw material trial presses, and custom tooling consultations.
            </p>
          </div>

          <div className="lg:col-span-4 flex flex-col gap-3">
            <Link to="/contact" className="btn-primary text-center">
              Book Factory Appointment
            </Link>
            <a
              href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent("Hello Gagan Engineering, I would like to schedule a factory visit to your Khopoli works.")}`}
              target="_blank"
              rel="noreferrer"
              className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold uppercase tracking-wider px-4 py-3 rounded-xs text-center transition-colors flex items-center justify-center gap-2"
            >
              <MessageCircle className="w-4 h-4" /> WhatsApp Works Manager
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
