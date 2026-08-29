import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAdminAuth } from "@/components/AdminLayout";
import {
  Plus, Trash2, Save, ArrowLeft, Upload,
  ChevronDown, ChevronUp, FileText, HelpCircle, Image as ImageIcon,
  Loader2, Sparkles, ArrowUp, ArrowDown, Eye, Check, X,
  Link2, RefreshCw
} from "lucide-react";

import { getBackendUrl } from "@/lib/adminConfig";
import { CATALOGUE_PRODUCTS, normalizeImageUrl } from "@/lib/catalogueData";

const BACKEND_URL = getBackendUrl();

const CATEGORY_OPTIONS = [
  { slug: "bra-cup-moulding-machine", name: "Bra Cup Moulding Machine" },
  { slug: "roll-forming-sheet-metal", name: "Roll Forming & Sheet Metal" },
  { slug: "cut-to-length-line", name: "Cut To Length Line" },
];

const SPEC_TEMPLATES = {
  "bra-cup": {
    name: "Bra Cup Moulding Preset",
    specs: {
      "Drive Mechanism": "Electric & Pneumatic dual-head",
      "Heating System": "Dual PID Microprocessor Controlled (0–250°C)",
      "Production Capacity": "400–600 pcs / shift (8 hours)",
      "Power Supply": "3-Phase 415V AC, 50Hz",
      "Platen Material": "High-grade Hardened Tool Steel",
      "Clamping": "Pneumatic cylinder with timer lock",
      "Applicable Materials": "PU Foam, Polyester Fiberfill, Laminated Fabrics, Spandex",
      "Application": "Seamless bra cups, swimsuit padding, sportswear inserts",
      "Warranty": "1 Year Manufacturer Warranty + Lifetime Support",
      "Origin": "Manufactured in Khopoli, Maharashtra, India"
    }
  },
  "roll-forming": {
    name: "Roll Forming / Decoiler Preset",
    specs: {
      "Load Capacity": "10,000 kg (10 Metric Tons)",
      "Material Thickness": "1.5 mm to 3.0 mm Galvanized / HR Steel",
      "Line Speed": "10–18 meters per minute",
      "Roller Stations": "16–20 Forming Stations (Cr12 / EN31 Tool Steel)",
      "Motor Power": "7.5 HP Geared Motor",
      "Control System": "Delta / Siemens PLC + Touchscreen HMI",
      "Shearing Unit": "Hydraulic Post-Cut System",
      "Application": "PEB structures, Roofing sheets, Solar mounting channels",
      "Warranty": "1 Year Comprehensive Warranty",
      "Origin": "Manufactured in Khopoli, Maharashtra, India"
    }
  },
  "ctl-line": {
    name: "Cut To Length Line Preset",
    specs: {
      "Machine Type": "Heavy-Duty Automatic Cut To Length Line",
      "Material Thickness": "Up to 6.0 mm MS / GI / Stainless Steel",
      "Material Width": "Up to 1250 mm / 1500 mm",
      "Line Speed": "20 Meters / Minute continuous",
      "Decoiler Capacity": "10 Metric Ton Hydraulic",
      "Leveller Mechanism": "9-Roll Gear Driven Precision Leveller",
      "Shearing Unit": "Guillotine Hydraulic Shear (cuts up to 6mm)",
      "Length Measuring": "Optical Rotary Encoder PLC (±0.5mm accuracy)",
      "Total Connected Power": "18 HP",
      "Warranty": "1 Year Warranty + Pan-India Commissioning"
    }
  }
};

const EMPTY_PRODUCT = {
  name: "",
  category: "Bra Cup Moulding Machine",
  categorySlug: "bra-cup-moulding-machine",
  image: "",
  images: [],
  video_url: "",
  tagline: "",
  shortDesc: "",
  description: "",
  featured: false,
};

