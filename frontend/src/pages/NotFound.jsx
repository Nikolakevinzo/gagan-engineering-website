import { Link } from "react-router-dom";
import { ArrowLeft, Factory, Search, Wrench, Phone, MessageCircle } from "lucide-react";
import SEO from "@/components/SEO";
import { BUSINESS } from "@/lib/business";
import { CATEGORIES } from "@/lib/catalogueData";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#050505] text-white pt-28 pb-16 flex items-center justify-center px-4">
      <SEO
        title="404 Page Not Found"
        description="The machinery page you are looking for may have been moved or updated. Explore our industrial machinery catalogue."
      />

      <div className="max-w-2xl w-full text-center">
        {/* Error Code & Graphic */}
        <div className="inline-flex items-center gap-2 bg-[#FF5722]/10 border border-[#FF5722]/30 px-3.5 py-1.5 rounded-sm mono text-xs tracking-widest text-[#FF5722] uppercase mb-6">
          <Factory className="w-4 h-4" />
          <span>Error 404 · Page Not Located</span>
        </div>

        <h1 className="font-display text-4xl sm:text-6xl text-white uppercase tracking-tight mb-4">
          Machine Specification <br className="hidden sm:inline" />
          <span className="text-[#FF5722]">Not Found</span>
        </h1>

        <p className="text-white/60 text-sm sm:text-base leading-relaxed max-w-lg mx-auto mb-8">
          The machinery line, technical page, or documentation link you requested may have been relocated in our updated workshop catalogue.
        </p>

        {/* Quick Actions */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-12">
          <Link
            to="/products"
            className="btn-primary inline-flex items-center gap-2 px-6 py-3"
          >
            <Wrench className="w-4 h-4" />
            <span>Browse All Machinery</span>
          </Link>
          <Link
            to="/"
            className="inline-flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/15 text-white text-sm px-6 py-3 rounded-sm transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Home</span>
          </Link>
        </div>

        {/* Machinery Categories Quick Directory */}
        <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 sm:p-8 text-left">
          <h3 className="mono text-xs uppercase tracking-widest text-white/50 mb-4 flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-[#FF5722]" />
            <span>Direct Category Access</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {CATEGORIES.filter(c => c.id !== "all").map((cat) => (
              <Link
                key={cat.id}
                to={`/products?category=${cat.id}`}
                className="bg-black/50 border border-white/10 hover:border-[#FF5722]/50 p-3.5 rounded-sm group transition-all"
              >
                <div className="text-sm font-semibold text-white group-hover:text-[#FF5722] transition-colors">
                  {cat.name}
                </div>
                <div className="mono text-[10px] text-white/40 mt-1">
                  View Machinery Line →
                </div>
              </Link>
            ))}
          </div>

          <div className="mt-6 pt-5 border-t border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs text-white/50">
            <span>Need immediate technical consultation?</span>
            <div className="flex items-center gap-3">
              <a
                href={`tel:${BUSINESS.phone}`}
                className="text-white hover:text-[#FF5722] inline-flex items-center gap-1.5 transition-colors"
              >
                <Phone className="w-3.5 h-3.5 text-[#FF5722]" />
                <span>{BUSINESS.phoneDisplay}</span>
              </a>
              <span>•</span>
              <a
                href={`https://wa.me/${BUSINESS.phoneRaw}?text=Hello%20Gagan%20Engineering,%20I%20am%20looking%20for%20a%20machine.`}
                target="_blank"
                rel="noreferrer"
                className="text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1.5 transition-colors"
              >
                <MessageCircle className="w-3.5 h-3.5" />
                <span>WhatsApp Engineer</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
