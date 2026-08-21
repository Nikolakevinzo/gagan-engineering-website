import { MessageCircle, Phone } from "lucide-react";
import { BUSINESS } from "@/lib/business";

export default function FloatingCTA() {
  return (
    <div className="fixed bottom-6 left-6 z-40 flex items-center gap-3">
      {/* WhatsApp Button */}
      <a
        href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent("Hello Gagan Engineering Works, I am looking for machinery details.")}`}
        target="_blank"
        rel="noopener noreferrer"
        data-testid="floating-whatsapp"
        aria-label="Chat on WhatsApp"
        className="w-12 h-12 bg-green-600 hover:bg-green-500 text-white rounded-full flex items-center justify-center shadow-2xl border border-white/20 transition-all hover:scale-110 active:scale-95 group relative"
      >
        <MessageCircle className="w-6 h-6" />
        <span className="absolute left-14 bg-black/90 text-white text-xs px-2.5 py-1 rounded shadow opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap border border-white/10">
          Chat on WhatsApp
        </span>
      </a>

      {/* Call Button */}
      <a
        href={`tel:${BUSINESS.phone}`}
        data-testid="floating-phone"
        aria-label="Call Now"
        className="w-12 h-12 bg-[#FF5722] hover:bg-[#F4511E] text-white rounded-full flex items-center justify-center shadow-2xl border border-white/20 transition-all hover:scale-110 active:scale-95 group relative"
      >
        <Phone className="w-5 h-5" />
        <span className="absolute left-14 bg-black/90 text-white text-xs px-2.5 py-1 rounded shadow opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap border border-white/10">
          Call: {BUSINESS.phoneDisplay}
        </span>
      </a>
    </div>
  );
}
