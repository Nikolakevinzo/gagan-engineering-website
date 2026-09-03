import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft, Save, Upload, Plus, Trash2, MoveUp, MoveDown,
  Eye, Edit3, Image as ImageIcon, Calendar, Clock, Tag,
  Layers, CheckCircle2, AlertCircle, Table, BookOpen, ExternalLink,
  HelpCircle, RefreshCw
} from "lucide-react";
import { toast } from "sonner";
import { useAdminAuth } from "@/components/AdminLayout";
import { BLOG_ARTICLES, BLOG_CATEGORIES } from "@/lib/blogData";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";

const STANDARD_CATEGORIES = [
  { name: "Roll Forming & PEB Framing", slug: "roll-forming" },
  { name: "Coil Processing & Metal Forming", slug: "coil-processing" },
  { name: "Intimate Wear Technology", slug: "intimate-wear-tech" },
  { name: "Machinery Export & Logistics", slug: "export-logistics" },
  { name: "General Engineering Guides", slug: "general" }
];

export default function AdminBlogForm() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { getAuthHeader } = useAdminAuth();

  const isEditMode = Boolean(slug);
  const [activeTab, setActiveTab] = useState("editor"); // 'editor' | 'preview'
  const [loading, setLoading] = useState(isEditMode);
  const [saving, setSaving] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    title: "",
    slug: "",
    summary: "",
    category: "Roll Forming & PEB Framing",
    categorySlug: "roll-forming",
    date: new Date().toISOString().split("T")[0],
    readTime: "7 min read",
    author: "Gagan Engineering Works Technical Desk",
    image: "",
    targetKeywords: "",
    tags: ["Machinery", "Roll Forming", "Gagan Engineering"],
    relatedProducts: ["corrugated-sheets-making-machine"],
    published: true,
    content: [
      {
        type: "section",
        id: "intro",
        heading: "Introduction",
        text: "Write your opening technical background and engineering overview here...",
        items: []
      }
    ]
  });

  const [newTagInput, setNewTagInput] = useState("");

  // Load existing article if in edit mode
  useEffect(() => {
    if (!isEditMode) return;

    const fetchArticle = async () => {
      setLoading(true);

      const applyLocalOverride = (art) => {
        try {
          const stored = JSON.parse(localStorage.getItem("gagan_custom_blogs") || "[]");
          const local = stored.find((b) => b.slug === slug);
          if (local) return { ...art, ...local };
        } catch (e) {}
        return art;
      };

      try {
        const res = await fetch(`/api/admin/blogs/${slug}`, {
          headers: getAuthHeader()
        });
        if (res.ok) {
          const data = await res.json();
          if (data.article) {
            const finalArt = applyLocalOverride(data.article);
            setFormData({
              ...finalArt,
              published: finalArt.published !== false,
              tags: finalArt.tags || [],
              relatedProducts: finalArt.relatedProducts || [],
              content: finalArt.content || []
            });
          }
        } else {
          // Fallback to static blogData
          const staticMatch = BLOG_ARTICLES.find((a) => a.slug === slug);
          if (staticMatch) {
            const finalArt = applyLocalOverride(staticMatch);
            setFormData({
              ...finalArt,
              published: true,
              tags: finalArt.tags || [],
              relatedProducts: finalArt.relatedProducts || [],
              content: finalArt.content || []
            });
          } else {
            toast.error("Article not found.");
            navigate("/admin/blogs");
          }
        }
      } catch (err) {
        console.warn("Failed to fetch from API, falling back to static:", err);
        const staticMatch = BLOG_ARTICLES.find((a) => a.slug === slug);
        if (staticMatch) {
          const finalArt = applyLocalOverride(staticMatch);
          setFormData({
            ...finalArt,
            published: true,
            tags: finalArt.tags || [],
            relatedProducts: finalArt.relatedProducts || [],
            content: finalArt.content || []
          });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isEditMode, slug, navigate]);

  // Title change: Auto-generate slug if new or untouched
  const handleTitleChange = (val) => {
    setFormData((prev) => {
      const updates = { title: val };
      if (!isEditMode || !prev.slug) {
        updates.slug = val
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-+|-+$/g, "");
      }
      return { ...prev, ...updates };
    });
  };

  // Category change
  const handleCategoryChange = (catName) => {
    const found = STANDARD_CATEGORIES.find((c) => c.name === catName);
    setFormData((prev) => ({
      ...prev,
      category: catName,
      categorySlug: found ? found.slug : catName.toLowerCase().replace(/[^a-z0-9]+/g, "-")
    }));
  };

  // Tag Management
  const handleAddTag = () => {
    const trimmed = newTagInput.trim();
    if (!trimmed) return;
    if (!formData.tags.includes(trimmed)) {
      setFormData((prev) => ({
        ...prev,
        tags: [...prev.tags, trimmed]
      }));
    }
    setNewTagInput("");
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData((prev) => ({
      ...prev,
      tags: prev.tags.filter((t) => t !== tagToRemove)
    }));
  };

  // Image Upload
  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingImage(true);
    const body = new FormData();
    body.append("file", file);

    try {
      const res = await fetch("/api/admin/upload-image", {
        method: "POST",
        headers: getAuthHeader(),
        body
      });
      if (res.ok) {
        const data = await res.json();
        setFormData((prev) => ({ ...prev, image: data.url }));
        toast.success("Cover image uploaded successfully!");
      } else {
        const err = await res.json();
        toast.error(err.detail || "Image upload failed.");
      }
    } catch (e) {
      toast.error("Network error during image upload.");
    } finally {
      setUploadingImage(false);
    }
  };

  // Content Sections Management
  const addTextSection = () => {
    const newSection = {
      type: "section",
      id: `sec-${Date.now()}`,
      heading: "New Heading",
      text: "Enter detailed technical information and engineering data here...",
      items: []
    };
    setFormData((prev) => ({ ...prev, content: [...prev.content, newSection] }));
  };

  const addTableSection = () => {
    const newTable = {
      type: "table",
      id: `table-${Date.now()}`,
      heading: "Technical Comparison Table",
      headers: ["Parameter", "Industry Standard", "Gagan Engineering Spec"],
      rows: [
        ["Motor Power", "3.0 HP", "5.0 HP Geared Drive"],
        ["Tooling Steel", "Mild Steel 45#", "Hardened EN31 / Cr12"]
      ]
    };
    setFormData((prev) => ({ ...prev, content: [...prev.content, newTable] }));
  };

  const updateSection = (index, updatedSection) => {
    setFormData((prev) => {
      const updatedContent = [...prev.content];
      updatedContent[index] = updatedSection;
      return { ...prev, content: updatedContent };
    });
  };

  const removeSection = (index) => {
    if (formData.content.length <= 1) {
      toast.error("Articles must contain at least one content section.");
      return;
    }
    setFormData((prev) => ({
      ...prev,
      content: prev.content.filter((_, i) => i !== index)
    }));
  };

  const moveSection = (index, direction) => {
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= formData.content.length) return;
    setFormData((prev) => {
      const copy = [...prev.content];
      const [moved] = copy.splice(index, 1);
      copy.splice(targetIndex, 0, moved);
      return { ...prev, content: copy };
    });
  };

  // Submit Handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      toast.error("Please provide an article title.");
      return;
    }
    if (!formData.slug.trim()) {
      toast.error("Please provide a valid URL slug.");
      return;
    }
    if (!formData.summary.trim()) {
      toast.error("Please provide a summary for SEO meta descriptions.");
      return;
    }

    // Auto-generate Table of Contents from headings
    const tableOfContents = formData.content
      .filter((sec) => sec.heading)
      .map((sec, idx) => ({
        id: sec.id || `section-${idx}`,
        title: sec.heading
      }));

    const payload = {
      ...formData,
      tableOfContents
    };

    setSaving(true);
    try {
      const url = isEditMode
        ? `/api/admin/blogs/${slug}`
        : "/api/admin/blogs";
      const method = isEditMode ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          ...getAuthHeader(),
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        // Also save to localStorage for immediate frontend sync
        try {
          const stored = JSON.parse(localStorage.getItem("gagan_custom_blogs") || "[]");
          const filtered = stored.filter((b) => b.slug !== payload.slug);
          localStorage.setItem("gagan_custom_blogs", JSON.stringify([...filtered, payload]));
        } catch (e) {}
        toast.success(isEditMode ? "Article updated successfully!" : "New article published successfully!");
        navigate("/admin/blogs");
      } else {
        // API failed (e.g. 401 auth mismatch) — save locally so frontend picks it up
        try {
          const stored = JSON.parse(localStorage.getItem("gagan_custom_blogs") || "[]");
          const filtered = stored.filter((b) => b.slug !== payload.slug);
          localStorage.setItem("gagan_custom_blogs", JSON.stringify([...filtered, payload]));
        } catch (e) {}
        toast.warning("Saved locally. Server sync failed — check admin credentials in Vercel environment variables.");
        navigate("/admin/blogs");
      }
    } catch (err) {
      // Network error — save locally
      try {
        const stored = JSON.parse(localStorage.getItem("gagan_custom_blogs") || "[]");
        const filtered = stored.filter((b) => b.slug !== payload.slug);
        localStorage.setItem("gagan_custom_blogs", JSON.stringify([...filtered, payload]));
      } catch (e) {}
      toast.warning("Saved locally (offline). Changes will sync when server is available.");
      navigate("/admin/blogs");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center text-white/40 mono text-xs flex flex-col items-center gap-3">
        <RefreshCw className="w-6 h-6 animate-spin text-[#FF5722]" />
        <span>Loading publication editor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Link
            to="/admin/blogs"
            className="inline-flex items-center gap-1.5 mono text-[10px] text-white/50 hover:text-white transition-colors uppercase tracking-wider"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Articles List
          </Link>
          <h1 className="font-display text-2xl sm:text-3xl text-white uppercase tracking-wider">
            {isEditMode ? "Edit Technical Publication" : "Create New Publication"}
          </h1>
          <p className="text-white/50 text-xs sm:text-sm">
            {isEditMode
              ? `Editing /blog/${formData.slug}`
              : "Drafting a high-intent technical publication to outrank competitors on Google."}
          </p>
        </div>

        {/* Action Controls & Tab Switcher */}
        <div className="flex items-center gap-3">
          <div className="bg-[#121216] border border-white/10 p-1 rounded-xs flex items-center">
            <button
              type="button"
              onClick={() => setActiveTab("editor")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-xs font-medium transition-colors ${
                activeTab === "editor"
                  ? "bg-[#FF5722] text-white"
                  : "text-white/60 hover:text-white"
              }`}
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Editor</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("preview")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-xs font-medium transition-colors ${
                activeTab === "preview"
                  ? "bg-[#FF5722] text-white"
                  : "text-white/60 hover:text-white"
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Live Preview</span>
            </button>
          </div>

          <button
            onClick={handleSubmit}
            disabled={saving}
            className="btn-primary flex items-center gap-2 text-xs py-2 px-5 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? "Saving..." : isEditMode ? "Update Article" : "Publish Article"}</span>
          </button>
        </div>
      </div>

      {activeTab === "preview" ? (
        /* ------------------ LIVE PREVIEW TAB ------------------ */
        <div className="space-y-8 bg-[#09090B] border border-white/10 rounded-xs p-6 sm:p-10 shadow-2xl">
          <div className="flex items-center gap-2 mono text-xs text-[#FF5722] uppercase tracking-wider">
            <Eye className="w-4 h-4" />
            <span>Live Article Preview</span>
          </div>

          {/* Article Header */}
          <div className="space-y-4 border-b border-white/10 pb-8">
            <div className="flex flex-wrap items-center gap-2">
              <span className="mono text-[10px] uppercase tracking-wider bg-[#FF5722]/15 text-[#FF5722] border border-[#FF5722]/30 px-2.5 py-0.5 rounded-xs">
                {formData.category}
              </span>
              <span className="text-white/40 text-xs">·</span>
              <span className="text-white/50 text-xs mono flex items-center gap-1">
                <Calendar className="w-3 h-3 text-[#FF5722]" /> {formData.date}
              </span>
              <span className="text-white/40 text-xs">·</span>
              <span className="text-white/50 text-xs mono flex items-center gap-1">
                <Clock className="w-3 h-3" /> {formData.readTime}
              </span>
            </div>

            <h1 className="font-display text-3xl sm:text-4xl text-white uppercase tracking-wide leading-tight">
              {formData.title || "Untitled Technical Publication"}
            </h1>

            <p className="text-white/70 text-sm sm:text-base leading-relaxed max-w-3xl">
              {formData.summary || "Summary of the publication..."}
            </p>
          </div>

          {/* Featured Cover Image */}
          {formData.image && (
            <div className="w-full h-80 bg-[#121216] border border-white/10 rounded-xs overflow-hidden">
              <img
                src={formData.image}
                alt={formData.title}
                onError={(e) => { e.currentTarget.src = "/logo.png"; }}
                className="w-full h-full object-contain p-4"
              />
            </div>
          )}

          {/* Render Sections */}
          <div className="space-y-8 pt-4">
            {formData.content.map((sec, idx) => {
              if (sec.type === "section") {
                return (
                  <div key={idx} className="space-y-3">
                    <h2 className="font-display text-2xl text-white uppercase tracking-wide border-b border-white/10 pb-2">
                      {sec.heading}
                    </h2>
                    <p className="text-white/80 text-sm leading-relaxed whitespace-pre-line">
                      {sec.text}
                    </p>
                    {sec.items && sec.items.length > 0 && (
                      <ul className="space-y-2 pt-1 text-sm text-white/80">
                        {sec.items.map((item, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-[#FF5722] font-bold">▸</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                );
              }

              if (sec.type === "table") {
                return (
                  <div key={idx} className="space-y-3">
                    <h3 className="font-display text-xl text-[#FF5722] uppercase tracking-wider">
                      {sec.heading}
                    </h3>
                    <div className="overflow-x-auto border border-white/10 rounded-xs">
                      <table className="w-full text-left text-xs sm:text-sm">
                        <thead className="bg-[#121216] border-b border-white/10 text-[#FF5722] mono text-[10px] uppercase">
                          <tr>
                            {sec.headers?.map((h, hi) => (
                              <th key={hi} className="px-4 py-3 font-semibold">{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {sec.rows?.map((row, ri) => (
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
          </div>
        </div>
      ) : (
        /* ------------------ EDITOR FORM TAB ------------------ */
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Card 1: Core Publication Details */}
          <div className="bg-[#09090B] border border-white/10 rounded-xs p-6 space-y-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="mono text-[11px] uppercase tracking-wider text-[#FF5722] flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                <span>1. Article Meta & Publication Settings</span>
              </div>

              <div className="flex items-center gap-2">
                <label className="mono text-xs text-white/60">Status:</label>
                <button
                  type="button"
                  onClick={() => setFormData((prev) => ({ ...prev, published: !prev.published }))}
                  className={`mono text-[10px] uppercase tracking-wider px-3 py-1 rounded-xs font-semibold transition-colors ${
                    formData.published
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                      : "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                  }`}
                >
                  {formData.published ? "✓ Published" : "Draft"}
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-white mb-1.5">
                  Article Title <span className="text-[#FF5722]">*</span>
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleTitleChange(e.target.value)}
                  placeholder="e.g. Complete Guide to Corrugated Sheet Making Machines (2026)"
                  className="w-full bg-[#121216] border border-white/10 rounded-xs px-3.5 py-2.5 text-sm text-white focus:outline-hidden focus:border-[#FF5722]"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-white mb-1.5">
                    URL Slug <span className="text-[#FF5722]">*</span>
                  </label>
                  <div className="flex items-center bg-[#121216] border border-white/10 rounded-xs px-3 py-2 text-xs">
                    <span className="text-white/40 mono mr-1">/blog/</span>
                    <input
                      type="text"
                      value={formData.slug}
                      onChange={(e) => setFormData((prev) => ({ ...prev, slug: e.target.value }))}
                      placeholder="guide-to-corrugated-sheet-making-machines"
                      className="w-full bg-transparent text-white font-mono focus:outline-hidden"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-white mb-1.5">
                    Category <span className="text-[#FF5722]">*</span>
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleCategoryChange(e.target.value)}
                    className="w-full bg-[#121216] border border-white/10 rounded-xs px-3.5 py-2.5 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
                  >
                    {STANDARD_CATEGORIES.map((c) => (
                      <option key={c.name} value={c.name}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-white mb-1.5">Publish Date</label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData((prev) => ({ ...prev, date: e.target.value }))}
                    className="w-full bg-[#121216] border border-white/10 rounded-xs px-3 py-2 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-white mb-1.5">Estimated Read Time</label>
                  <input
                    type="text"
                    value={formData.readTime}
                    onChange={(e) => setFormData((prev) => ({ ...prev, readTime: e.target.value }))}
                    placeholder="e.g. 7 min read"
                    className="w-full bg-[#121216] border border-white/10 rounded-xs px-3 py-2 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-white mb-1.5">Author Byline</label>
                  <input
                    type="text"
                    value={formData.author}
                    onChange={(e) => setFormData((prev) => ({ ...prev, author: e.target.value }))}
                    placeholder="Gagan Engineering Works Technical Desk"
                    className="w-full bg-[#121216] border border-white/10 rounded-xs px-3 py-2 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-white mb-1.5">
                  Summary & Search Excerpt (Meta Description) <span className="text-[#FF5722]">*</span>
                </label>
                <textarea
                  rows={3}
                  value={formData.summary}
                  onChange={(e) => setFormData((prev) => ({ ...prev, summary: e.target.value }))}
                  placeholder="Provide a compelling 150-word technical abstract for Google search results and article summary cards..."
                  className="w-full bg-[#121216] border border-white/10 rounded-xs px-3.5 py-2.5 text-xs text-white focus:outline-hidden focus:border-[#FF5722] leading-relaxed"
                  required
                />
                <div className="text-[10px] text-white/40 mono text-right mt-1">
                  {formData.summary.length} characters (120–160 optimal for Google search snippet)
                </div>
              </div>
            </div>
          </div>

          {/* Card 2: Cover Media & Image Upload */}
          <div className="bg-[#09090B] border border-white/10 rounded-xs p-6 space-y-4 shadow-xl">
            <div className="mono text-[11px] uppercase tracking-wider text-[#FF5722] flex items-center gap-2 border-b border-white/10 pb-3">
              <ImageIcon className="w-4 h-4" />
              <span>2. Cover Image & Media Asset</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-white mb-1.5">Image Asset URL</label>
                  <input
                    type="text"
                    value={formData.image}
                    onChange={(e) => setFormData((prev) => ({ ...prev, image: e.target.value }))}
                    placeholder="e.g. /automatic-ctl.png or https://..."
                    className="w-full bg-[#121216] border border-white/10 rounded-xs px-3.5 py-2.5 text-xs text-white font-mono focus:outline-hidden focus:border-[#FF5722]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-white mb-1.5">Or Upload New Photo</label>
                  <label className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 text-white text-xs rounded-xs border border-white/20 cursor-pointer transition-colors">
                    <Upload className="w-4 h-4 text-[#FF5722]" />
                    <span>{uploadingImage ? "Uploading Photo..." : "Choose Image File"}</span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      disabled={uploadingImage}
                      className="hidden"
                    />
                  </label>
                  <p className="text-[10px] text-white/40 mt-1">
                    Accepts PNG, JPG, WebP. High-resolution factory or machine photo recommended.
                  </p>
                </div>
              </div>

              {/* Cover Preview */}
              <div className="h-44 bg-[#121216] border border-white/10 rounded-xs overflow-hidden flex items-center justify-center relative">
                {formData.image ? (
                  <img
                    src={formData.image}
                    alt="Cover preview"
                    onError={(e) => { e.currentTarget.src = "/logo.png"; }}
                    className="w-full h-full object-contain p-2"
                  />
                ) : (
                  <div className="text-center text-white/30 space-y-1">
                    <ImageIcon className="w-8 h-8 mx-auto" />
                    <span className="mono text-[10px] uppercase">No Cover Selected</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Card 3: SEO Keywords, Tags & Related Products */}
          <div className="bg-[#09090B] border border-white/10 rounded-xs p-6 space-y-5 shadow-xl">
            <div className="mono text-[11px] uppercase tracking-wider text-[#FF5722] flex items-center gap-2 border-b border-white/10 pb-3">
              <Tag className="w-4 h-4" />
              <span>3. Search Intent Keywords, Tags & Contextual Internal Links</span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-white mb-1.5">
                  Target Commercial Keywords (Meta Keywords)
                </label>
                <input
                  type="text"
                  value={formData.targetKeywords}
                  onChange={(e) => setFormData((prev) => ({ ...prev, targetKeywords: e.target.value }))}
                  placeholder="e.g. Cut to length machine manufacturer, CTL line price India, Khopoli Maharashtra"
                  className="w-full bg-[#121216] border border-white/10 rounded-xs px-3.5 py-2.5 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
                />
              </div>

              {/* Tag Editor */}
              <div>
                <label className="block text-xs font-medium text-white mb-1.5">Article Tags</label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {formData.tags.map((t) => (
                    <span
                      key={t}
                      className="bg-white/5 border border-white/15 px-2.5 py-1 text-xs rounded-xs flex items-center gap-1.5 text-white/80"
                    >
                      {t}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(t)}
                        className="text-white/40 hover:text-red-400"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-2 max-w-sm">
                  <input
                    type="text"
                    value={newTagInput}
                    onChange={(e) => setNewTagInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); handleAddTag(); } }}
                    placeholder="Add tag..."
                    className="flex-1 bg-[#121216] border border-white/10 rounded-xs px-3 py-1.5 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
                  />
                  <button
                    type="button"
                    onClick={handleAddTag}
                    className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-xs rounded-xs border border-white/10"
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* Related Products Multi-Select */}
              <div>
                <label className="block text-xs font-medium text-white mb-1.5">
                  Contextual Related Catalogue Machines (Links in Article Footer)
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto p-3 bg-[#121216] border border-white/10 rounded-xs">
                  {CATALOGUE_PRODUCTS.map((prod) => {
                    const isSelected = formData.relatedProducts.includes(prod.id);
                    return (
                      <label
                        key={prod.id}
                        className={`flex items-center gap-2 p-2 rounded-xs text-xs cursor-pointer transition-colors ${
                          isSelected
                            ? "bg-[#FF5722]/15 text-white border border-[#FF5722]/40"
                            : "text-white/70 hover:bg-white/5 border border-transparent"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData((prev) => ({
                                ...prev,
                                relatedProducts: [...prev.relatedProducts, prod.id]
                              }));
                            } else {
                              setFormData((prev) => ({
                                ...prev,
                                relatedProducts: prev.relatedProducts.filter((id) => id !== prod.id)
                              }));
                            }
                          }}
                          className="accent-[#FF5722]"
                        />
                        <span className="truncate">{prod.name}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Card 4: Interactive Content Builder */}
          <div className="bg-[#09090B] border border-white/10 rounded-xs p-6 space-y-6 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-3">
              <div className="mono text-[11px] uppercase tracking-wider text-[#FF5722] flex items-center gap-2">
                <Layers className="w-4 h-4" />
                <span>4. Structured Content Sections & Specification Tables</span>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={addTextSection}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white/10 hover:bg-white/15 text-white text-xs rounded-xs border border-white/10 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5 text-[#FF5722]" />
                  <span>+ Text Section</span>
                </button>
                <button
                  type="button"
                  onClick={addTableSection}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white/10 hover:bg-white/15 text-white text-xs rounded-xs border border-white/10 transition-colors"
                >
                  <Table className="w-3.5 h-3.5 text-[#FF5722]" />
                  <span>+ Spec Table</span>
                </button>
              </div>
            </div>

            {/* Render Editable Sections */}
            <div className="space-y-6">
              {formData.content.map((sec, idx) => (
                <div
                  key={sec.id || idx}
                  className="bg-[#121216] border border-white/10 rounded-xs p-4 sm:p-5 space-y-4 relative group/sec"
                >
                  {/* Section Top Controls */}
                  <div className="flex items-center justify-between border-b border-white/10 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="mono text-[10px] uppercase tracking-wider bg-[#FF5722]/20 text-[#FF5722] px-2 py-0.5 rounded-xs font-bold">
                        #{idx + 1} {sec.type === "table" ? "Table" : "Section"}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => moveSection(idx, -1)}
                        disabled={idx === 0}
                        className="p-1 text-white/50 hover:text-white disabled:opacity-20"
                        title="Move Up"
                      >
                        <MoveUp className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => moveSection(idx, 1)}
                        disabled={idx === formData.content.length - 1}
                        className="p-1 text-white/50 hover:text-white disabled:opacity-20"
                        title="Move Down"
                      >
                        <MoveDown className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => removeSection(idx)}
                        className="p-1 text-red-400/60 hover:text-red-400"
                        title="Delete Section"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Heading */}
                  <div>
                    <label className="block text-[11px] font-medium text-white/70 mb-1">
                      Section Heading
                    </label>
                    <input
                      type="text"
                      value={sec.heading}
                      onChange={(e) => updateSection(idx, { ...sec, heading: e.target.value })}
                      placeholder="e.g. 9-Roll Precision Leveler Mechanism"
                      className="w-full bg-[#09090B] border border-white/10 rounded-xs px-3 py-2 text-sm text-white focus:outline-hidden focus:border-[#FF5722]"
                    />
                  </div>

                  {/* If Type == Section: Body text + Bullet points */}
                  {sec.type === "section" && (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-[11px] font-medium text-white/70 mb-1">
                          Body Text (Supports Markdown **bold**)
                        </label>
                        <textarea
                          rows={4}
                          value={sec.text || ""}
                          onChange={(e) => updateSection(idx, { ...sec, text: e.target.value })}
                          placeholder="Write detailed paragraphs explaining engineering details..."
                          className="w-full bg-[#09090B] border border-white/10 rounded-xs px-3 py-2 text-xs text-white focus:outline-hidden focus:border-[#FF5722] leading-relaxed"
                        />
                      </div>

                      {/* Bullet Items List */}
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <label className="text-[11px] font-medium text-white/70">
                            Key Bullet Points (Optional)
                          </label>
                          <button
                            type="button"
                            onClick={() => {
                              const updatedItems = [...(sec.items || []), "New technical specification point"];
                              updateSection(idx, { ...sec, items: updatedItems });
                            }}
                            className="text-[10px] text-[#FF5722] hover:underline"
                          >
                            + Add Bullet Point
                          </button>
                        </div>

                        <div className="space-y-2">
                          {(sec.items || []).map((item, itemIdx) => (
                            <div key={itemIdx} className="flex items-center gap-2">
                              <span className="text-[#FF5722] font-bold text-xs">▸</span>
                              <input
                                type="text"
                                value={item}
                                onChange={(e) => {
                                  const updatedItems = [...sec.items];
                                  updatedItems[itemIdx] = e.target.value;
                                  updateSection(idx, { ...sec, items: updatedItems });
                                }}
                                className="flex-1 bg-[#09090B] border border-white/10 rounded-xs px-2.5 py-1.5 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
                              />
                              <button
                                type="button"
                                onClick={() => {
                                  const updatedItems = sec.items.filter((_, i) => i !== itemIdx);
                                  updateSection(idx, { ...sec, items: updatedItems });
                                }}
                                className="text-white/40 hover:text-red-400 p-1"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* If Type == Table: Column Headers + Rows */}
                  {sec.type === "table" && (
                    <div className="space-y-4">
                      <div className="overflow-x-auto border border-white/10 rounded-xs">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-[#09090B] border-b border-white/10">
                            <tr>
                              {(sec.headers || []).map((header, hIdx) => (
                                <th key={hIdx} className="p-2 font-semibold">
                                  <input
                                    type="text"
                                    value={header}
                                    onChange={(e) => {
                                      const updatedHeaders = [...sec.headers];
                                      updatedHeaders[hIdx] = e.target.value;
                                      updateSection(idx, { ...sec, headers: updatedHeaders });
                                    }}
                                    className="w-full bg-transparent text-[#FF5722] font-mono text-xs focus:outline-hidden border-b border-transparent focus:border-[#FF5722]"
                                  />
                                </th>
                              ))}
                              <th className="p-2 w-12 text-center">Action</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-white/5 bg-[#09090B]">
                            {(sec.rows || []).map((row, rIdx) => (
                              <tr key={rIdx}>
                                {row.map((cell, cIdx) => (
                                  <td key={cIdx} className="p-2">
                                    <input
                                      type="text"
                                      value={cell}
                                      onChange={(e) => {
                                        const updatedRows = [...sec.rows];
                                        updatedRows[rIdx][cIdx] = e.target.value;
                                        updateSection(idx, { ...sec, rows: updatedRows });
                                      }}
                                      className="w-full bg-transparent text-white/80 font-mono text-xs focus:outline-hidden border-b border-transparent focus:border-[#FF5722]"
                                    />
                                  </td>
                                ))}
                                <td className="p-2 text-center">
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const updatedRows = sec.rows.filter((_, i) => i !== rIdx);
                                      updateSection(idx, { ...sec, rows: updatedRows });
                                    }}
                                    className="text-white/40 hover:text-red-400"
                                  >
                                    ×
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      <div className="flex items-center gap-3">
                        <button
                          type="button"
                          onClick={() => {
                            const newColName = `Column ${(sec.headers?.length || 0) + 1}`;
                            const updatedHeaders = [...(sec.headers || []), newColName];
                            const updatedRows = (sec.rows || []).map((row) => [...row, "-"]);
                            updateSection(idx, { ...sec, headers: updatedHeaders, rows: updatedRows });
                          }}
                          className="text-xs text-white/60 hover:text-white"
                        >
                          + Add Column
                        </button>
                        <span>·</span>
                        <button
                          type="button"
                          onClick={() => {
                            const emptyRow = (sec.headers || []).map(() => "-");
                            const updatedRows = [...(sec.rows || []), emptyRow];
                            updateSection(idx, { ...sec, rows: updatedRows });
                          }}
                          className="text-xs text-[#FF5722] hover:underline"
                        >
                          + Add Row
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Sticky Action Bar */}
          <div className="sticky bottom-4 z-20 bg-[#09090B]/95 backdrop-blur border border-white/20 p-4 rounded-xs flex items-center justify-between shadow-2xl">
            <Link
              to="/admin/blogs"
              className="text-xs text-white/60 hover:text-white transition-colors"
            >
              Discard Changes
            </Link>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setActiveTab("preview")}
                className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white text-xs rounded-xs border border-white/10 font-medium"
              >
                Preview Article
              </button>

              <button
                type="submit"
                disabled={saving}
                className="btn-primary flex items-center gap-2 text-xs py-2 px-6 disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                <span>{saving ? "Saving..." : isEditMode ? "Update Publication" : "Publish to Live Site"}</span>
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
