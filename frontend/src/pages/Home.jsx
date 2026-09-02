import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, ShieldCheck, Cog, Factory, Star, CheckCircle2, Phone, MessageCircle, ChevronDown, Bot, Sparkles, Layers, Cpu, Wrench } from "lucide-react";
import SEO from "@/components/SEO";
import ProductCard from "@/components/ProductCard";
import SectionHeader from "@/components/SectionHeader";
import { BUSINESS, GLOBAL_FAQS } from "@/lib/business";
import { CATALOGUE_PRODUCTS, getLiveCatalogueProducts } from "@/lib/catalogueData";
import { api } from "@/lib/api";

const HERO_BG = "/hero-bg.jpg";

const stats = [
  { value: "19+", label: "Years Engineering Experience" },
  { value: "8+", label: "Industrial Machine Lines" },
  { value: "500+", label: "Machines Operating in India" },
  { value: "4.0★", label: "IndiaMART Verified Rating" },
];

const capabilities = [
  {
    icon: Cog,
    title: "Custom Machine Engineering",
    desc: "Machines precision-built to your factory's exact sheet thickness, cycle speed, and platen sizes."
  },
  {
    icon: ShieldCheck,
    title: "Heavy Hardened Steel Platens",
    desc: "Built with EN31 tool steel rollers and hardened platen assemblies for decades of 24/7 industrial duty."
  },
  {
    icon: Factory,
    title: "Pan-India On-Site Commissioning",
    desc: "Full installation, operator training, 1-year comprehensive warranty, and ready spare parts supply."
  },
];

const INDUSTRIES = [
  { id: "all", name: "All Machinery" },
  { id: "roll-forming-sheet-metal", name: "Roofing & Roll Forming", icon: Wrench },
  { id: "cut-to-length-line", name: "Coil Processing & CTL Lines", icon: Cpu },
  { id: "bra-cup-moulding-machine", name: "Lingerie & Bra Cup Moulding", icon: Layers }
];

