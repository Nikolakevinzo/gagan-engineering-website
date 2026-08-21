import { Link } from "react-router-dom";
import { Phone, Mail, MapPin, MessageCircle, ExternalLink, ShieldCheck, Award } from "lucide-react";
import { BUSINESS } from "@/lib/business";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";

export default function Footer() {
  return (
    <footer className="bg-[#030304] border-t border-white/10 text-white/70 pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-white/10">
          {/* Col 1 & 2: Company Overview */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-10 flex items-center justify-center shrink-0">
                <img
                  src="/logo.png"
                  alt="Gagan Engineering Works (GSK) Logo"
                  className="w-full h-full object-contain"
                />
              </div>
              <div>
                <div className="font-display text-2xl text-white tracking-wider">
                  GAGAN <span className="text-[#FF5722]">ENGINEERING WORKS</span>
                </div>
                <div className="mono text-[10px] text-white/50 tracking-[0.25em] uppercase">
                  Precision Industrial Machinery · Since 2006
                </div>
              </div>
            </div>

            <p className="text-sm text-white/60 leading-relaxed max-w-md">
              Established in 2006 in Khopoli, Maharashtra, Gagan Engineering Works is a leading manufacturer of high-performance Bra Cup Moulding Presses, Hydraulic Decoilers, C/Z Purlin Roll Formers, and Cut-To-Length Lines.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              <a
                href={BUSINESS.indiamartUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 bg-[#0e1e24] border border-[#1b3d4a] text-sky-400 text-xs px-3 py-1.5 rounded-sm hover:border-sky-400 transition-colors"
              >
                <Award className="w-3.5 h-3.5" /> IndiaMART TrustSEAL Verified (4.0★)
              </a>
              <span className="mono text-[11px] text-white/40 bg-zinc-900 px-2.5 py-1 border border-zinc-800 rounded-sm">
                GST Registered
              </span>
            </div>
          </div>

          {/* Col 3: Machinery Products (SEO Links) */}
          <div className="space-y-3">
            <div className="mono text-xs tracking-[0.2em] uppercase text-[#FF5722] font-semibold">
              Machinery Lines
            </div>
            <ul className="space-y-2 text-xs">
              {CATALOGUE_PRODUCTS.slice(0, 6).map((p) => (
                <li key={p.id}>
                  <Link
                    to={`/products/${p.id}`}
                    className="hover:text-[#FF5722] transition-colors line-clamp-1"
                  >
                    {p.name}
                  </Link>
                </li>
              ))}
              <li>
                <Link to="/products" className="text-[#FF5722] hover:underline font-mono">
                  + View All Machinery →
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: Quick Links & SEO */}
          <div className="space-y-3">
            <div className="mono text-xs tracking-[0.2em] uppercase text-[#FF5722] font-semibold">
              Company
            </div>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/" className="hover:text-[#FF5722] transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/products" className="hover:text-[#FF5722] transition-colors">
                  Product Catalogue
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-[#FF5722] transition-colors">
                  About Our Khopoli Works
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-[#FF5722] transition-colors">
                  Request a Quotation (RFQ)
                </Link>
              </li>
              <li>
                <a href="/sitemap.xml" target="_blank" className="hover:text-[#FF5722] transition-colors mono">
                  XML Sitemap
                </a>
              </li>
              <li>
                <a href="/llms.txt" target="_blank" className="hover:text-[#FF5722] transition-colors mono">
                  LLM / AI Search Manifest (llms.txt)
                </a>
              </li>
            </ul>
          </div>

          {/* Col 5: Contact Info */}
          <div className="space-y-3">
            <div className="mono text-xs tracking-[0.2em] uppercase text-[#FF5722] font-semibold">
              Factory & Works
            </div>
            <div className="space-y-2.5 text-xs">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-[#FF5722] shrink-0 mt-0.5" />
                <span className="leading-snug">{BUSINESS.address}</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-[#FF5722] shrink-0" />
                <a href={`tel:${BUSINESS.phone}`} className="hover:text-white transition-colors">
                  {BUSINESS.phoneDisplay}
                </a>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-[#FF5722] shrink-0" />
                <a href={`mailto:${BUSINESS.email}`} className="hover:text-white transition-colors">
                  {BUSINESS.email}
                </a>
              </div>
              <div className="flex items-center gap-2">
                <MessageCircle className="w-4 h-4 text-green-500 shrink-0" />
                <a
                  href={`https://wa.me/${BUSINESS.phoneRaw}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-green-400 transition-colors"
                >
                  Direct WhatsApp Chat
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Strip */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/40">
          <div>
            © {new Date().getFullYear()} {BUSINESS.name}. All Rights Reserved. Manufactured in Khopoli, India.
          </div>
          <div className="flex items-center gap-6 mono text-[11px]">
            <span>🇮🇳 Make In India</span>
            <span>19+ Years Engineering</span>
            <span>Pan-India Dispatch</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
