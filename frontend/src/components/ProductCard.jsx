import { Link } from "react-router-dom";
import { ArrowRight, MessageCircle, Eye, CheckCircle2 } from "lucide-react";
import { BUSINESS } from "@/lib/business";
import { getProductImages } from "@/lib/catalogueData";

export default function ProductCard({ product, index = 0 }) {
  const specsEntries = Object.entries(product.specs || {}).slice(0, 3);
  const coverImage = getProductImages(product)[0] || "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg";

  return (
    <div
      data-testid={`product-card-${product.id}`}
      className="group relative bg-[#09090B] border border-white/10 hover:border-[#FF5722]/60 transition-all duration-300 rounded-sm flex flex-col justify-between overflow-hidden hover:-translate-y-1 shadow-lg"
    >
      {/* Top Image & Category Tag */}
      <div>
        <div className="relative aspect-[16/10] bg-[#0c0c0e] flex items-center justify-center p-3 sm:p-4 overflow-hidden border-b border-white/10">
          <img
            src={coverImage}
            alt={`${product.name} - Gagan Engineering Works`}
            loading="lazy"
            onError={(e) => {
              e.currentTarget.src = "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg";
            }}
            className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute top-2.5 left-2.5 bg-black/85 backdrop-blur-md px-2 py-0.5 text-[9px] sm:text-[10px] mono tracking-wider text-[#FF5722] border border-[#FF5722]/30 uppercase rounded-xs">
            {product.category}
          </div>
          {product.featured && (
            <div className="absolute top-2.5 right-2.5 bg-[#FF5722] text-white px-2 py-0.5 text-[8px] sm:text-[9px] mono tracking-widest uppercase font-bold rounded-xs shadow-md">
              Featured
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="font-display text-xl sm:text-2xl text-white tracking-wide uppercase line-clamp-1 group-hover:text-[#FF5722] transition-colors">
            {product.name}
          </h3>
          <p className="text-xs text-white/60 mt-2 line-clamp-2 leading-relaxed">
            {product.tagline || product.shortDesc}
          </p>

          {/* Quick Specs Snippet */}
          {specsEntries.length > 0 && (
            <div className="mt-4 pt-3 border-t border-white/5 space-y-1.5 text-xs">
              {specsEntries.map(([key, val]) => (
                <div key={key} className="flex justify-between items-center text-[11px]">
                  <span className="text-white/40 mono truncate max-w-[45%]">{key}:</span>
                  <span className="text-white/80 font-medium truncate max-w-[55%] text-right">{val}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Card Action Buttons */}
      <div className="p-6 pt-0 mt-2 flex items-center gap-2">
        <Link
          to={`/products/${product.id}`}
          data-testid={`product-detail-link-${product.id}`}
          className="flex-1 btn-primary py-2.5 px-3 text-xs text-center flex items-center justify-center gap-1.5"
        >
          <span>View Specs</span> <ArrowRight className="w-3.5 h-3.5" />
        </Link>
        <a
          href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent(`Hi, I am interested in getting a price quote for: ${product.name}`)}`}
          target="_blank"
          rel="noopener noreferrer"
          data-testid={`product-card-whatsapp-${product.id}`}
          title="Inquire on WhatsApp"
          className="p-2.5 bg-green-600/20 hover:bg-green-600 text-green-400 hover:text-white border border-green-500/40 rounded-xs transition-colors"
        >
          <MessageCircle className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}
