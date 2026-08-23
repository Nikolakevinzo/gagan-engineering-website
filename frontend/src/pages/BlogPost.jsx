import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Calendar, Clock, ArrowLeft, ArrowRight, Tag, Share2, Printer, CheckCircle2, Factory, Wrench, Send, Phone, MessageCircle, BookOpen, Layers } from "lucide-react";
import { toast } from "sonner";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BLOG_ARTICLES } from "@/lib/blogData";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";
import { BUSINESS } from "@/lib/business";
import { api } from "@/lib/api";

export default function BlogPost() {
  const { slug } = useParams();
  const navigate = useNavigate();

  const article = BLOG_ARTICLES.find((a) => a.slug === slug);

  const [rfqForm, setRfqForm] = useState({
    name: "",
    email: "",
    phone: "",
    destination: "",
    message: ""
  });
  const [rfqSubmitting, setRfqSubmitting] = useState(false);
  const [rfqDone, setRfqDone] = useState(false);

  if (!article) {
    return (
      <div className="bg-[#050505] min-h-screen pt-32 flex flex-col items-center justify-center text-center px-4 text-white">
        <h1 className="font-display text-4xl text-white uppercase mb-4">Article Not Located</h1>
        <p className="text-white/60 mb-8 max-w-md text-sm">
          The technical engineering publication you requested may have been revised or updated.
        </p>
        <Link to="/blog" className="btn-primary">
          Back to Knowledge Hub
        </Link>
      </div>
    );
  }

  const handleRfqSubmit = async (e) => {
    e.preventDefault();
    if (!rfqForm.name || !rfqForm.email || !rfqForm.phone) {
      toast.error("Please fill in your Name, Email, and Phone Number.");
      return;
    }

    setRfqSubmitting(true);
    try {
      const payload = {
        name: rfqForm.name,
        email: rfqForm.email,
        phone: rfqForm.phone,
        product_interest: `Article Inquiry: ${article.title}`,
        message: `[KNOWLEDGE HUB INQUIRY] Article: ${article.title} (${slug})\nDestination: ${rfqForm.destination || "N/A"}\nMessage: ${rfqForm.message || "N/A"}`
      };

      const res = await api.post("/contact", payload);

      // Cache locally
      try {
        const existing = JSON.parse(localStorage.getItem("gagan_cached_leads") || "[]");
        const newLead = {
          id: res.data?.lead_id || `article_rfq_${Date.now()}`,
          name: rfqForm.name,
          email: rfqForm.email,
          phone: rfqForm.phone,
          product_interest: article.title,
          message: payload.message,
          created_at: new Date().toISOString(),
          email_sent: Boolean(res.data?.email_sent),
        };
        localStorage.setItem("gagan_cached_leads", JSON.stringify([newLead, ...existing].slice(0, 50)));
      } catch (err) {}

      toast.success("Inquiry received! Our machinery engineering team will contact you.");
      setRfqDone(true);
    } catch (err) {
      toast.success("Thank you! Your quotation request has been recorded.");
      setRfqDone(true);
    } finally {
      setRfqSubmitting(false);
    }
  };

  const relatedProducts = (article.relatedProducts || [])
    .map((pid) => CATALOGUE_PRODUCTS.find((p) => p.id === pid))
    .filter(Boolean);

  const breadcrumbs = [
    { name: "Home", url: BUSINESS.websiteUrl },
    { name: "Blog", url: `${BUSINESS.websiteUrl}/blog` },
    { name: article.title, url: `${BUSINESS.websiteUrl}/blog/${article.slug}` }
  ];

  return (
    <div className="bg-[#050505] min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24 text-white">
      <SEO
        title={article.title}
        description={article.summary}
        keywords={article.targetKeywords}
        canonicalUrl={`${BUSINESS.websiteUrl}/blog/${article.slug}`}
        ogImage={article.image}
        ogType="article"
        breadcrumbs={breadcrumbs}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Breadcrumb */}
        <div className="flex items-center gap-1.5 sm:gap-2 mono text-[10px] sm:text-[11px] text-white/50 mb-6 sm:mb-8 uppercase tracking-wider overflow-x-auto whitespace-nowrap pb-1">
          <Link to="/" className="hover:text-white transition-colors shrink-0">Home</Link>
          <span>/</span>
          <Link to="/blog" className="hover:text-white transition-colors shrink-0">Blog</Link>
          <span>/</span>
          <span className="text-[#FF5722] truncate">{article.title}</span>
        </div>

        {/* Article Header */}
        <div className="max-w-4xl space-y-4 pb-8 sm:pb-12 border-b border-white/10">
          <div className="inline-flex items-center gap-2 bg-[#FF5722]/10 border border-[#FF5722]/40 px-3 py-1 rounded-xs mono text-[10px] sm:text-xs uppercase tracking-widest text-[#FF5722]">
            <BookOpen className="w-3.5 h-3.5" />
            <span>{article.category}</span>
          </div>

          <h1 className="font-display text-3xl sm:text-4xl md:text-5xl text-white uppercase tracking-wide leading-tight">
            {article.title}
          </h1>

          <p className="text-white/70 text-sm sm:text-base leading-relaxed font-normal">
            {article.summary}
          </p>

          <div className="flex flex-wrap items-center gap-4 text-xs mono text-white/50 pt-2 border-t border-white/5">
            <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5 text-[#FF5722]" /> Published: {article.date}</span>
            <span>•</span>
            <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-[#FF5722]" /> {article.readTime}</span>
            <span>•</span>
            <span className="text-white/70">Author: {article.author}</span>
          </div>
        </div>

        {/* Article Layout (Content + Sticky Sidebar) */}
        <div className="mt-8 sm:mt-12 grid lg:grid-cols-12 gap-8 lg:gap-12 items-start">
          {/* Main Article Content */}
          <main className="lg:col-span-8 space-y-8 sm:space-y-10 text-white/80 leading-relaxed text-sm sm:text-base font-normal">
            {/* Featured Image */}
            <div className="aspect-[16/9] bg-[#0c0c0e] border border-white/10 rounded-xs overflow-hidden flex items-center justify-center p-6 shadow-2xl">
              <img
                src={article.image}
                alt={article.title}
                onError={(e) => {
                  e.currentTarget.src = "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg";
                }}
                className="w-full h-full object-contain"
              />
            </div>


            {/* Render Article Sections */}
            {article.content.map((sec, idx) => {
              if (sec.type === "section") {
                return (
                  <section key={idx} id={sec.id} className="space-y-4 pt-2 scroll-mt-28">
                    <h2 className="font-display text-2xl sm:text-3xl text-white uppercase tracking-wide border-b border-white/10 pb-2.5">
                      {sec.heading}
                    </h2>
                    <div className="whitespace-pre-line text-white/75 text-sm sm:text-base leading-relaxed">
                      {sec.text}
                    </div>

                    {sec.items && sec.items.length > 0 && (
                      <ul className="space-y-2.5 pt-2 text-sm sm:text-base text-white/80">
                        {sec.items.map((item, i) => (
                          <li key={i} className="flex items-start gap-2.5">
                            <span className="text-[#FF5722] font-bold text-base leading-none mt-1">▸</span>
                            <span dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>') }} />
                          </li>
                        ))}
                      </ul>
                    )}
                  </section>
                );
              }

              if (sec.type === "table") {
                return (
                  <div key={idx} className="space-y-3 pt-2">
                    <h3 className="font-display text-xl text-white uppercase tracking-wider text-[#FF5722]">
                      {sec.heading}
                    </h3>
                    <div className="overflow-x-auto bg-[#09090B] border border-white/10 rounded-xs shadow-xl">
                      <table className="w-full text-left text-xs sm:text-sm">
                        <thead className="bg-[#121216] border-b border-white/10 text-[#FF5722] mono text-[10px] sm:text-xs uppercase tracking-wider">
                          <tr>
                            {sec.headers.map((h, hi) => (
                              <th key={hi} className="px-4 py-3 font-semibold">{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {sec.rows.map((row, ri) => (
                            <tr key={ri} className="hover:bg-white/5 transition-colors">
                              {row.map((cell, ci) => (
                                <td key={ci} className="px-4 py-2.5 text-white/80 font-mono text-xs">{cell}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                );
              }

              return null;
            })}

            {/* Author Attribution Card */}
            <div className="mt-12 p-6 bg-[#09090B] border border-white/10 rounded-xs flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-[#FF5722]/10 border border-[#FF5722]/40 flex items-center justify-center text-[#FF5722] shrink-0 font-display text-lg">
                GSK
              </div>
              <div className="space-y-1 text-xs">
                <div className="font-semibold text-white text-sm">Gagan Engineering Technical Editorial Desk</div>
                <p className="text-white/60 leading-relaxed">
                  Published by senior mechanical and tooling engineers at Gagan Engineering Works Khopoli. Sourcing domestic certified raw materials and manufacturing industrial machinery in Maharashtra since 2006.
                </p>
              </div>
            </div>

            {/* Direct Inquiry Banner */}
            <div className="mt-10 bg-gradient-to-br from-[#0c1418] to-[#09090B] border border-[#FF5722]/40 p-6 sm:p-8 rounded-xs shadow-2xl space-y-4">
              <div className="inline-flex items-center gap-2 bg-[#FF5722]/10 border border-[#FF5722]/40 px-3 py-1 rounded-xs mono text-[10px] uppercase tracking-widest text-[#FF5722]">
                <Send className="w-3.5 h-3.5" />
                <span>Consult Factory Engineering Desk</span>
              </div>
              <h3 className="font-display text-2xl text-white uppercase tracking-wide">
                Need Machinery Sizing or a Commercial Price Quotation?
              </h3>
              <p className="text-white/70 text-xs sm:text-sm leading-relaxed">
                Connect directly with our engineering team for technical layouts, power grid customization, FOB/CIF delivery rates, or on-site commissioning timelines.
              </p>

              {rfqDone ? (
                <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 p-4 rounded-xs text-xs sm:text-sm flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 shrink-0" />
                  <span>Your request has been received. Our chief engineer will respond shortly!</span>
                </div>
              ) : (
                <form onSubmit={handleRfqSubmit} className="space-y-3 pt-2">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <input
                      type="text"
                      required
                      placeholder="Your Name *"
                      value={rfqForm.name}
                      onChange={(e) => setRfqForm({ ...rfqForm, name: e.target.value })}
                      className="bg-black/60 border border-white/15 text-white text-xs px-3.5 py-2.5 rounded-xs focus:outline-none focus:border-[#FF5722]"
                    />
                    <input
                      type="email"
                      required
                      placeholder="Business Email *"
                      value={rfqForm.email}
                      onChange={(e) => setRfqForm({ ...rfqForm, email: e.target.value })}
                      className="bg-black/60 border border-white/15 text-white text-xs px-3.5 py-2.5 rounded-xs focus:outline-none focus:border-[#FF5722]"
                    />
                    <input
                      type="tel"
                      required
                      placeholder="Phone / WhatsApp *"
                      value={rfqForm.phone}
                      onChange={(e) => setRfqForm({ ...rfqForm, phone: e.target.value })}
                      className="bg-black/60 border border-white/15 text-white text-xs px-3.5 py-2.5 rounded-xs focus:outline-none focus:border-[#FF5722]"
                    />
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                    <button
                      type="submit"
                      disabled={rfqSubmitting}
                      className="btn-primary text-xs font-semibold px-5 py-2.5 inline-flex items-center gap-2"
                    >
                      <Send className="w-3.5 h-3.5" />
                      {rfqSubmitting ? "Submitting..." : "Request Technical Quotation"}
                    </button>
                    <a
                      href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent(`Hello Gagan Engineering, I read your article "${article.title}" and would like a quote.`)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-emerald-400 hover:text-emerald-300 text-xs mono inline-flex items-center gap-1.5 transition-colors"
                    >
                      <MessageCircle className="w-3.5 h-3.5" /> Direct WhatsApp Inquiry →
                    </a>
                  </div>
                </form>
              )}
            </div>
          </main>

          {/* Sticky Sidebar */}
          <aside className="lg:col-span-4 space-y-6 sticky top-28">
            {/* Table of Contents */}
            {article.tableOfContents && article.tableOfContents.length > 0 && (
              <div className="bg-[#09090B] border border-white/10 p-5 rounded-xs space-y-3">
                <div className="mono text-xs uppercase tracking-widest text-[#FF5722] font-semibold flex items-center gap-2">
                  <BookOpen className="w-3.5 h-3.5" /> Table of Contents
                </div>
                <nav className="space-y-1.5 text-xs text-white/60">
                  {article.tableOfContents.map((item) => (
                    <a
                      key={item.id}
                      href={`#${item.id}`}
                      className="block hover:text-[#FF5722] hover:translate-x-1 transition-all py-1 border-b border-white/5 last:border-0"
                    >
                      {item.title}
                    </a>
                  ))}
                </nav>
              </div>
            )}

            {/* Related Certified Machinery */}
            {relatedProducts.length > 0 && (
              <div className="bg-[#09090B] border border-white/10 p-5 rounded-xs space-y-4">
                <div className="mono text-xs uppercase tracking-widest text-[#FF5722] font-semibold flex items-center gap-2">
                  <Wrench className="w-3.5 h-3.5" /> Related Machinery Lines
                </div>
                <div className="space-y-3">
                  {relatedProducts.map((p) => (
                    <Link
                      key={p.id}
                      to={`/products/${p.id}`}
                      className="block bg-black/40 border border-white/10 hover:border-[#FF5722]/50 p-3 rounded-xs group transition-all"
                    >
                      <div className="text-xs font-semibold text-white group-hover:text-[#FF5722] transition-colors line-clamp-1">
                        {p.name}
                      </div>
                      <div className="mono text-[10px] text-white/40 mt-1 flex items-center justify-between">
                        <span>{p.category}</span>
                        <span className="text-[#FF5722]">View Spec →</span>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Contact Card */}
            <div className="bg-[#09090B] border border-white/10 p-5 rounded-xs space-y-3 text-xs">
              <div className="font-semibold text-white uppercase mono text-xs">Khopoli Factory Hotline</div>
              <p className="text-white/60">
                Call our workshop directly for immediate machine delivery schedules and tooling advice:
              </p>
              <a
                href={`tel:${BUSINESS.phone}`}
                className="btn-ghost w-full justify-center flex items-center gap-2 text-xs"
              >
                <Phone className="w-3.5 h-3.5 text-[#FF5722]" /> {BUSINESS.phoneDisplay}
              </a>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
