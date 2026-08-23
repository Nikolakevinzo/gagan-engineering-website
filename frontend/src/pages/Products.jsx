import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Search, MessageCircle, ArrowRight, Filter } from "lucide-react";
import SEO from "@/components/SEO";
import ProductCard from "@/components/ProductCard";
import SectionHeader from "@/components/SectionHeader";
import { CATALOGUE_PRODUCTS, CATEGORIES } from "@/lib/catalogueData";
import { BUSINESS } from "@/lib/business";
import { api } from "@/lib/api";

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryParam = searchParams.get("category") || "All";

  const [products, setProducts] = useState(CATALOGUE_PRODUCTS);
  const [activeCategory, setActiveCategory] = useState(categoryParam);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);

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
        let combined = [...CATALOGUE_PRODUCTS];
        // 1. Merge DB products (DB wins over catalogue)
        if (r.data && r.data.products && r.data.products.length > 0) {
          combined = mergeProducts(combined, r.data.products);
        }
        // 2. Merge localStorage admin edits (local wins over DB for instant updates)
        try {
          const localProducts = JSON.parse(localStorage.getItem("gagan_custom_products") || "[]");
          if (localProducts.length > 0) {
            combined = mergeProducts(combined, localProducts);
          }
        } catch (e) {}
        setProducts(combined);
      })
      .catch(() => {
        // API offline: use catalogue + localStorage fallback
        let combined = [...CATALOGUE_PRODUCTS];
        try {
          const localProducts = JSON.parse(localStorage.getItem("gagan_custom_products") || "[]");
          if (localProducts.length > 0) {
            combined = mergeProducts(combined, localProducts);
          }
        } catch (e) {}
        setProducts(combined);
      });
  }, []);

  useEffect(() => {
    if (categoryParam) {
      setActiveCategory(categoryParam);
    }
  }, [categoryParam]);

  const handleCategorySelect = (name) => {
    setActiveCategory(name);
    const newParams = new URLSearchParams(searchParams);
    if (name === "All") {
      newParams.delete("category");
    } else {
      newParams.set("category", name);
    }
    setSearchParams(newParams);
  };

  const filteredProducts = products.filter((p) => {
    const matchesCategory =
      activeCategory === "All" ||
      p.category === activeCategory ||
      (activeCategory === "Bra Cup Moulding Machine" && p.category.includes("Bra Cup")) ||
      (activeCategory === "Roll Forming & Sheet Metal" && (p.category.includes("Roll") || p.category.includes("Decoiler") || p.category.includes("Roofing"))) ||
      (activeCategory === "Cut To Length Line" && (p.category.includes("Cut") || p.category.includes("CTL")));

    const matchesSearch =
      searchQuery.trim() === "" ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.description || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.tagline && p.tagline.toLowerCase().includes(searchQuery.toLowerCase())) ||
      Object.values(p.specs || {}).some((v) =>
        v.toLowerCase().includes(searchQuery.toLowerCase())
      );

    return matchesCategory && matchesSearch;
  });

  return (
    <div className="bg-[#050505] text-white min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24">
      <SEO
        title="Industrial Machinery Catalogue"
        description="Catalogue of Bra Cup Moulding Machines, 10-Ton Hydraulic Decoilers, Roll Formers & Cut-To-Length Lines from Khopoli, Maharashtra."
        keywords="Bra Cup Moulding Machine, Hydraulic Decoiler, C Z Purlin Machine, Automatic CTL Line, Roofing Crimping Machine Catalogue, Gagan Engineering Khopoli"
        canonicalUrl={`${BUSINESS.websiteUrl}/products`}
        breadcrumbs={[
          { name: "Home", url: BUSINESS.websiteUrl },
          { name: "Machinery Catalogue", url: `${BUSINESS.websiteUrl}/products` }
        ]}
        itemList={filteredProducts}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Header */}
        <SectionHeader
          as="h1"
          overline="// Industrial Machinery Catalogue"
          title="Engineered for Continuous Shift Operations"
          description="Browse our range of heavy-duty bra cup moulding presses, coil handling decoilers, cut-to-length lines, and roll forming machinery manufactured at our Khopoli workshop."
        />

        {/* Search & Count Bar */}
        <div className="mt-8 sm:mt-12 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-[#0A0A0C] border border-white/10 rounded-xs p-3 sm:p-4">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by machine, spec, or speed..."
              className="w-full bg-black/60 border border-white/10 text-white text-xs sm:text-sm pl-10 pr-4 py-2.5 sm:py-3 rounded-xs focus:outline-none focus:border-[#FF5722] transition-colors"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-white/40 hover:text-white transition-colors"
              >
                Clear
              </button>
            )}
          </div>

          <div className="flex items-center gap-2 px-1 sm:px-3 py-1.5 sm:py-0 border-t sm:border-t-0 sm:border-l border-white/10">
            <Filter className="w-4 h-4 text-white/30 shrink-0" />
            <span className="mono text-xs text-white/60 whitespace-nowrap">
              Showing <span className="text-[#FF5722] font-bold">{filteredProducts.length}</span> machines
            </span>
          </div>
        </div>

        {/* Category Filter Pills — horizontal scroll on mobile */}
        <div className="mt-4 sm:mt-6 flex gap-2 sm:gap-2.5 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0 sm:flex-wrap" data-testid="products-filter">
          {CATEGORIES.map((c) => {
            const isSelected =
              activeCategory === c.name || (c.name === "All Machinery" && activeCategory === "All");
            return (
              <button
                key={c.id}
                onClick={() => handleCategorySelect(c.name === "All Machinery" ? "All" : c.name)}
                data-testid={`filter-${c.id}`}
                className={`mono text-xs tracking-wider uppercase px-3 sm:px-4 py-2 sm:py-2.5 rounded-xs border transition-all whitespace-nowrap flex-shrink-0 ${
                  isSelected
                    ? "bg-[#FF5722] border-[#FF5722] text-white font-bold shadow-md"
                    : "bg-[#09090B] border-white/10 text-white/70 hover:border-[#FF5722] hover:text-white"
                }`}
              >
                {c.name}
              </button>
            );
          })}
        </div>

        {/* Product Cards Grid */}
        {filteredProducts.length > 0 ? (
          <div
            className="mt-8 sm:mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6"
            data-testid="products-grid"
          >
            {filteredProducts.map((p, idx) => (
              <ProductCard key={p.id} product={p} index={idx} />
            ))}
          </div>
        ) : (
          <div className="mt-12 sm:mt-16 text-center p-8 sm:p-12 bg-[#09090B] border border-white/10 rounded-xs">
            <p className="text-white/60 mb-4 text-sm sm:text-base">No machinery matching your filter or search query.</p>
            <button
              onClick={() => {
                setActiveCategory("All");
                setSearchQuery("");
              }}
              className="btn-primary inline-flex"
            >
              Reset Filters
            </button>
          </div>
        )}

        {/* Custom Engineering CTA Banner */}
        <div className="mt-16 sm:mt-20 p-6 sm:p-8 md:p-10 bg-gradient-to-r from-[#0E0E10] to-[#121216] border border-white/10 rounded-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-5 sm:gap-6">
          <div className="max-w-2xl">
            <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] mb-2 font-semibold">
              // Custom Factory Solutions
            </div>
            <h3 className="font-display text-2xl sm:text-3xl text-white uppercase tracking-wider">
              Need custom platen sizes or specific motor tonnage?
            </h3>
            <p className="mt-2 text-xs sm:text-sm text-white/70 leading-relaxed">
              We specialize in custom roll-forming stations, double-sided heating platens, and hydraulic power pack configurations suited for your exact factory footprint.
            </p>
          </div>
          <div className="flex flex-col xs:flex-row sm:flex-col md:flex-row gap-3 w-full md:w-auto shrink-0">
            <Link to="/contact" className="btn-primary text-center flex items-center justify-center">
              Request Custom RFQ
            </Link>
            <a
              href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent("Hi Gagan Engineering, I need a customized machine quotation.")}`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 hover:bg-green-500 text-white text-xs font-semibold uppercase tracking-wider px-4 py-3 rounded-xs flex items-center justify-center gap-2 transition-colors"
            >
              <MessageCircle className="w-4 h-4" /> WhatsApp Specs
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
