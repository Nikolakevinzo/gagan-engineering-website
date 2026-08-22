import { Link } from "react-router-dom";
import { Shield, Lock, Eye, FileText, Phone, Mail } from "lucide-react";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BUSINESS } from "@/lib/business";

export default function PrivacyPolicy() {
  return (
    <div className="bg-[#050505] text-white min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24">
      <SEO
        title="Privacy Policy"
        description="Privacy Policy for Gagan Engineering Works. Learn how we handle and protect customer inquiries, communications, and quotation details."
        keywords="Privacy Policy, Gagan Engineering Works Privacy, Data Protection Khopoli"
        canonicalUrl={`${BUSINESS.websiteUrl}/privacy-policy`}
        breadcrumbs={[
          { name: "Home", url: BUSINESS.websiteUrl },
          { name: "Privacy Policy", url: `${BUSINESS.websiteUrl}/privacy-policy` }
        ]}
      />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mono text-xs text-white/50 mb-6 uppercase tracking-wider">
          <Link to="/" className="hover:text-white transition-colors">Home</Link>
          <span>/</span>
          <span className="text-[#FF5722]">Privacy Policy</span>
        </div>

        <SectionHeader
          as="h1"
          overline="// Privacy & Data Protection"
          title="Privacy Policy"
          description="Last updated: August 2026. Gagan Engineering Works is committed to protecting your business contact information and privacy."
        />

        <div className="mt-10 space-y-8 text-sm text-white/80 leading-relaxed">
          <div className="bg-[#0A0A0C] border border-white/10 p-6 rounded-xs space-y-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#FF5722]" /> Information We Collect
            </h2>
            <p>
              When you submit a machine price inquiry, request technical specifications, or contact our sales engineering team, we collect only the necessary details: Name, Company Name, Phone/WhatsApp Number, Email Address, and Machine Interests.
            </p>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Lock className="w-4 h-4 text-[#FF5722]" /> How We Use Your Information
            </h2>
            <p>
              We use your information exclusively for:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-white/70">
              <li>Preparing accurate machine quotations and technical drawings.</li>
              <li>Coordinating factory trial visits, freight dispatch, and on-site commissioning.</li>
              <li>Providing post-sales warranty and spare parts assistance.</li>
              <li>We never sell, rent, or trade your contact data with third-party advertising brokers.</li>
            </ul>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Eye className="w-4 h-4 text-[#FF5722]" /> Security & Data Retention
            </h2>
            <p>
              Your inquiries and communications are stored securely using encrypted connections (TLS/HTTPS). We retain business inquiries only as long as necessary to fulfill technical support, warranty obligations, and statutory tax/accounting compliance under Indian commercial law.
            </p>
          </div>

          <div className="bg-[#0e0e11] border border-white/10 p-6 rounded-xs space-y-2 text-xs">
            <div className="font-bold text-white text-sm">Privacy Inquiries Contact</div>
            <p className="text-white/70">For any questions regarding your data, please contact:</p>
            <p className="text-white">Email: <strong>{BUSINESS.email}</strong> | Phone: <strong>{BUSINESS.phoneDisplay}</strong></p>
            <p className="text-white/50">{BUSINESS.address}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