// -------------------------------------------------------------
// Interactive Specification Table Component
// -------------------------------------------------------------
function SpecificationTableBuilder({ specs, onChange }) {
  const entries = Object.entries(specs || {});
  const [showPreview, setShowPreview] = useState(true);

  const handleKeyChange = (idx, newKey) => {
    const newEntries = [...entries];
    newEntries[idx] = [newKey, newEntries[idx][1]];
    onChange(Object.fromEntries(newEntries));
  };

  const handleValueChange = (idx, newVal) => {
    const newEntries = [...entries];
    newEntries[idx] = [newEntries[idx][0], newVal];
    onChange(Object.fromEntries(newEntries));
  };

  const handleAdd = () => {
    const defaultKey = `Specification ${entries.length + 1}`;
    onChange({ ...specs, [defaultKey]: "" });
  };

  const handleRemove = (idx) => {
    const newEntries = entries.filter((_, i) => i !== idx);
    onChange(Object.fromEntries(newEntries));
  };

  const handleMove = (idx, direction) => {
    const targetIdx = idx + direction;
    if (targetIdx < 0 || targetIdx >= entries.length) return;
    const newEntries = [...entries];
    const temp = newEntries[idx];
    newEntries[idx] = newEntries[targetIdx];
    newEntries[targetIdx] = temp;
    onChange(Object.fromEntries(newEntries));
  };

  const applyTemplate = (key) => {
    if (entries.length > 0 && !window.confirm("Replace current specifications with template presets?")) {
      return;
    }
    onChange(SPEC_TEMPLATES[key].specs);
  };

  const clearAll = () => {
    if (window.confirm("Clear all specification rows?")) {
      onChange({});
    }
  };

  return (
    <div className="space-y-4">
      {/* Template Quick Actions */}
      <div className="bg-black/40 border border-white/10 rounded-sm p-3.5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="mono text-[10px] text-white/50 uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-[#FF5722]" /> Quick Templates:
          </span>
          {Object.entries(SPEC_TEMPLATES).map(([k, t]) => (
            <button
              key={k}
              type="button"
              onClick={() => applyTemplate(k)}
              className="text-[11px] mono bg-white/5 hover:bg-[#FF5722]/15 text-white/80 hover:text-[#FF5722] border border-white/10 hover:border-[#FF5722]/40 px-2.5 py-1 rounded-xs transition-colors"
            >
              + {t.name}
            </button>
          ))}
        </div>
        {entries.length > 0 && (
          <button
            type="button"
            onClick={clearAll}
            className="text-[11px] mono text-red-400/60 hover:text-red-400 transition-colors"
          >
            Clear All ({entries.length})
          </button>
        )}
      </div>

      {/* Specification Table Editor */}
      <div className="border border-white/10 rounded-sm overflow-hidden bg-black/50">
        <div className="grid grid-cols-12 bg-[#121216] px-4 py-2.5 text-white/50 mono text-[10px] uppercase tracking-wider font-semibold border-b border-white/10">
          <div className="col-span-5 sm:col-span-4">Specification / Parameter</div>
          <div className="col-span-5 sm:col-span-6">Technical Value</div>
          <div className="col-span-2 text-right">Actions</div>
        </div>

        <div className="divide-y divide-white/5">
          {entries.length === 0 ? (
            <div className="p-8 text-center text-white/40 text-xs">
              No specifications added yet. Click <strong>"Add Spec Row"</strong> below or choose a <strong>Quick Template</strong> above.
            </div>
          ) : (
            entries.map(([key, val], idx) => (
              <div
                key={idx}
                className="grid grid-cols-12 items-center px-3 py-2 gap-2 hover:bg-white/3 transition-colors"
              >
                {/* Spec Key */}
                <div className="col-span-5 sm:col-span-4">
                  <input
                    type="text"
                    value={key}
                    onChange={(e) => handleKeyChange(idx, e.target.value)}
                    placeholder="e.g. Motor Power"
                    className="w-full bg-black/60 border border-white/15 text-white text-xs px-2.5 py-1.5 rounded-xs focus:outline-none focus:border-[#FF5722]"
                  />
                </div>

                {/* Spec Value */}
                <div className="col-span-5 sm:col-span-6">
                  <input
                    type="text"
                    value={val}
                    onChange={(e) => handleValueChange(idx, e.target.value)}
                    placeholder="e.g. 7.5 HP Heavy Gear Motor"
                    className="w-full bg-black/60 border border-white/15 text-white text-xs px-2.5 py-1.5 rounded-xs focus:outline-none focus:border-[#FF5722]"
                  />
                </div>

                {/* Row Actions */}
                <div className="col-span-2 flex items-center justify-end gap-1">
                  <button
                    type="button"
                    disabled={idx === 0}
                    onClick={() => handleMove(idx, -1)}
                    title="Move Up"
                    className="p-1 text-white/30 hover:text-white disabled:opacity-20 transition-colors"
                  >
                    <ArrowUp className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    disabled={idx === entries.length - 1}
                    onClick={() => handleMove(idx, 1)}
                    title="Move Down"
                    className="p-1 text-white/30 hover:text-white disabled:opacity-20 transition-colors"
                  >
                    <ArrowDown className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRemove(idx)}
                    title="Delete Row"
                    className="p-1 text-white/30 hover:text-red-400 rounded-xs hover:bg-red-400/10 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add Row Button */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={handleAdd}
          className="flex items-center gap-1.5 text-xs text-[#FF5722] hover:text-white border border-[#FF5722]/30 hover:border-[#FF5722] px-3.5 py-2 rounded-sm transition-all"
        >
          <Plus className="w-4 h-4" /> Add Specification Row
        </button>

        {entries.length > 0 && (
          <button
            type="button"
            onClick={() => setShowPreview(!showPreview)}
            className="flex items-center gap-1.5 text-xs text-white/50 hover:text-white transition-colors"
          >
            <Eye className="w-3.5 h-3.5" />
            {showPreview ? "Hide Live Table Preview" : "Show Live Table Preview"}
          </button>
        )}
      </div>

      {/* Live Table Preview */}
      {showPreview && entries.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="mono text-[10px] text-white/40 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Eye className="w-3 h-3 text-[#FF5722]" /> Customer-Facing Table Preview:
          </div>
          <div className="bg-[#09090B] border border-white/15 rounded-xs overflow-hidden">
            <div className="bg-[#121216] px-4 py-2.5 border-b border-white/10 flex items-center justify-between">
              <span className="mono text-xs tracking-wider uppercase text-[#FF5722] font-semibold flex items-center gap-2">
                <FileText className="w-3.5 h-3.5" /> Technical Specifications Matrix
              </span>
              <span className="text-[10px] mono text-white/40">Verified In-House</span>
            </div>
            <div className="divide-y divide-white/5 text-xs">
              {entries.map(([key, val]) => (
                <div key={key} className="grid grid-cols-1 sm:grid-cols-2 px-4 py-2.5 gap-1 hover:bg-white/5 transition-colors">
                  <span className="text-white/50 mono text-[10px] uppercase tracking-wider">{key}</span>
                  <span className="text-white font-medium">{val || "—"}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// Gallery Uploader — up to 5 image URLs per product
// -------------------------------------------------------------
function GalleryUploader({ images, onChange }) {
  const MAX = 5;
  const [urlInput, setUrlInput] = useState("");
  const [urlError, setUrlError] = useState("");

  const addUrl = () => {
    let trimmed = urlInput.trim();
    if (!trimmed) return;
    if (images.length >= MAX) {
      setUrlError(`Maximum ${MAX} photos allowed.`);
      return;
    }
    trimmed = normalizeImageUrl(trimmed);
    try { new URL(trimmed); } catch { setUrlError("Please enter a valid URL."); return; }
    setUrlError("");
    onChange([...images, trimmed]);
    setUrlInput("");
  };

  const remove = (idx) => onChange(images.filter((_, i) => i !== idx));

  const moveUp = (idx) => {
    if (idx === 0) return;
    const next = [...images];
    [next[idx - 1], next[idx]] = [next[idx], next[idx - 1]];
    onChange(next);
  };

  const moveDown = (idx) => {
    if (idx === images.length - 1) return;
    const next = [...images];
    [next[idx], next[idx + 1]] = [next[idx + 1], next[idx]];
    onChange(next);
  };

  const FALLBACK = "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg";

  return (
    <div className="space-y-4">
      {/* Current images grid */}
      {images.length > 0 && (
        <div className="space-y-2">
          {images.map((url, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 bg-black/40 border border-white/10 rounded-xs p-2"
            >
              {/* Thumbnail */}
              <div className="shrink-0 w-14 h-12 bg-[#0c0c0e] border border-white/10 rounded-xs overflow-hidden flex items-center justify-center">
                <img
                  src={url}
                  alt={`Photo ${idx + 1}`}
                  className="w-full h-full object-contain"
                  onError={(e) => { e.currentTarget.src = FALLBACK; }}
                />
              </div>

              {/* Label */}
              <div className="flex-1 min-w-0">
                {idx === 0 && (
                  <span className="inline-block bg-[#FF5722] text-white mono text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded-xs mb-0.5">★ Primary</span>
                )}
                <p className="mono text-[11px] text-white/50 truncate">{url}</p>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-0.5 shrink-0">
                <button type="button" onClick={() => moveUp(idx)} disabled={idx === 0}
                  className="p-1 text-white/30 hover:text-white disabled:opacity-20 transition-colors" title="Move up">
                  <ArrowUp className="w-3.5 h-3.5" />
                </button>
                <button type="button" onClick={() => moveDown(idx)} disabled={idx === images.length - 1}
                  className="p-1 text-white/30 hover:text-white disabled:opacity-20 transition-colors" title="Move down">
                  <ArrowDown className="w-3.5 h-3.5" />
                </button>
                <button type="button" onClick={() => remove(idx)}
                  className="p-1 text-white/30 hover:text-red-400 transition-colors" title="Remove">
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add URL input */}
      {images.length < MAX ? (
        <div className="space-y-2">
          <label className="block mono text-[10px] text-white/50 uppercase tracking-wider">
            Add Photo URL ({images.length}/{MAX})
          </label>
          <div className="flex gap-2">
            <input
              type="url"
              value={urlInput}
              onChange={(e) => { setUrlInput(e.target.value); setUrlError(""); }}
              onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addUrl())}
              placeholder="https://5.imimg.com/data5/... or any CDN image URL"
              className="flex-1 bg-black/60 border border-white/15 text-white text-sm px-3.5 py-2.5 rounded-sm focus:outline-none focus:border-[#FF5722]"
            />
            <button
              type="button"
              onClick={addUrl}
              disabled={!urlInput.trim()}
              className="flex items-center gap-1.5 px-4 py-2.5 bg-[#FF5722] hover:bg-[#F4511E] text-white text-xs font-semibold uppercase tracking-wider rounded-sm transition-colors disabled:opacity-40"
            >
              <Plus className="w-4 h-4" /> Add
            </button>
          </div>
          {urlError && <p className="text-red-400 text-xs">{urlError}</p>}
          <p className="mono text-[10px] text-white/40">First photo is the primary/cover image. Reorder using arrows. Max {MAX} photos.</p>
        </div>
      ) : (
        <div className="bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs px-3 py-2 rounded-xs">
          Maximum {MAX} photos reached. Remove one to add another.
        </div>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// YouTube Video URL field
// -------------------------------------------------------------
function VideoUrlField({ value, onChange }) {
  const [error, setError] = useState("");

  const extractVideoId = (url) => {
    if (!url) return null;
    const m =
      url.match(/[?&]v=([^&#]+)/) ||
      url.match(/youtu\.be\/([^?&#]+)/) ||
      url.match(/\/shorts\/([^?&#]+)/);
    return m ? m[1] : null;
  };

  const handleBlur = () => {
    if (!value) { setError(""); return; }
    const vid = extractVideoId(value);
    if (!vid) {
      setError("Not a valid YouTube URL. Use youtube.com/watch?v=..., youtu.be/..., or youtube.com/shorts/...");
    } else {
      setError("");
    }
  };

  const videoId = extractVideoId(value);

  return (
    <div className="space-y-3">
      <div className="flex gap-3 items-start">
        <div className="flex-1">
          <input
            type="url"
            value={value}
            onChange={(e) => { onChange(e.target.value); setError(""); }}
            onBlur={handleBlur}
            placeholder="https://www.youtube.com/watch?v=XXXXXXXXXXX"
            className={`w-full bg-black/60 border text-white text-sm px-3.5 py-2.5 rounded-sm focus:outline-none ${
              error ? "border-red-500" : "border-white/15 focus:border-[#FF5722]"
            }`}
          />
          {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
        </div>
        {value && (
          <button
            type="button"
            onClick={() => onChange("")}
            className="p-2.5 text-white/40 hover:text-red-400 border border-white/10 rounded-xs transition-colors shrink-0"
            title="Clear video URL"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Live thumbnail preview */}
      {videoId && !error && (
        <div className="flex items-center gap-3 bg-black/40 border border-white/10 rounded-xs p-2">
          <div className="shrink-0 w-24 h-16 bg-[#0c0c0e] border border-white/10 rounded-xs overflow-hidden relative">
            <img
              src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
              alt="YouTube thumbnail"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-7 h-7 rounded-full bg-[#FF5722]/90 flex items-center justify-center">
                <Eye className="w-3.5 h-3.5 text-white" />
              </div>
            </div>
          </div>
          <div className="min-w-0">
            <span className="mono text-xs text-green-400 flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5" /> Valid YouTube URL
            </span>
            <p className="mono text-[11px] text-white/40 truncate mt-0.5">ID: {videoId}</p>
          </div>
        </div>
      )}

      <p className="mono text-[10px] text-white/40">Optional. Paste a YouTube watch link. The video will play inline on the product page — never redirects to YouTube.com.</p>
    </div>
  );
}

// -------------------------------------------------------------
// FAQs Editor Component
// -------------------------------------------------------------
function FAQsEditor({ faqs, onChange }) {
  const handleChange = (idx, field, val) => {
    const updated = faqs.map((f, i) => i === idx ? { ...f, [field]: val } : f);
    onChange(updated);
  };

  const handleAdd = () => {
    onChange([...faqs, { q: "", a: "" }]);
  };

  const handleRemove = (idx) => {
    onChange(faqs.filter((_, i) => i !== idx));
  };

  return (
    <div className="space-y-4">
      {faqs.map((faq, idx) => (
        <div key={idx} className="bg-black/30 border border-white/10 rounded-sm p-4 space-y-3">
          <div className="flex items-start justify-between gap-2">
            <span className="mono text-[10px] text-[#FF5722] uppercase tracking-wider">FAQ #{idx + 1}</span>
            <button
              type="button"
              onClick={() => handleRemove(idx)}
              className="p-1 text-white/30 hover:text-red-400 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
          <div>
            <label className="block mono text-[10px] text-white/50 uppercase tracking-wider mb-1">Question</label>
            <input
              type="text"
              value={faq.q}
              onChange={(e) => handleChange(idx, "q", e.target.value)}
              placeholder="e.g. What is the daily output capacity?"
              className="w-full bg-black/60 border border-white/15 text-white text-sm px-3 py-2 rounded-sm focus:outline-none focus:border-[#FF5722]"
            />
          </div>
          <div>
            <label className="block mono text-[10px] text-white/50 uppercase tracking-wider mb-1">Answer</label>
            <textarea
              rows={3}
              value={faq.a}
              onChange={(e) => handleChange(idx, "a", e.target.value)}
              placeholder="Detailed answer..."
              className="w-full bg-black/60 border border-white/15 text-white text-sm px-3 py-2 rounded-sm focus:outline-none focus:border-[#FF5722] resize-none"
            />
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={handleAdd}
        className="flex items-center gap-1.5 text-xs text-[#FF5722] hover:text-white border border-[#FF5722]/30 hover:border-[#FF5722] px-3 py-1.5 rounded-sm transition-all"
      >
        <Plus className="w-3.5 h-3.5" /> Add FAQ
      </button>
    </div>
  );
}

// -------------------------------------------------------------
// Main Product Form Page
// -------------------------------------------------------------
export default function AdminProductForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { getAuthHeader } = useAdminAuth();

  const isEdit = Boolean(id);

  const [form, setForm] = useState(EMPTY_PRODUCT);
  const [specs, setSpecs] = useState({});
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(isEdit);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // JSON bulk import state
  const [bulkJson, setBulkJson] = useState("");
  const [showBulkImport, setShowBulkImport] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);

  useEffect(() => {
    if (!isEdit) return;

    const fetchProduct = async () => {
      try {
        let p = null;
        try {
          const res = await fetch(`${BACKEND_URL}/api/admin/products/${id}`, {
            headers: getAuthHeader(),
          });
          if (res.ok) {
            const data = await res.json();
            p = data.product;
          }
        } catch (e) {
          // Fall through to catalogue lookup
        }

        // Fallback 1: check static catalogue
        if (!p) {
          p = CATALOGUE_PRODUCTS.find((item) => item.id === id);
        }

        // Fallback 2: check localStorage admin cache
        if (!p) {
          try {
            const localProducts = JSON.parse(localStorage.getItem("gagan_custom_products") || "[]");
            p = localProducts.find((item) => item.id === id);
          } catch (e) {}
        }

        if (!p) throw new Error("Not found");

        setForm({
          name: p.name || "",
          category: p.category || "Roll Forming & Sheet Metal",
          categorySlug: p.categorySlug || "roll-forming-sheet-metal",
          image: p.image || "",
          images: Array.isArray(p.images) ? p.images : [],
          video_url: p.video_url || "",
          tagline: p.tagline || "",
          shortDesc: p.shortDesc || p.short_description || "",
          description: p.description || "",
          featured: p.featured || false,
        });
        setSpecs(p.specs || {});
        setFaqs(p.faqs || []);
      } catch (err) {
        setError("Could not load product for editing. Please check your connection and try again.");
      } finally {
        setFetching(false);
      }
    };

    fetchProduct();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, isEdit]);

  const handleCategoryChange = (slug) => {
    const cat = CATEGORY_OPTIONS.find((c) => c.slug === slug);
    setForm((f) => ({ ...f, categorySlug: slug, category: cat ? cat.name : f.category }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name) {
      setError("Product name is required.");
      return;
    }
    if (!form.image && form.images.length === 0) {
      setError("Please add at least one product photo (URL).");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    const payload = {
      ...form,
      specs,
      faqs,
      // Sync legacy image field: keep as first image for backward compat
      image: form.images[0] || form.image || "",
      images: form.images.length > 0 ? form.images : (form.image ? [form.image] : []),
      video_url: form.video_url || null,
    };

    try {
      const url = isEdit
        ? `${BACKEND_URL}/api/admin/products/${id}`
        : `${BACKEND_URL}/api/admin/products`;
      const method = isEdit ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { ...getAuthHeader(), "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok) {
        // ✅ Server confirmed the save — also update local cache for instant UI feedback
        try {
          const stored = JSON.parse(localStorage.getItem("gagan_custom_products") || "[]");
          const prodId = isEdit ? id : (data?.product?.id || form.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"));
          const savedProduct = data?.product ? { ...data.product } : { ...payload, id: prodId };
          const filtered = stored.filter((item) => item.id !== savedProduct.id);
          localStorage.setItem("gagan_custom_products", JSON.stringify([...filtered, savedProduct]));
        } catch (e) {}

        setSuccess(isEdit ? "✅ Product updated successfully! Changes are live." : "✅ Product created successfully!");
        if (!isEdit) {
          setTimeout(() => navigate("/admin/products"), 1500);
        }
      } else if (res.status === 401) {
        setError("Authentication failed. Please log out and log in again.");
      } else {
        // API failed — save locally as fallback
        try {
          const stored = JSON.parse(localStorage.getItem("gagan_custom_products") || "[]");
          const prodId = isEdit ? id : form.name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
          const updatedItem = { ...payload, id: prodId };
          const filtered = stored.filter((item) => item.id !== prodId);
          localStorage.setItem("gagan_custom_products", JSON.stringify([...filtered, updatedItem]));
          setSuccess(`⚠️ ${isEdit ? "Updated" : "Created"} (saved to local cache — server error: ${data?.detail || res.status}).`);
          if (!isEdit) {
            setTimeout(() => navigate("/admin/products"), 2000);
          }
        } catch (e) {
          setError(`Server error (${res.status}): ${data?.detail || "Could not save product."}`);
        }
      }
    } catch (err) {
      // Network offline — fallback save to localStorage
      try {
        const stored = JSON.parse(localStorage.getItem("gagan_custom_products") || "[]");
        const prodId = isEdit ? id : form.name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
        const updatedItem = { ...payload, id: prodId };
        const filtered = stored.filter((item) => item.id !== prodId);
        localStorage.setItem("gagan_custom_products", JSON.stringify([...filtered, updatedItem]));
        setSuccess(`⚠️ ${isEdit ? "Updated" : "Created"} locally (offline mode — will sync when reconnected).`);
        if (!isEdit) {
          setTimeout(() => navigate("/admin/products"), 2000);
        }
      } catch (e) {
        setError(`Network error: ${err.message || "Could not save product."}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleBulkImport = async () => {
    let parsed;
    try {
      parsed = JSON.parse(bulkJson);
      if (!Array.isArray(parsed)) parsed = [parsed];
    } catch {
      setError("Invalid JSON. Please paste a valid JSON array of products.");
      return;
    }

    setImporting(true);
    setImportResult(null);
    setError("");

    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/products/import`, {
        method: "POST",
        headers: { ...getAuthHeader(), "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      const data = await res.json();
      setImportResult(data);
      setBulkJson("");
    } catch (err) {
      setError("Import failed. Check your backend connection.");
    } finally {
      setImporting(false);
    }
  };

  if (fetching) {
    return (
      <div className="flex items-center justify-center min-h-[300px] text-white/40">
        <Loader2 className="w-6 h-6 animate-spin mr-3" />
        Loading product specifications...
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link
          to="/admin/products"
          className="p-2 text-white/50 hover:text-white border border-white/10 hover:border-white/30 rounded-sm transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="font-display text-3xl text-white tracking-wider uppercase">
            {isEdit ? "Edit Machinery Product" : "Add New Machinery Product"}
          </h1>
          <p className="mono text-xs text-white/40 mt-1 uppercase tracking-wider">
            {isEdit ? `Editing ID: ${id}` : "Configure machine listing, images, specs table, and FAQs"}
          </p>
        </div>
      </div>

      {/* Bulk Import Toggle (only for new) */}
      {!isEdit && (
        <div className="mb-6">
          <button
            type="button"
            onClick={() => setShowBulkImport(!showBulkImport)}
            className="flex items-center gap-2 text-sm text-[#FF5722] border border-[#FF5722]/30 hover:border-[#FF5722] px-4 py-2 rounded-sm transition-all"
          >
            <Upload className="w-4 h-4" />
            {showBulkImport ? "Hide Bulk Import" : "Bulk Import from JSON"}
            {showBulkImport ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showBulkImport && (
            <div className="mt-3 bg-[#09090B] border border-white/10 rounded-sm p-5 space-y-4">
              <div>
                <div className="mono text-xs text-[#FF5722] uppercase tracking-wider mb-2">
                  Paste JSON array of products (format matches the product schema)
                </div>
                <textarea
                  rows={8}
                  value={bulkJson}
                  onChange={(e) => setBulkJson(e.target.value)}
                  placeholder='[{"name":"My Machine","category":"Roll Forming & Sheet Metal","categorySlug":"roll-forming-sheet-metal","image":"https://...","specs":{"Motor Power":"7.5 HP"},"featured":false}]'
                  className="w-full bg-black/60 border border-white/15 text-white text-xs font-mono px-4 py-3 rounded-sm focus:outline-none focus:border-[#FF5722] resize-y"
                />
              </div>
              {importResult && (
                <div className={`text-sm px-4 py-3 rounded-sm border ${importResult.created > 0 ? "bg-green-500/10 border-green-500/30 text-green-400" : "bg-yellow-500/10 border-yellow-500/30 text-yellow-400"}`}>
                  ✓ Imported {importResult.created} products.
                  {importResult.skipped > 0 && ` Skipped ${importResult.skipped} duplicates (${importResult.skipped_ids.join(", ")}).`}
                </div>
              )}
              <button
                type="button"
                onClick={handleBulkImport}
                disabled={importing || !bulkJson.trim()}
                className="flex items-center gap-2 bg-[#FF5722] hover:bg-[#F4511E] text-white font-semibold text-xs uppercase tracking-wider px-5 py-2.5 rounded-sm transition-colors disabled:opacity-50"
              >
                {importing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                {importing ? "Importing..." : "Import Products"}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-500/10 border border-green-500/30 text-green-400 text-sm px-4 py-3 rounded-sm">
            ✓ {success}
          </div>
        )}

        {/* 1. Basic Info */}
        <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 space-y-5">
          <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] mb-1 flex items-center gap-2">
            <FileText className="w-4 h-4" /> Basic Machine Information
          </div>

          <div className="grid sm:grid-cols-2 gap-5">
            <div className="sm:col-span-2">
              <label className="block mono text-[10px] text-white/50 uppercase tracking-wider mb-1.5">
                Product Name <span className="text-[#FF5722]">*</span>
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                placeholder="e.g. Double Head Electric Bra Cup Moulding Machine"
                className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-sm focus:outline-none focus:border-[#FF5722]"
              />
            </div>

            <div>
              <label className="block mono text-[10px] text-white/50 uppercase tracking-wider mb-1.5">
                Category <span className="text-[#FF5722]">*</span>
              </label>
              <select
                value={form.categorySlug}
                onChange={(e) => handleCategoryChange(e.target.value)}
                className="w-full bg-black/60 border border-white/15 text-white text-sm px-3 py-3 rounded-sm focus:outline-none focus:border-[#FF5722]"
              >
                {CATEGORY_OPTIONS.map((c) => (
                  <option key={c.slug} value={c.slug}>{c.name}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-3 pt-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <div
                  onClick={() => setForm({ ...form, featured: !form.featured })}
                  className={`relative w-11 h-6 rounded-full transition-colors cursor-pointer ${
                    form.featured ? "bg-[#FF5722]" : "bg-white/10"
                  }`}
                >
                  <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                    form.featured ? "translate-x-6" : "translate-x-1"
                  }`} />
                </div>
                <span className="text-sm text-white/70">Featured on Home Page</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block mono text-[10px] text-white/50 uppercase tracking-wider mb-1.5">
              Tagline (Short Highlight)
            </label>
            <input
              type="text"
              value={form.tagline}
              onChange={(e) => setForm({ ...form, tagline: e.target.value })}
              placeholder="e.g. Twin-station high-output cup moulding for industrial lingerie production lines"
              className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-sm focus:outline-none focus:border-[#FF5722]"
            />
          </div>

          <div>
            <label className="block mono text-[10px] text-white/50 uppercase tracking-wider mb-1.5">
              Short Description (Card Summary)
            </label>
            <textarea
              rows={2}
              value={form.shortDesc}
              onChange={(e) => setForm({ ...form, shortDesc: e.target.value })}
              placeholder="2-3 sentence overview for product card..."
              className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-sm focus:outline-none focus:border-[#FF5722] resize-none"
            />
          </div>

          <div>
            <label className="block mono text-[10px] text-white/50 uppercase tracking-wider mb-1.5">
              Full Description (Detail Page Overview)
            </label>
            <textarea
              rows={5}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Complete technical description of the machine operation, construction, and benefits..."
              className="w-full bg-black/60 border border-white/15 text-white text-sm px-4 py-3 rounded-sm focus:outline-none focus:border-[#FF5722]"
            />
          </div>
        </div>

        {/* 2. Photo Gallery */}
        <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 space-y-4">
          <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] mb-1 flex items-center gap-2">
            <ImageIcon className="w-4 h-4" /> Product Photos (up to 5)
          </div>
          <p className="text-xs text-white/50">Add photos via IndiaMART, Google Drive, or any public CDN URL. First photo is the primary/cover image.</p>
          <GalleryUploader
            images={form.images.length > 0 ? form.images : (form.image ? [form.image] : [])}
            onChange={(imgs) => setForm({ ...form, images: imgs, image: imgs[0] || "" })}
          />
        </div>

        {/* 3. Product Video (YouTube) */}
        <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 space-y-4">
          <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] mb-1 flex items-center gap-2">
            <Eye className="w-4 h-4" /> Machine Video (YouTube — Optional)
          </div>
          <VideoUrlField
            value={form.video_url}
            onChange={(val) => setForm({ ...form, video_url: val })}
          />
        </div>

        {/* 3. Specification Table Builder */}
        <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 space-y-4">
          <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] mb-1 flex items-center gap-2">
            <FileText className="w-4 h-4" /> Technical Specification Table
          </div>
          <p className="text-xs text-white/60">
            Define technical parameters (e.g., Motor Power, Tonnage, Material Thickness, Dimensions, Origin).
          </p>
          <SpecificationTableBuilder
            specs={specs}
            onChange={setSpecs}
          />
        </div>

        {/* 4. FAQs */}
        <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 space-y-4">
          <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] mb-1 flex items-center gap-2">
            <HelpCircle className="w-4 h-4" /> Technical FAQs (Optional — Generates Google SERP Schema)
          </div>
          <FAQsEditor faqs={faqs} onChange={setFaqs} />
        </div>

        {/* 5. Submit Controls */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-4 border-t border-white/10">
          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto flex items-center justify-center gap-2 bg-[#FF5722] hover:bg-[#F4511E] text-white font-semibold text-sm uppercase tracking-wider px-8 py-3.5 rounded-sm transition-colors disabled:opacity-60"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {loading ? "Saving Product..." : isEdit ? "Update Product" : "Publish Machinery Product"}
          </button>
          <Link
            to="/admin/products"
            className="w-full sm:w-auto text-center text-sm text-white/50 hover:text-white/80 border border-white/10 hover:border-white/30 px-6 py-3.5 rounded-sm transition-all"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
