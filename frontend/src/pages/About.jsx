import { Link } from "react-router-dom";
import { Award, Users, Wrench, Building2, ArrowRight, ShieldCheck, CheckCircle2, Factory } from "lucide-react";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BUSINESS } from "@/lib/business";

const ABOUT_IMG =
  "https://images.unsplash.com/photo-1496247749665-49cf5b1022e9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MTN8MHwxfHNlYXJjaHwyfHxtZXRhbCUyMHN0ZWVsJTIwbWFudWZhY3R1cmluZ3xlbnwwfHx8fDE3ODIyNzk0Mzh8MA&ixlib=rb-4.1.0&q=85";

const facts = [
  { label: "Established Year", value: "2006" },
  { label: "Years in Business", value: "19+ Years" },
  { label: "Nature of Business", value: "Manufacturer & Exporter" },
  { label: "Firm Structure", value: "Proprietorship" },
  { label: "Annual Turnover", value: "₹40L – ₹1.5Cr" },
  { label: "Team Size", value: "11–25 Engineers" },
  { label: "GST Registration", value: "Sep 2017 (MH)" },
  { label: "IndiaMART Rating", value: "4.0★ TrustSEAL" },
];

const values = [
  {
    icon: Wrench,
    title: "Precision Tolerances",
    desc: "We machine all platens and rollers with high-grade hardened tool steel (EN31) to maintain exact dimensional accuracy across years of continuous shifts."
  },
  {
    icon: Users,
    title: "Factory-Floor Engineered",
    desc: "We understand operator ergonomics and real factory electrical/pneumatic conditions. Every machine is simple to operate and easy to maintain."
  },
  {
    icon: ShieldCheck,
    title: "Lifetime Support & Warranty",
    desc: "Every machine comes with a 1-year comprehensive warranty, complete spare parts availability, and prompt technical support across India."
  },
  {
    icon: Building2,
    title: "100% Make In India",
    desc: "Entirely manufactured at our Khopoli facility in Maharashtra, sourcing domestic certified steel and supporting Indian industrial self-reliance."
  },
];

const QUALITY_STEPS = [
  {
    step: "01",
    title: "Certified Raw Material Inspection",
    desc: "Rigorous ultrasonic and hardness testing of alloy steels, plates, and shafts before machining."
  },
  {
    step: "02",
    title: "Precision CNC Machining & Heat Treatment",
    desc: "Moulding dies, leveler rolls, and shearing blades undergo controlled heat treatment (50–52 HRC)."
  },
  {
    step: "03",
    title: "Hydraulic & Electrical System Assembly",
    desc: "Installation of Yuken/Rexroth grade hydraulic pumps, digital PID thermostats, and Delta/Siemens PLCs."
  },
  {
    step: "04",
    title: "48-Hour Continuous Factory Stress Run",
    desc: "Every machine undergoes trial production runs with raw coil/foam stock before final dispatch."
  }
];

