import { Link } from "react-router-dom";
import { ShieldCheck, RefreshCw, Wrench, AlertCircle, Phone, Mail, FileText, CheckCircle2 } from "lucide-react";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BUSINESS } from "@/lib/business";

export default function ReturnPolicy() {
  return (
    <div className="bg-[#050505] text-white min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24">
      <SEO
        title="Warranty, Returns & Cancellation Policy"
        description="Official Warranty, Return and Cancellation Policy for industrial machinery manufactured by Gagan Engineering Works, Khopoli, Maharashtra."
        keywords="Return Policy, Warranty Terms, Gagan Engineering Works Refund Policy, Machinery Warranty Khopoli"
        breadcrumbs={[
          { name: "Home", url: BUSINESS.websiteUrl },
          { name: "Return & Warranty Policy", url: `${BUSINESS.websiteUrl}/return-policy` }
        ]}
      />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mono text-xs text-white/50 mb-6 uppercase tracking-wider">
          <Link to="/" className="hover:text-white transition-colors">Home</Link>
          <span>/</span>
          <span className="text-[#FF5722]">Return & Warranty Policy</span>
        </div>

        <SectionHeader
          overline="// Official Policy"
          title="Return, Replacement & Warranty Policy"
          description="Last updated: August 2026. This policy applies to all industrial machinery and equipment manufactured and supplied by Gagan Engineering Works."
        />

        <div className="mt-10 space-y-8 text-sm text-white/80 leading-relaxed">
          {/* Policy Overview Card */}
          <div className="bg-[#0A0A0C] border border-white/10 p-6 rounded-xs space-y-4">
            <div className="flex items-center gap-3 text-[#FF5722] font-semibold text-base">
              <ShieldCheck className="w-5 h-5" /> 1-Year Comprehensive Manufacturer Warranty
            </div>
            <p>
              All industrial machines (including Bra Cup Moulding Machines, Hydraulic Decoilers, Roll Forming Lines, and Cut-To-Length Lines) manufactured by <strong>Gagan Engineering Works</strong> are covered under a <strong>1-Year Comprehensive Manufacturer Warranty</strong> from the date of dispatch and on-site commissioning.
            </p>
          </div>

          {/* Section 1: Returns & Custom Manufacturing */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-[#FF5722]" /> 1. Returns & Exchange Policy
            </h2>
            <p>
              Due to the specialized nature of heavy-duty, custom-engineered industrial machinery:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-white/70">
              <li>
                <strong>Custom-Built Equipment:</strong> Machinery manufactured to customer-specified platen sizes, roll profiles, voltage specifications, or sheet dimensions is built to order and is <strong>non-returnable for change-of-mind</strong> once manufactured and dispatched.
              </li>
              <li>
                <strong>Pre-Dispatch Factory Trials:</strong> Every customer is invited to conduct trial production runs at our Khopoli facility to verify machine performance, tolerances, and cycle times prior to final packaging and dispatch.
              </li>
            </ul>
          </div>

          {/* Section 2: Defective Goods & Part Replacement */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Wrench className="w-4 h-4 text-[#FF5722]" /> 2. Defective Goods, Damaged Parts & Replacements
            </h2>
            <p>
              In the event that any machine component or part is found defective in material, workmanship, or transit:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-white/70">
              <li>
                <strong>Immediate Replacement:</strong> Any defective hydraulic valve, heating element, platen component, or electrical switchgear covered under warranty will be repaired or replaced <strong>free of charge</strong>.
              </li>
              <li>
                <strong>Transit Damage:</strong> If transit damage occurs during freight delivery arranged by us, report it within <strong>48 hours of receipt</strong> with photographic evidence, and our team will dispatch replacement parts or a technician immediately.
              </li>
              <li>
                <strong>On-Site Technician Support:</strong> Our factory-trained service engineers provide prompt on-site diagnostics, servicing, and replacement across India.
              </li>
            </ul>
          </div>

          {/* Section 3: Order Cancellation & Refunds */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-[#FF5722]" /> 3. Cancellation & Refund Terms
            </h2>
            <ul className="list-disc pl-5 space-y-2 text-white/70">
              <li>
                <strong>Standard Orders:</strong> Order cancellations requested before raw material procurement or engineering fabrication begins are eligible for refund of advance deposit minus standard administrative fees (processed within 7–10 business days).
              </li>
              <li>
                <strong>In-Production Orders:</strong> Once machining (CNC tooling, EN31 roll turning, steel cutting) has commenced, advance payments are non-refundable as materials are custom cut.
              </li>
            </ul>
          </div>

          {/* Section 4: How to Request Warranty Support or Replacement */}
          <div className="bg-[#0e0e11] border border-white/10 p-6 rounded-xs space-y-4">
            <h2 className="text-base font-bold text-white">How to Claim Warranty Support or Part Replacement</h2>
            <p className="text-xs text-white/70">
              Please contact our dedicated support desk with your invoice number, machine serial number, and a brief description of the issue:
            </p>
            <div className="grid sm:grid-cols-2 gap-3 pt-2 text-xs">
              <div className="flex items-center gap-2 text-white">
                <Phone className="w-4 h-4 text-[#FF5722]" />
                <span>Direct Support: <strong>{BUSINESS.phoneDisplay}</strong></span>
              </div>
              <div className="flex items-center gap-2 text-white">
                <Mail className="w-4 h-4 text-[#FF5722]" />
                <span>Email: <strong>{BUSINESS.email}</strong></span>
              </div>
            </div>
            <p className="text-xs text-white/50 pt-2">
              Factory Address: {BUSINESS.address}
            </p>
          </div>

          {/* Links */}
          <div className="pt-4 flex flex-wrap gap-4 text-xs mono">
            <Link to="/contact" className="text-[#FF5722] hover:underline flex items-center gap-1">
              Contact Support <CheckCircle2 className="w-3.5 h-3.5" />
            </Link>
            <Link to="/products" className="text-white/60 hover:text-white transition-colors">
              View Machinery Catalogue
            </Link>
            <Link to="/privacy-policy" className="text-white/60 hover:text-white transition-colors">
              Privacy Policy
            </Link>
            <Link to="/terms" className="text-white/60 hover:text-white transition-colors">
              Terms & Conditions
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
