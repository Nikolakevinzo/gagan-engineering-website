import { Link } from "react-router-dom";
import { FileText, CheckCircle2, ShieldCheck, Phone, Mail } from "lucide-react";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BUSINESS } from "@/lib/business";

export default function Terms() {
  return (
    <div className="bg-[#050505] text-white min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24">
      <SEO
        title="Terms & Conditions"
        description="Terms and conditions for machinery inquiries, quotation validity, manufacturing lead times, and commercial supply by Gagan Engineering Works."
        keywords="Terms and Conditions, Machinery Supply Terms, Gagan Engineering Works Khopoli"
        breadcrumbs={[
          { name: "Home", url: BUSINESS.websiteUrl },
          { name: "Terms & Conditions", url: `${BUSINESS.websiteUrl}/terms` }
        ]}
      />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mono text-xs text-white/50 mb-6 uppercase tracking-wider">
          <Link to="/" className="hover:text-white transition-colors">Home</Link>
          <span>/</span>
          <span className="text-[#FF5722]">Terms & Conditions</span>
        </div>

        <SectionHeader
          overline="// Commercial Terms"
          title="Terms & Conditions of Machinery Supply"
          description="Last updated: August 2026. These commercial terms govern machinery orders, quotations, manufacturing lead times, and warranties provided by Gagan Engineering Works."
        />

        <div className="mt-10 space-y-8 text-sm text-white/80 leading-relaxed">
          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">1. Quotations & Pricing</h2>
            <p>
              Machine price quotations issued by Gagan Engineering Works remain valid for <strong>30 days</strong> from the date of issue unless specified otherwise. Quotations exclude statutory GST (applicable as per prevailing Indian tariff slabs) and freight/transport charges unless explicitly stated.
            </p>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">2. Manufacturing & Delivery Lead Times</h2>
            <p>
              Standard manufacturing lead times range between <strong>2 to 6 weeks</strong> depending on machine complexity, customization requirements (e.g. customized PLC automation or special platen dimensions), and workshop workload. Delivery timelines commence upon receipt of the agreed advance payment and final technical drawing approval.
            </p>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">3. Installation, Commissioning & Warranty</h2>
            <p>
              All machines include a <strong>1-Year Manufacturer Warranty</strong> covering manufacturing defects and mechanical/electrical components. Pan-India on-site commissioning and operator training are provided. Buyers are responsible for providing appropriate factory electrical supply (3-Phase 415V standard), pneumatic air connections, and hydraulic oil as per machine requirements.
            </p>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">4. Governing Law & Jurisdiction</h2>
            <p>
              Any disputes arising from commercial supply or purchase agreements shall be subject to the exclusive jurisdiction of the competent courts in <strong>Khalapur / Khopoli / Raigad District, Maharashtra, India</strong>.
            </p>
          </div>

          <div className="bg-[#0e0e11] border border-white/10 p-6 rounded-xs space-y-2 text-xs">
            <div className="font-bold text-white text-sm">Gagan Engineering Works Works & Office</div>
            <p className="text-white/70">Phone: {BUSINESS.phoneDisplay} | Email: {BUSINESS.email}</p>
            <p className="text-white/50">{BUSINESS.address}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
