import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, Phone, MessageCircle, ShieldCheck, Printer, FileText, ChevronDown, Wrench, Factory } from "lucide-react";
import SEO from "@/components/SEO";
import ProductCard from "@/components/ProductCard";
import SectionHeader from "@/components/SectionHeader";
import { CATALOGUE_PRODUCTS, getLiveCatalogueProducts } from "@/lib/catalogueData";
import { BUSINESS } from "@/lib/business";
import { api } from "@/lib/api";

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [product, setProduct] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openFaq, setOpenFaq] = useState(null);

  useEffect(() => {
    setLoading(true);
    const liveList = getLiveCatalogueProducts();
    const localProd = liveList.find((p) => p.id === id);

    api
      .get(`/products/${id}`)
      .then((r) => {
        if (r.data && r.data.product) {
          // Merge with live custom updates if available
          setProduct(localProd ? { ...r.data.product, ...localProd } : r.data.product);
          setRelated(r.data.related || []);
        } else if (localProd) {
          setProduct(localProd);
          setRelated(
            liveList.filter((p) => p.categorySlug === localProd.categorySlug && p.id !== localProd.id).slice(0, 3)
          );
        }
        setLoading(false);
        window.scrollTo(0, 0);
      })
      .catch(() => {
        if (localProd) {
          setProduct(localProd);
          setRelated(
            liveList.filter((p) => p.categorySlug === localProd.categorySlug && p.id !== localProd.id).slice(0, 3)
          );
        }
        setLoading(false);
        window.scrollTo(0, 0);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="bg-[#050505] min-h-screen pt-32 flex items-center justify-center text-white/50 mono uppercase tracking-widest text-sm">
        Loading Machine Specifications...
      </div>
    );
  }

  if (!product) {
    return (
      <div className="bg-[#050505] min-h-screen pt-32 flex flex-col items-center justify-center text-center px-4">
        <h1 className="font-display text-4xl text-white uppercase mb-4">Machine Not Found</h1>
        <p className="text-white/60 mb-8 max-w-md">
          The requested machinery specification may have been moved or updated in our workshop catalogue.
        </p>
        <Link to="/products" className="btn-primary">
          Browse All Machinery
        </Link>
      </div>
    );
  }

  const breadcrumbs = [
    { name: "Home", url: BUSINESS.websiteUrl },
    { name: "Machinery Catalogue", url: `${BUSINESS.websiteUrl}/products` },
    { name: product.name, url: `${BUSINESS.websiteUrl}/products/${product.id}` }
  ];

  return (
    <div className="bg-[#050505] text-white min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24">
      <SEO
        title={`${product.name} Manufacturer India`}
        description={`Specifications & Price for ${product.name}. ${(product.description || "").slice(0, 150)}... Manufactured by Gagan Engineering Works, Khopoli.`}
        keywords={`${product.name}, ${product.category}, Industrial Machinery Manufacturer, Gagan Engineering Khopoli, ${product.name} price`}
        productData={product}
        faqData={product.faqs}
        breadcrumbs={breadcrumbs}
        canonicalUrl={`${BUSINESS.websiteUrl}/products/${product.id}`}
        ogImage={product.image}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-1.5 sm:gap-2 mono text-[10px] sm:text-[11px] text-white/50 mb-6 sm:mb-8 uppercase tracking-wider overflow-x-auto whitespace-nowrap pb-1">
          <Link to="/" className="hover:text-white transition-colors shrink-0">Home</Link>
          <span className="shrink-0">/</span>
          <Link to="/products" className="hover:text-white transition-colors shrink-0">Catalogue</Link>
          <span className="shrink-0">/</span>
          <span className="text-[#FF5722] truncate">{product.name}</span>
        </div>

        {/* Top Product Overview Grid */}
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-start">
          {/* Left: Product Image */}
          <div className="space-y-3 sm:space-y-4">
            <div className="relative border border-white/10 bg-[#0c0c0e] aspect-[4/3] sm:aspect-[16/11] rounded-xs overflow-hidden shadow-2xl p-4 sm:p-6 flex items-center justify-center">
              <img
                src={product.image || "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg"}
                alt={`${product.name} - Gagan Engineering Works Khopoli`}
                className="w-full h-full object-contain"
                onError={(e) => {
                  e.currentTarget.src = "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg";
                }}
                data-testid="product-image"
              />
              <div className="absolute top-3 left-3 bg-black/85 backdrop-blur-md px-2.5 sm:px-3 py-1 sm:py-1.5 mono text-[9px] sm:text-[10px] tracking-[0.15em] sm:tracking-[0.2em] uppercase text-[#FF5722] border border-[#FF5722]/40 rounded-xs">
                {product.category}
              </div>
            </div>

            {/* Quick Badges */}
            <div className="grid grid-cols-3 gap-2 text-center mono text-white/70">
              {[
                { icon: ShieldCheck, label: "Warranty", value: "1 Year" },
                { icon: Factory, label: "Origin", value: "Khopoli, MH" },
                { icon: Wrench, label: "Commissioning", value: "Pan-India" },
              ].map((badge) => (
                <div key={badge.label} className="p-2 sm:p-3 bg-white/5 border border-white/10 rounded-xs">
                  <badge.icon className="w-4 h-4 text-[#FF5722] mx-auto mb-1" />
                  <div className="text-[8px] sm:text-[10px] text-white/40 uppercase">{badge.label}</div>
                  <div className="font-semibold text-white text-[10px] sm:text-xs mt-0.5">{badge.value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Specs & Actions */}
          <div className="space-y-5 sm:space-y-6">
            <div className="mono text-xs uppercase tracking-[0.2em] text-[#FF5722] font-semibold">
              // Precision Engineering Spec
            </div>

            <h1 className="font-display text-3xl sm:text-4xl md:text-5xl text-white tracking-wide uppercase leading-tight" data-testid="product-name">
              {product.name}
            </h1>

            <p className="text-sm sm:text-base text-white/70 leading-relaxed font-normal" data-testid="product-description">
              {product.description}
            </p>

            {/* Action Buttons */}
            <div className="pt-1 sm:pt-2 flex flex-col xs:flex-row flex-wrap gap-2 sm:gap-3">
              <Link
                to={`/contact?product=${encodeURIComponent(product.name)}`}
                className="btn-primary flex items-center justify-center gap-2 xs:flex-1"
                data-testid="product-quote-btn"
              >
                Request Quotation <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent(`Hello Gagan Engineering, I would like to request price and delivery schedule for: ${product.name}`)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-green-600 hover:bg-green-500 text-white text-xs font-semibold uppercase tracking-wider px-4 py-3 rounded-xs flex items-center justify-center gap-2 transition-colors"
                data-testid="product-whatsapp-btn"
              >
                <MessageCircle className="w-4 h-4" /> WhatsApp Quote
              </a>
              <a
                href={`tel:${BUSINESS.phone}`}
                className="btn-ghost flex items-center justify-center gap-2"
                data-testid="product-call-btn"
              >
                <Phone className="w-4 h-4" /> Call Works
              </a>
              <button
                onClick={() => window.print()}
                className="btn-ghost flex items-center justify-center gap-2"
                title="Print Specification Sheet"
              >
                <Printer className="w-4 h-4" /> Print
              </button>
            </div>

            {/* Technical Specification Matrix */}
            <div className="pt-2 sm:pt-4">
              <div className="bg-[#09090B] border border-white/10 rounded-xs overflow-hidden">
                <div className="bg-[#121216] px-4 sm:px-5 py-3 sm:py-3.5 border-b border-white/10 flex items-center justify-between">
                  <span className="mono text-xs tracking-[0.15em] sm:tracking-[0.2em] uppercase text-[#FF5722] font-semibold flex items-center gap-2">
                    <FileText className="w-4 h-4" /> Technical Specifications
                  </span>
                  <span className="text-[10px] sm:text-[11px] mono text-white/40 hidden sm:block">Verified In-House</span>
                </div>

                <div className="divide-y divide-white/5 text-sm" data-testid="product-specs">
                  {Object.entries(product.specs || {}).map(([key, val]) => (
                    <div key={key} className="grid grid-cols-1 sm:grid-cols-2 px-4 sm:px-5 py-2.5 sm:py-3 gap-0.5 sm:gap-1 hover:bg-white/5 transition-colors">
                      <span className="text-white/50 mono text-[10px] sm:text-xs uppercase tracking-wider">{key}</span>
                      <span className="text-white font-medium text-xs sm:text-sm">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Product FAQs Section */}
        {product.faqs && product.faqs.length > 0 && (
          <div className="mt-16 sm:mt-20 pt-10 sm:pt-12 border-t border-white/10">
            <SectionHeader
              overline="// Technical Q&A"
              title="Machine Specific FAQs"
              description={`Frequently asked technical questions regarding the ${product.name}.`}
            />

            <div className="mt-6 sm:mt-8 max-w-4xl space-y-3">
              {product.faqs.map((faq, idx) => {
                const isOpen = openFaq === idx;
                return (
                  <div
                    key={idx}
                    className="border border-white/10 bg-[#09090B] rounded-xs overflow-hidden"
                  >
                    <button
                      onClick={() => setOpenFaq(isOpen ? null : idx)}
                      className="w-full text-left p-4 sm:p-5 flex items-start sm:items-center justify-between gap-3 sm:gap-4 hover:text-[#FF5722] transition-colors"
                    >
                      <span className="font-medium text-sm sm:text-base text-white text-left">{faq.q}</span>
                      <ChevronDown
                        className={`w-4 h-4 text-[#FF5722] transition-transform duration-200 shrink-0 mt-0.5 sm:mt-0 ${
                          isOpen ? "rotate-180" : ""
                        }`}
                      />
                    </button>
                    {isOpen && (
                      <div className="px-4 sm:px-5 pb-4 sm:pb-5 pt-0 text-white/70 text-sm leading-relaxed border-t border-white/5 bg-black/40 pt-4">
                        {faq.a}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Related Machinery */}
        {related && related.length > 0 && (
          <div className="mt-16 sm:mt-20 pt-10 sm:pt-12 border-t border-white/10">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 sm:gap-4 mb-6 sm:mb-8">
              <SectionHeader
                overline="// Related Machinery"
                title="Explore Complementary Equipment"
                description="Other industrial machinery designed for your production line."
              />
              <Link to="/products" className="btn-ghost shrink-0 self-start sm:self-auto">
                All Machines →
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {related.map((p, idx) => (
                <ProductCard key={p.id} product={p} index={idx} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
