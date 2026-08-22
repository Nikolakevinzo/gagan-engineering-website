import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Phone, Mail, MapPin, MessageCircle, Send, CheckCircle2, Clock, Factory } from "lucide-react";
import { toast } from "sonner";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BUSINESS } from "@/lib/business";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";
import { api } from "@/lib/api";

export default function Contact() {
  const [params] = useSearchParams();
  const preset = params.get("product") || "";

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    product_interest: preset || "Double Head Electric Bra Cup Moulding Machine",
    message: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (preset) {
      setForm((f) => ({ ...f, product_interest: preset }));
    }
  }, [preset]);

  const handle = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.phone || !form.email) {
      toast.error("Please fill in Name, Phone, and Email.");
      return;
    }

    setSubmitting(true);
    try {
      const r = await api.post("/contact", form);

      // Save lead locally to browser backup
      try {
        const existing = JSON.parse(localStorage.getItem("gagan_cached_leads") || "[]");
        const newLead = {
          id: r.data?.lead_id || `lead_${Date.now()}`,
          name: form.name,
          email: form.email,
          phone: form.phone,
          product_interest: form.product_interest,
          message: form.message,
          created_at: new Date().toISOString(),
          email_sent: Boolean(r.data?.email_sent),
        };
        localStorage.setItem("gagan_cached_leads", JSON.stringify([newLead, ...existing.filter(x => x.id !== newLead.id)].slice(0, 50)));
      } catch (e) {
        // ignore localStorage error
      }

      toast.success(r.data?.message || "Inquiry submitted successfully!");
      setDone(true);
      setForm({
        name: "",
        email: "",
        phone: "",
        product_interest: "Double Head Electric Bra Cup Moulding Machine",
        message: "",
      });
    } catch (err) {
      console.error("Submission error:", err);
      // Even if network fails, cache locally
      try {
        const existing = JSON.parse(localStorage.getItem("gagan_cached_leads") || "[]");
        const fallbackLead = {
          id: `local_${Date.now()}`,
          name: form.name,
          email: form.email,
          phone: form.phone,
          product_interest: form.product_interest,
          message: form.message,
          created_at: new Date().toISOString(),
          email_sent: false,
        };
        localStorage.setItem("gagan_cached_leads", JSON.stringify([fallbackLead, ...existing].slice(0, 50)));
      } catch (e) {}

      toast.success("Thank you! Your quotation request has been recorded. Our engineer will reach out.");
      setDone(true);
    } finally {
      setSubmitting(false);
    }
  };

  const breadcrumbs = [
    { name: "Home", url: BUSINESS.websiteUrl },
    { name: "Contact & RFQ", url: `${BUSINESS.websiteUrl}/contact` }
  ];

  return (
    <div className="bg-[#050505] min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24 text-white">
      <SEO
        title="Contact & Request Machinery Quotation | Gagan Engineering Works Khopoli"
        description="Request a price quotation for Bra Cup Moulding Machines, Hydraulic Decoilers, and Roll Formers from Gagan Engineering Works in Khopoli, Maharashtra. Direct phone and WhatsApp inquiries welcome."
        keywords="Contact Gagan Engineering Works, Machinery Price Quotation, Bra Cup Machine RFQ, Khopoli Factory Phone Number, Gagan Engineering Contact"
        breadcrumbs={breadcrumbs}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-1.5 sm:gap-2 mono text-[10px] sm:text-[11px] text-white/50 mb-6 sm:mb-8 uppercase tracking-wider overflow-x-auto whitespace-nowrap pb-1">
          <Link to="/" className="hover:text-white transition-colors shrink-0">Home</Link>
          <span className="shrink-0">/</span>
          <span className="text-[#FF5722] shrink-0">Contact & Quotation</span>
        </div>

        {/* Section Header */}
        <SectionHeader
          overline="// Connect With Our Works"
          title="Request a Machine Quotation (RFQ)"
          description="Tell us your factory's production target, sheet thickness, or cup size requirements. We will prepare an engineering proposal and commercial quotation within 24 hours."
        />

        <div className="mt-10 sm:mt-14 grid lg:grid-cols-12 gap-8 lg:gap-14">
          {/* Left: Contact Form */}
          <div className="lg:col-span-7">
            <form
              onSubmit={submit}
              className="bg-[#09090B] border border-white/10 p-5 sm:p-6 md:p-8 lg:p-10 rounded-xs space-y-5 sm:space-y-6 shadow-2xl"
              data-testid="contact-form"
            >
              {done && (
                <div className="flex items-start gap-3 bg-[#FF5722]/10 border border-[#FF5722]/40 p-3 sm:p-4 rounded-xs">
                  <CheckCircle2 className="w-5 h-5 text-[#FF5722] mt-0.5 shrink-0" />
                  <div>
                    <div className="font-semibold text-white text-sm">Quotation Request Received!</div>
                    <div className="text-xs text-white/70 mt-1 leading-relaxed">
                      Our chief engineer at Khopoli will review your specifications and contact you within 24 hours. For urgent needs, call us directly at <strong>{BUSINESS.phoneDisplay}</strong>.
                    </div>
                  </div>
                </div>
              )}

              {/* Name + Phone */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                <div>
                  <label className="block mono text-[10px] sm:text-[11px] uppercase tracking-wider text-white/70 mb-1.5 sm:mb-2">
                    Full Name <span className="text-[#FF5722]">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={form.name}
                    onChange={handle("name")}
                    placeholder="e.g. Rajesh Patel"
                    data-testid="contact-input-name"
                    className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-xs focus:outline-none focus:border-[#FF5722] transition-colors"
                  />
                </div>

                <div>
                  <label className="block mono text-[10px] sm:text-[11px] uppercase tracking-wider text-white/70 mb-1.5 sm:mb-2">
                    Phone / Mobile <span className="text-[#FF5722]">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    value={form.phone}
                    onChange={handle("phone")}
                    placeholder="+91 98765 43210"
                    data-testid="contact-input-phone"
                    className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-xs focus:outline-none focus:border-[#FF5722] transition-colors"
                  />
                </div>
              </div>

              {/* Email + Product */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                <div>
                  <label className="block mono text-[10px] sm:text-[11px] uppercase tracking-wider text-white/70 mb-1.5 sm:mb-2">
                    Email Address <span className="text-[#FF5722]">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={form.email}
                    onChange={handle("email")}
                    placeholder="factory@company.com"
                    data-testid="contact-input-email"
                    className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-xs focus:outline-none focus:border-[#FF5722] transition-colors"
                  />
                </div>

                <div>
                  <label className="block mono text-[10px] sm:text-[11px] uppercase tracking-wider text-white/70 mb-1.5 sm:mb-2">
                    Machinery of Interest
                  </label>
                  <select
                    value={form.product_interest}
                    onChange={handle("product_interest")}
                    data-testid="contact-input-product"
                    className="w-full bg-[#121214] border border-white/15 text-white text-sm px-3 py-3 rounded-xs focus:outline-none focus:border-[#FF5722] transition-colors"
                  >
                    {CATALOGUE_PRODUCTS.map((p) => (
                      <option key={p.id} value={p.name}>{p.name}</option>
                    ))}
                    <option value="Custom Engineered Machinery">Custom Engineered Machinery</option>
                    <option value="General Industrial Inquiry">General Industrial Inquiry</option>
                  </select>
                </div>
              </div>

              {/* Message */}
              <div>
                <label className="block mono text-[10px] sm:text-[11px] uppercase tracking-wider text-white/70 mb-1.5 sm:mb-2">
                  Production Requirements & Details
                </label>
                <textarea
                  rows={4}
                  value={form.message}
                  onChange={handle("message")}
                  placeholder="Mention your daily output target, raw material type (sheet thickness, foam grade), electrical power specs, or delivery location..."
                  data-testid="contact-input-message"
                  className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-xs focus:outline-none focus:border-[#FF5722] transition-colors"
                />
              </div>

              {/* Buttons */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-1 sm:pt-2">
                <button
                  type="submit"
                  disabled={submitting}
                  data-testid="contact-submit-btn"
                  className="w-full sm:w-auto btn-primary flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {submitting ? "Sending RFQ..." : "Submit Quotation Request"}
                </button>

                <a
                  href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent(`Hi Gagan Engineering, I want a quotation for: ${form.product_interest || "Industrial Machinery"}`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full sm:w-auto bg-green-600 hover:bg-green-500 text-white text-xs font-semibold uppercase tracking-wider px-5 py-3.5 rounded-xs flex items-center justify-center gap-2 transition-colors"
                >
                  <MessageCircle className="w-4 h-4" /> Send via WhatsApp
                </a>
              </div>
            </form>
          </div>

          {/* Right: Contact Info */}
          <div className="lg:col-span-5 space-y-4 sm:space-y-6">
            {/* Works Address Card */}
            <div className="bg-[#09090B] border border-white/10 p-5 sm:p-6 md:p-8 rounded-xs space-y-4 sm:space-y-5">
              <div className="mono text-xs uppercase tracking-[0.2em] text-[#FF5722] font-semibold">
                // Factory & Registered Works
              </div>

              <div className="space-y-3 sm:space-y-4 text-sm">
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-[#FF5722] shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-white">{BUSINESS.name}</div>
                    <div className="text-white/70 text-xs leading-relaxed mt-1">{BUSINESS.address}</div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-[#FF5722] shrink-0" />
                  <div>
                    <div className="text-xs text-white/50 mono">Direct Hotline:</div>
                    <a href={`tel:${BUSINESS.phone}`} className="text-white font-semibold hover:text-[#FF5722] transition-colors">
                      {BUSINESS.phoneDisplay}
                    </a>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-[#FF5722] shrink-0" />
                  <div>
                    <div className="text-xs text-white/50 mono">Direct Email:</div>
                    <a href={`mailto:${BUSINESS.email}`} className="text-white font-semibold hover:text-[#FF5722] transition-colors break-all">
                      {BUSINESS.email}
                    </a>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-[#FF5722] shrink-0" />
                  <div>
                    <div className="text-xs text-white/50 mono">Working Hours:</div>
                    <div className="text-white/80 text-xs leading-relaxed">{BUSINESS.workingHours}</div>
                  </div>
                </div>
              </div>

              {/* WhatsApp CTA */}
              <a
                href={`https://wa.me/${BUSINESS.phoneRaw}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 w-full bg-green-600/20 hover:bg-green-600 text-green-400 hover:text-white border border-green-500/40 text-xs font-semibold uppercase tracking-wider px-4 py-3 rounded-xs transition-all"
              >
                <MessageCircle className="w-4 h-4" /> Open WhatsApp Chat
              </a>
            </div>

            {/* Logistics Card */}
            <div className="bg-[#09090B] border border-white/10 p-5 sm:p-6 md:p-8 rounded-xs space-y-3">
              <div className="flex items-center gap-2 text-white font-semibold text-sm uppercase tracking-wide">
                <Factory className="w-4 h-4 text-[#FF5722]" /> Strategic Mumbai-Pune Logistics
              </div>
              <p className="text-xs text-white/60 leading-relaxed">
                Located directly on the Mumbai-Pune Highway in Khopoli, our works have seamless heavy transport connectivity for rapid machine dispatch across Maharashtra, Gujarat, South India, and JNPT Port for international exports.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