export default function About() {
  const breadcrumbs = [
    { name: "Home", url: BUSINESS.websiteUrl },
    { name: "About Us", url: `${BUSINESS.websiteUrl}/about` }
  ];

  return (
    <div className="bg-[#050505] min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24 text-white">
      <SEO
        title="About Our Works"
        description="Learn about Gagan Engineering Works, established in 2006 in Khopoli, Maharashtra. Manufacturer of Bra Cup Moulding Machines, Roll Formers & Decoilers."
        keywords="About Gagan Engineering Works, Industrial Machinery Khopoli, Machinery Manufacturer Maharashtra, Bra Cup Machine Factory, Gagan Engineering Estd 2006"
        canonicalUrl={`${BUSINESS.websiteUrl}/about`}
        breadcrumbs={breadcrumbs}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Breadcrumb navigation */}
        <div className="flex items-center gap-1.5 sm:gap-2 mono text-[10px] sm:text-[11px] text-white/50 mb-6 sm:mb-8 uppercase tracking-wider overflow-x-auto whitespace-nowrap pb-1">
          <Link to="/" className="hover:text-white transition-colors shrink-0">Home</Link>
          <span className="shrink-0">/</span>
          <span className="text-[#FF5722] truncate">About Our Works</span>
        </div>

        {/* Hero Section */}
        <section className="grid lg:grid-cols-2 gap-8 sm:gap-12 items-center pb-14 sm:pb-20 border-b border-white/10">
          <div className="space-y-4 sm:space-y-6">
            <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] font-semibold">
              // Khopoli Works · Estd. 2006
            </div>
            <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-white uppercase tracking-wide leading-tight">
              Forged in <span className="text-[#FF5722]">Khopoli.</span>
              <br />
              Trusted Across India.
            </h1>
            <p className="text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed font-normal">
              <strong>Gagan Engineering Works</strong> started in 2006 along the Mumbai-Pune industrial highway corridor. Over 19+ years, we have grown into one of India's most dependable manufacturers of precision bra cup moulding presses, hydraulic uncoilers, and structural roll-forming lines.
            </p>
            <p className="text-xs sm:text-sm text-white/60 leading-relaxed">
              We serve intimate wear manufacturers, roofing sheet contractors, and PEB infrastructure companies nationwide. Our machines are built with one priority: reliable, uninterrupted production day after day.
            </p>

            <div className="pt-2 flex flex-col xs:flex-row flex-wrap gap-3">
              <Link to="/contact" className="btn-primary flex items-center justify-center gap-2 w-full xs:w-auto" data-testid="about-cta">
                Visit Our Facility <ArrowRight className="w-4 h-4" />
              </Link>
              <Link to="/products" className="btn-ghost w-full xs:w-auto text-center">
                View Machines
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="aspect-[4/3] border border-white/10 rounded-xs overflow-hidden bg-[#09090B] shadow-2xl">
              <img
                src={ABOUT_IMG}
                alt="Gagan Engineering Works Factory Floor Khopoli"
                className="w-full h-full object-cover"
              />
            </div>
            {/* Floating badge — hidden on very small screens to prevent overflow */}
            <div className="absolute -bottom-5 sm:-bottom-6 -left-3 sm:-left-6 bg-[#FF5722] p-4 sm:p-6 hidden xs:block rounded-xs shadow-xl">
              <div className="font-display text-4xl sm:text-5xl text-white">19+</div>
              <div className="mono text-[9px] sm:text-[10px] tracking-[0.15em] sm:tracking-[0.2em] uppercase text-white font-semibold">
                Years Of Precision Engineering
              </div>
            </div>
          </div>
        </section>

        {/* Company Facts */}
        <section className="py-14 sm:py-20 border-b border-white/10">
          <SectionHeader
            overline="// Verified Credentials"
            title="Company Data & Registration Specs"
            description="Transparent business data reflecting 19 years of verified manufacturing in Maharashtra."
          />

          <div className="mt-8 sm:mt-12 grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-px bg-white/10 border border-white/10 rounded-xs overflow-hidden">
            {facts.map((f, idx) => (
              <div key={idx} className="bg-[#050505] p-4 sm:p-5 md:p-6 hover:bg-[#09090B] transition-colors">
                <div className="mono text-[9px] sm:text-[10px] text-[#FF5722] uppercase tracking-wider font-semibold leading-snug">
                  {f.label}
                </div>
                <div className="mt-2 font-display text-lg sm:text-xl md:text-2xl text-white uppercase tracking-wide leading-tight">
                  {f.value}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 4 Quality Steps */}
        <section className="py-14 sm:py-20 border-b border-white/10">
          <SectionHeader
            overline="// Quality Assurance"
            title="Our 4-Stage Manufacturing Protocol"
            description="How we ensure zero defects and high precision before any machine leaves our workshop."
          />

          <div className="mt-8 sm:mt-12 grid sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {QUALITY_STEPS.map((s) => (
              <div key={s.step} className="p-5 sm:p-6 bg-[#09090B] border border-white/10 rounded-xs flex flex-col justify-between">
                <div>
                  <div className="font-display text-3xl text-[#FF5722]">{s.step}</div>
                  <h3 className="text-sm sm:text-base font-semibold text-white mt-3 uppercase tracking-wide">
                    {s.title}
                  </h3>
                  <p className="text-xs text-white/60 leading-relaxed mt-2">{s.desc}</p>
                </div>
                <div className="mt-4 pt-4 border-t border-white/5 mono text-[10px] text-green-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> QA Checkpoint
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Operating Values */}
        <section className="py-14 sm:py-20">
          <SectionHeader
            overline="// Core Principles"
            title="The 4 Rules We Never Compromise"
            description="Operating values that guide our engineering design choices on the shop floor."
          />

          <div className="mt-8 sm:mt-12 grid sm:grid-cols-2 gap-4 sm:gap-6">
            {values.map((v, idx) => (
              <div key={idx} className="p-6 sm:p-8 bg-[#09090B] border border-white/10 rounded-xs hover:border-[#FF5722]/60 transition-colors">
                <div className="w-10 h-10 rounded bg-[#FF5722]/10 border border-[#FF5722]/40 flex items-center justify-center text-[#FF5722]">
                  <v.icon className="w-5 h-5" />
                </div>
                <h3 className="font-display text-xl sm:text-2xl uppercase tracking-wider text-white mt-4 sm:mt-5">
                  {v.title}
                </h3>
                <p className="text-xs sm:text-sm text-white/70 leading-relaxed mt-2">{v.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