export default function Home() {
  const [products, setProducts] = useState(getLiveCatalogueProducts);
  const [featured, setFeatured] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState("all");
  const [openFaq, setOpenFaq] = useState(null);

  useEffect(() => {
    // Helper: merge array of products with overrides (later wins)
    const mergeProducts = (base, overrides) => {
      const merged = [...base];
      overrides.forEach((item) => {
        const idx = merged.findIndex((m) => m.id === item.id);
        if (idx >= 0) {
          merged[idx] = { ...merged[idx], ...item };
        } else {
          merged.push(item);
        }
      });
      return merged;
    };

    api
      .get("/products")
      .then((r) => {
        let combined = getLiveCatalogueProducts();
        if (r.data && r.data.products && r.data.products.length > 0) {
          combined = mergeProducts(combined, r.data.products);
        }
        try {
          const localProducts = JSON.parse(localStorage.getItem("gagan_custom_products") || "[]");
          if (localProducts.length > 0) {
            combined = mergeProducts(combined, localProducts);
          }
        } catch (e) {}
        setProducts(combined);
        setFeatured(combined.filter((p) => p.featured));
      })
      .catch(() => {
        const live = getLiveCatalogueProducts();
        setProducts(live);
        setFeatured(live.filter((p) => p.featured));
      });
  }, []);

  const filteredCatalog =
    selectedIndustry === "all"
      ? products
      : products.filter((p) => p.categorySlug === selectedIndustry);

  return (
    <div className="bg-[#050505] text-white min-h-screen">
      <SEO
        title="Industrial Machinery Manufacturer & Exporter | Khopoli India"
        description="Premier Indian manufacturer & exporter of Bra Cup Moulding Machines, 10 Ton Hydraulic Decoilers, C/Z Purlin Roll Forming Machines, Automatic Cut-To-Length Lines, and Roofing Sheet Machinery. 19+ years precision engineering from Khopoli, Maharashtra. Pan-India & worldwide export."
        keywords="Industrial Machinery Manufacturer India, Bra Cup Moulding Machine Manufacturer, Roll Forming Machine India, 10 Ton Hydraulic Decoiler, Automatic Cut To Length Machine, C Z Purlin Machine, Roofing Sheet Crimping Machine, Gagan Engineering Works Khopoli Maharashtra"
        faqData={GLOBAL_FAQS}
        breadcrumbs={[{ name: "Home", url: BUSINESS.websiteUrl }]}
      />

      {/* HERO SECTION */}
      <section className="relative min-h-[92vh] sm:min-h-[95vh] flex items-center overflow-hidden border-b border-white/10 pt-20 sm:pt-24 pb-12 sm:pb-16" data-testid="hero-section">
        {/* Responsive Background Image */}
        <div className="absolute inset-0 overflow-hidden">
          <img
            src={HERO_BG}
            alt="Gagan Engineering Works Khopoli Industrial Machinery"
            className="w-full h-full object-cover object-[center_right] sm:object-[60%_center] lg:object-[70%_center] opacity-65 sm:opacity-80 scale-100 sm:scale-105 transition-transform duration-700"
          />
        </div>
        {/* Directional gradient overlays for readability */}
        <div className="absolute inset-0 bg-gradient-to-t sm:bg-gradient-to-r from-[#050505] via-[#050505]/90 sm:via-[#050505]/75 to-[#050505]/50 sm:to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-[#050505]/80 via-transparent to-[#050505]" />
        <div className="absolute inset-0 grid-bg opacity-20 pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 w-full">
          <div className="max-w-3xl">
            {/* Trust Badge */}
            <div className="inline-flex items-center gap-2 bg-[#FF5722]/10 border border-[#FF5722]/40 px-3 py-1.5 rounded-xs mono text-[10px] sm:text-[11px] tracking-[0.15em] sm:tracking-[0.2em] uppercase text-[#FF5722] mb-5 sm:mb-6">
              <span className="w-2 h-2 rounded-full bg-[#FF5722] animate-pulse flex-shrink-0" />
              <span>Khopoli, Maharashtra · Estd. 2006 · 19+ Years</span>
            </div>

            {/* Main Headline */}
            <h1 className="font-display text-4xl xs:text-5xl sm:text-6xl md:text-7xl lg:text-8xl text-white tracking-wide uppercase leading-[0.95]">
              HEAVY <span className="text-[#FF5722]">MACHINERY.</span>
              <br />
              PRECISION BUILT.
            </h1>

            {/* Subtitle */}
            <p className="mt-5 sm:mt-6 text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed max-w-2xl font-normal">
              Trusted Indian manufacturer of <strong>10-Ton Hydraulic Decoilers</strong>, <strong>Automatic Cut-to-Length Lines</strong>, <strong>C/Z Purlin Roll Formers</strong>, and <strong>Bra Cup Moulding Presses</strong> engineered for continuous 24/7 factory output.
            </p>

            {/* Key USPs */}
            <div className="mt-5 sm:mt-6 flex flex-wrap gap-2 sm:gap-4 text-xs mono text-white/70">
              <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 px-2.5 sm:px-3 py-1.5 rounded-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-green-400 shrink-0" /> 1-Year Comprehensive Warranty
              </div>
              <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 px-2.5 sm:px-3 py-1.5 rounded-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-green-400 shrink-0" /> Pan-India & Global Commissioning
              </div>
              <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 px-2.5 sm:px-3 py-1.5 rounded-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-sky-400 shrink-0" /> Worldwide Exports (JNPT Mumbai Port)
              </div>
            </div>

            {/* Hero CTAs */}
            <div className="mt-8 sm:mt-10 flex flex-col xs:flex-row flex-wrap items-start xs:items-center gap-3 sm:gap-4">
              <Link to="/products" className="btn-primary flex items-center gap-2 w-full xs:w-auto justify-center" data-testid="hero-cta-products">
                Explore 10 Machinery Lines <ArrowRight className="w-4 h-4" />
              </Link>
              <Link to="/contact" className="btn-ghost flex items-center gap-2 w-full xs:w-auto justify-center" data-testid="hero-cta-quote">
                Request Price Quotation
              </Link>
              <a
                href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent("Hi Gagan Engineering Works, I would like to inquire about your machinery catalogue.")}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 bg-green-600/20 hover:bg-green-600 text-green-400 hover:text-white border border-green-500/40 px-4 py-3 text-xs font-semibold uppercase tracking-wider rounded-xs transition-all w-full xs:w-auto"
              >
                <MessageCircle className="w-4 h-4" /> WhatsApp Quote
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* STATS STRIP */}
      <section className="border-b border-white/10 bg-[#08080A]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 grid grid-cols-2 md:grid-cols-4 divide-y md:divide-y-0 divide-x divide-white/10">
          {stats.map((s, idx) => (
            <div key={idx} className={`py-6 sm:py-8 px-4 sm:px-6 ${idx % 2 === 0 && idx < 2 ? "border-r border-white/10 md:border-r-0 md:border-l border-white/10" : ""} ${idx >= 2 ? "md:border-l border-white/10" : ""}`}>
              <div className="font-display text-3xl sm:text-4xl md:text-5xl text-[#FF5722] tracking-wider">
                {s.value}
              </div>
              <div className="mono text-[9px] sm:text-[11px] tracking-[0.15em] sm:tracking-[0.2em] uppercase text-white/60 mt-1">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* INTERACTIVE MACHINERY SELECTOR */}
      <section className="py-14 sm:py-20 bg-[#050505] border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 sm:gap-6 mb-8 sm:mb-12">
            <SectionHeader
              overline="// Production Line Finder"
              title="Select Your Manufacturing Application"
              description="Choose your industry sector below to filter our high-performance machinery catalogue."
            />
            <Link to="/products" className="btn-ghost shrink-0 flex items-center gap-2 self-start md:self-auto">
              Browse All 10 Models <ArrowRight className="w-4 h-4" />
            </Link>
          </div>


          {/* Industry Filter — horizontally scrollable on mobile */}
          <div className="flex gap-2 sm:gap-2.5 mb-8 sm:mb-10 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0 sm:flex-wrap">
            {INDUSTRIES.map((ind) => {
              const Icon = ind.icon;
              return (
                <button
                  key={ind.id}
                  onClick={() => setSelectedIndustry(ind.id)}
                  className={`flex items-center gap-2 mono text-xs uppercase tracking-wider px-3 sm:px-4 py-2 sm:py-2.5 rounded-xs border transition-all whitespace-nowrap flex-shrink-0 ${
                    selectedIndustry === ind.id
                      ? "bg-[#FF5722] border-[#FF5722] text-white font-bold shadow-lg"
                      : "bg-[#0A0A0C] border-white/15 text-white/70 hover:border-[#FF5722] hover:text-white"
                  }`}
                >
                  {Icon && <Icon className="w-3.5 h-3.5" />}
                  {ind.name}
                </button>
              );
            })}
          </div>

          {/* Dynamic Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {filteredCatalog.map((p, idx) => (
              <ProductCard key={p.id} product={p} index={idx} />
            ))}
          </div>
        </div>
      </section>

      {/* MANUFACTURING CAPABILITIES */}
      <section className="py-16 sm:py-24 bg-[#08080A] border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
          <SectionHeader
            overline="// Engineering Standards"
            title="Built For Non-Stop Industrial Duty"
            description="Every machine leaving our Khopoli workshop is engineered with heavy steel frames and strict calibration standards."
          />

          <div className="mt-10 sm:mt-14 grid md:grid-cols-3 gap-px bg-white/10 border border-white/10 rounded-xs overflow-hidden">
            {capabilities.map((c, idx) => (
              <div
                key={idx}
                className="bg-[#050505] p-6 sm:p-8 lg:p-10 hover:bg-[#0C0C0E] transition-colors flex flex-col justify-between"
              >
                <div>
                  <div className="w-11 h-11 sm:w-12 sm:h-12 rounded-xs bg-[#FF5722]/10 border border-[#FF5722]/40 flex items-center justify-center text-[#FF5722]">
                    <c.icon className="w-5 h-5 sm:w-6 sm:h-6" />
                  </div>
                  <h3 className="font-display text-xl sm:text-2xl tracking-wide uppercase text-white mt-5 sm:mt-6">
                    {c.title}
                  </h3>
                  <p className="text-white/60 mt-2 sm:mt-3 text-sm leading-relaxed">
                    {c.desc}
                  </p>
                </div>
                <div className="mt-5 sm:mt-6 mono text-[10px] tracking-[0.2em] text-[#FF5722] uppercase">
                  Quality Guaranteed ──
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* MARQUEE */}
      <section className="py-4 sm:py-5 bg-[#FF5722] overflow-hidden border-y border-[#E64A19]">
        <div className="marquee-track flex gap-8 sm:gap-12 whitespace-nowrap font-display text-xl sm:text-2xl md:text-3xl tracking-wider uppercase text-white font-bold">
          <span>★ 10-TON HYDRAULIC DECOILERS</span>
          <span>★ AUTOMATIC CUT-TO-LENGTH LINES</span>
          <span>★ C & Z PURLIN ROLL FORMERS</span>
          <span>★ ROOFING SHEET CRIMPING</span>
          <span>★ BRA CUP MOULDING MACHINES</span>
          <span>★ KHOPOLI WORKS · SINCE 2006</span>
          <span>★ 10-TON HYDRAULIC DECOILERS</span>
          <span>★ AUTOMATIC CUT-TO-LENGTH LINES</span>
        </div>
      </section>

      {/* FAQS */}
      <section className="py-16 sm:py-24 bg-[#050505] border-b border-white/10" id="faqs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
          <SectionHeader
            overline="// Machinery Buyers FAQ"
            title="Frequently Asked Questions"
            description="Answers to common technical, logistics, and warranty questions from factory owners and production managers."
          />

          <div className="mt-10 sm:mt-12 max-w-4xl space-y-3">
            {GLOBAL_FAQS.map((faq, idx) => {
              const isOpen = openFaq === idx;
              return (
                <div
                  key={idx}
                  className="border border-white/10 bg-[#09090B] rounded-xs overflow-hidden"
                >
                  <button
                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                    className="w-full text-left p-4 sm:p-5 md:p-6 flex items-start sm:items-center justify-between gap-3 sm:gap-4 hover:text-[#FF5722] transition-colors"
                  >
                    <span className="font-medium text-sm sm:text-base lg:text-lg text-white text-left">
                      {faq.q}
                    </span>
                    <ChevronDown
                      className={`w-5 h-5 text-[#FF5722] transition-transform duration-200 shrink-0 mt-0.5 sm:mt-0 ${
                        isOpen ? "rotate-180" : ""
                      }`}
                    />
                  </button>
                  {isOpen && (
                    <div className="px-4 sm:px-5 md:px-6 pb-4 sm:pb-5 md:pb-6 text-white/70 text-sm leading-relaxed border-t border-white/5 bg-black/40 pt-4">
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="py-16 sm:py-20 bg-gradient-to-b from-[#0A0A0C] to-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 text-center">
          <div className="inline-block mono text-xs tracking-[0.25em] uppercase text-[#FF5722] mb-4">
            ── Start Your Production Line
          </div>
          <h2 className="font-display text-3xl sm:text-4xl md:text-5xl lg:text-6xl text-white tracking-wide uppercase max-w-3xl mx-auto leading-tight">
            Ready to upgrade your factory's machinery?
          </h2>
          <p className="mt-4 text-white/60 max-w-xl mx-auto text-sm sm:text-base leading-relaxed">
            Contact our engineering team in Khopoli for machine configurations, layout drawings, and transparent price quotations.
          </p>

          <div className="mt-8 sm:mt-10 flex flex-col xs:flex-row flex-wrap justify-center items-center gap-3 sm:gap-4">
            <Link to="/contact" className="btn-primary w-full xs:w-auto justify-center">
              Request a Quotation (RFQ)
            </Link>
            <a
              href={`tel:${BUSINESS.phone}`}
              className="btn-ghost flex items-center justify-center gap-2 w-full xs:w-auto"
            >
              <Phone className="w-4 h-4" /> Call: {BUSINESS.phoneDisplay}
            </a>
            <a
              href={`https://wa.me/${BUSINESS.phoneRaw}`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 hover:bg-green-500 text-white font-semibold text-xs uppercase tracking-wider py-3 sm:py-3.5 px-5 sm:px-6 rounded-xs transition-colors flex items-center justify-center gap-2 w-full xs:w-auto"
            >
              <MessageCircle className="w-4 h-4" /> Chat on WhatsApp
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
