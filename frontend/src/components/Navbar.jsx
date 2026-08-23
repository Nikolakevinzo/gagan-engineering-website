import { useState, useEffect } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { Menu, X, Phone, MessageCircle, ChevronDown, Bot, Factory } from "lucide-react";
import { BUSINESS } from "@/lib/business";
import { CATEGORIES } from "@/lib/catalogueData";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [catOpen, setCatOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setOpen(false);
    setCatOpen(false);
  }, [location.pathname]);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <header
      data-testid="site-navbar"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[#050505]/95 backdrop-blur-xl border-b border-white/10 shadow-2xl py-3"
          : "bg-gradient-to-b from-black/90 via-black/50 to-transparent border-b border-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" data-testid="navbar-logo" className="flex items-center gap-3 group">
          <div className="w-12 h-10 transition-transform group-hover:scale-105 flex items-center justify-center shrink-0">
            <img
              src="/logo.png"
              alt="Gagan Engineering Works (GSK) Logo"
              className="w-full h-full object-contain"
            />
          </div>
          <div className="leading-tight min-w-0">
            <div className="font-display text-lg xs:text-xl sm:text-2xl text-white tracking-wider">
              GAGAN <span className="text-[#FF5722]">ENGINEERING</span>
            </div>
            <div className="mono text-[8px] sm:text-[10px] tracking-[0.2em] sm:tracking-[0.25em] text-white/60 uppercase hidden xs:block">
              Works · Khopoli · Estd. 2006
            </div>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-8">
          <NavLink
            to="/"
            data-testid="nav-link-home"
            className={({ isActive }) =>
              `relative text-xs tracking-[0.15em] uppercase font-semibold transition-colors ${
                isActive ? "text-[#FF5722]" : "text-white/80 hover:text-white"
              }`
            }
          >
            Home
          </NavLink>

          {/* Products with Dropdown */}
          <div
            className="relative"
            onMouseEnter={() => setCatOpen(true)}
            onMouseLeave={() => setCatOpen(false)}
          >
            <NavLink
              to="/products"
              data-testid="nav-link-products"
              className={({ isActive }) =>
                `flex items-center gap-1 text-xs tracking-[0.15em] uppercase font-semibold transition-colors ${
                  isActive ? "text-[#FF5722]" : "text-white/80 hover:text-white"
                }`
              }
            >
              Machinery <ChevronDown className="w-3.5 h-3.5" />
            </NavLink>

            {catOpen && (
              <div className="absolute top-full left-0 w-64 pt-2 z-50">
                <div className="bg-[#0A0A0C] border border-[#27272A] p-2 rounded shadow-2xl backdrop-blur-xl">
                  {CATEGORIES.map((c) => (
                    <Link
                      key={c.id}
                      to={c.id === "all" ? "/products" : `/products?category=${encodeURIComponent(c.name)}`}
                      className="block px-3 py-2.5 text-xs text-white/80 hover:text-[#FF5722] hover:bg-white/5 rounded transition-colors"
                    >
                      {c.name}
                    </Link>
                  ))}
                  <div className="border-t border-white/10 my-1 pt-1">
                    <Link
                      to="/products"
                      className="block px-3 py-2 text-[11px] mono text-[#FF5722] hover:underline"
                    >
                      View All 10 Machine Models →
                    </Link>
                  </div>
                </div>
              </div>
            )}
          </div>

          <NavLink
            to="/about"
            data-testid="nav-link-about"
            className={({ isActive }) =>
              `relative text-xs tracking-[0.15em] uppercase font-semibold transition-colors ${
                isActive ? "text-[#FF5722]" : "text-white/80 hover:text-white"
              }`
            }
          >
            About Works
          </NavLink>

          <NavLink
            to="/factory"
            data-testid="nav-link-factory"
            className={({ isActive }) =>
              `relative text-xs tracking-[0.15em] uppercase font-semibold transition-colors ${
                isActive ? "text-[#FF5722]" : "text-white/80 hover:text-white"
              }`
            }
          >
            Factory Tour
          </NavLink>

          <NavLink
            to="/blog"
            data-testid="nav-link-blog"
            className={({ isActive }) =>
              `relative text-xs tracking-[0.15em] uppercase font-semibold transition-colors ${
                isActive ? "text-[#FF5722]" : "text-white/80 hover:text-white"
              }`
            }
          >
            Knowledge Hub
          </NavLink>

          <NavLink
            to="/contact"
            data-testid="nav-link-contact"
            className={({ isActive }) =>
              `relative text-xs tracking-[0.15em] uppercase font-semibold transition-colors ${
                isActive ? "text-[#FF5722]" : "text-white/80 hover:text-white"
              }`
            }
          >
            Contact & RFQ
          </NavLink>
        </nav>

        {/* Action CTAs */}
        <div className="hidden lg:flex items-center gap-3">
          <a
            href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent("Hi Gagan Engineering Works, I would like to inquire about industrial machinery.")}`}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="navbar-whatsapp-btn"
            className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider bg-green-600/20 hover:bg-green-600 text-green-400 hover:text-white border border-green-500/40 px-3.5 py-2 rounded-sm transition-all"
          >
            <MessageCircle className="w-4 h-4" /> WhatsApp
          </a>

          <a
            href={`tel:${BUSINESS.phone}`}
            data-testid="navbar-call-btn"
            className="btn-primary flex items-center gap-2 text-xs py-2 px-4"
          >
            <Phone className="w-3.5 h-3.5" /> {BUSINESS.phoneDisplay}
          </a>
        </div>

        {/* Mobile Toggle */}
        <button
          className="lg:hidden text-white p-2"
          onClick={() => setOpen(!open)}
          data-testid="navbar-mobile-toggle"
          aria-label="Toggle Menu"
        >
          {open ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Slide-down Menu */}
      {open && (
        <div
          data-testid="navbar-mobile-menu"
          className="lg:hidden bg-[#0A0A0C]/98 backdrop-blur-2xl border-b border-white/10 px-6 py-6 space-y-5 animate-in fade-in slide-in-from-top-3 duration-200"
        >
          <div className="flex flex-col gap-4">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `text-base tracking-wider uppercase font-semibold ${isActive ? "text-[#FF5722]" : "text-white/80"}`
              }
            >
              Home
            </NavLink>
            <NavLink
              to="/products"
              className={({ isActive }) =>
                `text-base tracking-wider uppercase font-semibold ${isActive ? "text-[#FF5722]" : "text-white/80"}`
              }
            >
              Machinery Catalogue (10 Models)
            </NavLink>
            <NavLink
              to="/about"
              className={({ isActive }) =>
                `text-base tracking-wider uppercase font-semibold ${isActive ? "text-[#FF5722]" : "text-white/80"}`
              }
            >
              About Khopoli Works
            </NavLink>
            <NavLink
              to="/factory"
              className={({ isActive }) =>
                `text-base tracking-wider uppercase font-semibold ${isActive ? "text-[#FF5722]" : "text-white/80"}`
              }
            >
              Factory Tour & Workshop
            </NavLink>
            <NavLink
              to="/blog"
              className={({ isActive }) =>
                `text-base tracking-wider uppercase font-semibold ${isActive ? "text-[#FF5722]" : "text-white/80"}`
              }
            >
              Knowledge Hub & Guides
            </NavLink>
            <NavLink
              to="/contact"
              className={({ isActive }) =>
                `text-base tracking-wider uppercase font-semibold ${isActive ? "text-[#FF5722]" : "text-white/80"}`
              }
            >
              Contact & Request Quotation
            </NavLink>
          </div>


          <div className="pt-4 border-t border-white/10 flex flex-col gap-3">
            <a
              href={`tel:${BUSINESS.phone}`}
              className="btn-primary w-full text-center flex items-center justify-center gap-2"
            >
              <Phone className="w-4 h-4" /> Call {BUSINESS.phoneDisplay}
            </a>
            <a
              href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent("Hi Gagan Engineering Works, I would like to inquire about industrial machinery.")}`}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full text-center flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white py-2.5 px-4 font-semibold text-xs tracking-wider uppercase rounded-sm transition-colors"
            >
              <MessageCircle className="w-4 h-4" /> Chat on WhatsApp
            </a>
          </div>

          <div className="mono text-[11px] text-white/50 space-y-1 pt-2">
            <div>📍 Khopoli, Maharashtra 410203</div>
            <div>✉️ {BUSINESS.email}</div>
          </div>

          <div className="pt-2 border-t border-white/5">
            <Link to="/admin" className="mono text-[10px] text-white/20 hover:text-white/50 transition-colors">
              Admin Panel →
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
