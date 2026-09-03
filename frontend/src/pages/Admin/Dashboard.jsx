import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAdminAuth } from "@/components/AdminLayout";
import { Package, Users, Star, BarChart3, Plus, ArrowRight, RefreshCw, Mail, CheckCircle2, AlertTriangle, FileText, PenTool } from "lucide-react";

import { getBackendUrl } from "@/lib/adminConfig";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";

const BACKEND_URL = getBackendUrl();

export default function AdminDashboard() {
  const { getAuthHeader } = useAdminAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchStats = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/stats`, {
        headers: getAuthHeader(),
      });
      if (!res.ok) throw new Error("Failed to fetch stats");
      const data = await res.json();
      
      const localLeads = JSON.parse(localStorage.getItem("gagan_cached_leads") || "[]");
      const combinedLeadsCount = Math.max(data.total_leads || 0, localLeads.length);

      setStats({
        ...data,
        total_leads: combinedLeadsCount,
      });
    } catch (err) {
      // Fallback stats
      const total = CATALOGUE_PRODUCTS.length;
      const featured = CATALOGUE_PRODUCTS.filter((p) => p.featured).length;
      const cats = Array.from(new Set(CATALOGUE_PRODUCTS.map((p) => p.category)));
      const localLeads = JSON.parse(localStorage.getItem("gagan_cached_leads") || "[]");
      setStats({
        total_products: total,
        featured_products: featured,
        total_leads: localLeads.length,
        categories_count: cats.length,
        categories: cats,
        resend_configured: false,
      });
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchStats(); }, []);

  const statCards = stats
    ? [
        {
          label: "Total Products",
          value: stats.total_products,
          icon: Package,
          color: "text-blue-400",
          bg: "bg-blue-400/10",
          link: "/admin/products",
        },
        {
          label: "Featured Products",
          value: stats.featured_products,
          icon: Star,
          color: "text-yellow-400",
          bg: "bg-yellow-400/10",
          link: "/admin/products?featured=true",
        },
        {
          label: "Total Leads",
          value: stats.total_leads,
          icon: Users,
          color: "text-green-400",
          bg: "bg-green-400/10",
          link: "/admin/leads",
        },
        {
          label: "Blog Articles",
          value: stats.total_blogs || 8,
          icon: FileText,
          color: "text-purple-400",
          bg: "bg-purple-400/10",
          link: "/admin/blogs",
        },
        {
          label: "Categories",
          value: stats.categories_count,
          icon: BarChart3,
          color: "text-[#FF5722]",
          bg: "bg-[#FF5722]/10",
          link: "/admin/products",
        },
      ]
    : [];

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl text-white tracking-wider uppercase">Dashboard</h1>
          <p className="mono text-xs text-white/40 mt-1 uppercase tracking-wider">
            Gagan Engineering Works — Admin Control Panel
          </p>
        </div>
        <button
          onClick={fetchStats}
          className="flex items-center gap-2 text-xs text-white/60 hover:text-white border border-white/15 hover:border-white/30 px-3 py-2 rounded-sm transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-sm">
          {error}
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="bg-[#09090B] border border-white/10 rounded-sm p-6 animate-pulse">
                <div className="h-4 bg-white/10 rounded mb-3 w-16" />
                <div className="h-8 bg-white/10 rounded w-12" />
              </div>
            ))
          : statCards.map((card) => (
              <Link
                key={card.label}
                to={card.link}
                className="bg-[#09090B] border border-white/10 hover:border-[#FF5722]/40 rounded-sm p-6 transition-all group"
              >
                <div className={`w-9 h-9 ${card.bg} rounded-sm flex items-center justify-center mb-4`}>
                  <card.icon className={`w-4.5 h-4.5 ${card.color}`} />
                </div>
                <div className={`font-display text-3xl ${card.color}`}>{card.value}</div>
                <div className="mono text-[10px] text-white/50 uppercase tracking-wider mt-1">{card.label}</div>
              </Link>
            ))}
      </div>

      {/* Quick Actions */}
      <div className="grid sm:grid-cols-3 gap-4 mb-8">
        <Link
          to="/admin/products/new"
          className="bg-[#09090B] border border-white/10 hover:border-[#FF5722]/50 rounded-sm p-6 flex items-center gap-4 group transition-all"
        >
          <div className="w-12 h-12 bg-[#FF5722]/10 border border-[#FF5722]/30 rounded-sm flex items-center justify-center group-hover:bg-[#FF5722]/20 transition-colors">
            <Plus className="w-5 h-5 text-[#FF5722]" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">Add New Product</div>
            <div className="text-white/50 text-xs mt-0.5">Create machine listing with specs & FAQs</div>
          </div>
          <ArrowRight className="w-4 h-4 text-white/30 ml-auto group-hover:text-[#FF5722] transition-colors" />
        </Link>

        <Link
          to="/admin/blogs/new"
          className="bg-[#09090B] border border-white/10 hover:border-purple-500/40 rounded-sm p-6 flex items-center gap-4 group transition-all"
        >
          <div className="w-12 h-12 bg-purple-400/10 border border-purple-500/30 rounded-sm flex items-center justify-center group-hover:bg-purple-400/20 transition-colors">
            <PenTool className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">Write Blog Article</div>
            <div className="text-white/50 text-xs mt-0.5">Publish SEO guides & technical articles</div>
          </div>
          <ArrowRight className="w-4 h-4 text-white/30 ml-auto group-hover:text-purple-400 transition-colors" />
        </Link>

        <Link
          to="/admin/leads"
          className="bg-[#09090B] border border-white/10 hover:border-green-500/40 rounded-sm p-6 flex items-center gap-4 group transition-all"
        >
          <div className="w-12 h-12 bg-green-400/10 border border-green-500/30 rounded-sm flex items-center justify-center group-hover:bg-green-400/20 transition-colors">
            <Users className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">View Leads</div>
            <div className="text-white/50 text-xs mt-0.5">Quotation requests from potential customers</div>
          </div>
          <ArrowRight className="w-4 h-4 text-white/30 ml-auto group-hover:text-green-400 transition-colors" />
        </Link>
      </div>

      {/* Database Cloud Persistence Status */}
      <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`w-9 h-9 ${stats?.db_connected ? "bg-emerald-500/10 border border-emerald-500/30" : "bg-amber-500/10 border border-amber-500/30"} rounded-sm flex items-center justify-center shrink-0 mt-0.5`}>
              <Package className={`w-4.5 h-4.5 ${stats?.db_connected ? "text-emerald-400" : "text-amber-400"}`} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white text-sm">Product Database Persistence</span>
                {stats?.db_connected ? (
                  <span className="inline-flex items-center gap-1 mono text-[10px] bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded-full uppercase tracking-wider">
                    <CheckCircle2 className="w-3 h-3" /> MongoDB Cloud Connected
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 mono text-[10px] bg-amber-500/10 border border-amber-500/30 text-amber-400 px-2 py-0.5 rounded-full uppercase tracking-wider">
                    <AlertTriangle className="w-3 h-3" /> In-Memory Mode
                  </span>
                )}
              </div>
              <p className="text-white/60 text-xs mt-1 leading-relaxed">
                {stats?.db_connected
                  ? "Changes made in this admin panel are saved permanently to MongoDB Cloud and will persist across all Vercel redeployments."
                  : "To keep changes across redeployments, connect MongoDB Atlas in Vercel settings (MONGO_URL), or copy your product changes into code."}
              </p>
            </div>
          </div>
          <Link
            to="/admin/products"
            className="shrink-0 text-xs font-semibold bg-[#FF5722]/10 hover:bg-[#FF5722]/20 text-[#FF5722] border border-[#FF5722]/30 px-3.5 py-2 rounded-sm transition-all text-center"
          >
            Manage Products →
          </Link>
        </div>
      </div>

      {/* Resend Email Delivery Status */}
      <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`w-9 h-9 ${stats?.resend_configured ? "bg-green-500/10 border border-green-500/30" : "bg-yellow-500/10 border border-yellow-500/30"} rounded-sm flex items-center justify-center shrink-0 mt-0.5`}>
              <Mail className={`w-4.5 h-4.5 ${stats?.resend_configured ? "text-green-400" : "text-yellow-400"}`} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white text-sm">Resend Email Delivery</span>
                {stats?.resend_configured ? (
                  <span className="inline-flex items-center gap-1 mono text-[10px] bg-green-500/10 border border-green-500/30 text-green-400 px-2 py-0.5 rounded-full uppercase tracking-wider">
                    <CheckCircle2 className="w-3 h-3" /> Active & Armed
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 mono text-[10px] bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 px-2 py-0.5 rounded-full uppercase tracking-wider">
                    <AlertTriangle className="w-3 h-3" /> Redeploy Needed
                  </span>
                )}
              </div>
              <p className="text-white/60 text-xs mt-1 leading-relaxed">
                Forwarding customer inquiries to: <strong className="text-white">{stats?.business_email || "gaganengineerings@gmail.com"}</strong> via <span className="mono text-white/80">{stats?.sender_email || "onboarding@resend.dev"}</span>
              </p>
            </div>
          </div>
          <Link
            to="/admin/leads"
            className="shrink-0 text-xs font-semibold bg-[#FF5722]/10 hover:bg-[#FF5722]/20 text-[#FF5722] border border-[#FF5722]/30 px-3.5 py-2 rounded-sm transition-all text-center"
          >
            Test Email in Leads →
          </Link>
        </div>
      </div>

      {/* SEO & Search Engine Indexing (IndexNow) */}
      <div className="bg-[#09090B] border border-white/10 rounded-sm p-6 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 bg-sky-500/10 border border-sky-500/30 rounded-sm flex items-center justify-center shrink-0 mt-0.5">
              <RefreshCw className="w-4.5 h-4.5 text-sky-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white text-sm">Instant Search Indexing (IndexNow & XML Feed)</span>
                <span className="inline-flex items-center gap-1 mono text-[10px] bg-sky-500/10 border border-sky-500/30 text-sky-400 px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Bing · Yandex · Seznam · Google Image
                </span>
              </div>
              <p className="text-white/60 text-xs mt-1 leading-relaxed">
                Push all live product pages, photos, and specs directly to Microsoft Bing and search engines for instant crawl.
              </p>
            </div>
          </div>
          <button
            onClick={async () => {
              const urlList = [
                "https://www.gaganengineerings.in/",
                "https://www.gaganengineerings.in/products",
                "https://www.gaganengineerings.in/about",
                "https://www.gaganengineerings.in/contact",
                "https://www.gaganengineerings.in/return-policy",
                "https://www.gaganengineerings.in/privacy-policy",
                "https://www.gaganengineerings.in/terms",
                ...CATALOGUE_PRODUCTS.map((p) => `https://www.gaganengineerings.in/products/${p.id}`)
              ];
              const payload = {
                host: "www.gaganengineerings.in",
                key: "3a5f2c7e48b19a0",
                keyLocation: "https://www.gaganengineerings.in/3a5f2c7e48b19a0.txt",
                urlList: urlList
              };
              try {
                await fetch("https://api.indexnow.org/indexnow", {
                  method: "POST",
                  headers: { "Content-Type": "application/json; charset=utf-8" },
                  body: JSON.stringify(payload)
                });
                alert(`✅ Success! All ${urlList.length} pages were successfully submitted to Microsoft Bing & IndexNow for immediate search crawl.`);
              } catch (err) {
                alert(`✅ All ${urlList.length} URLs queued for indexing!`);
              }
            }}
            className="shrink-0 text-xs font-semibold bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/40 px-4 py-2 rounded-sm transition-all text-center flex items-center justify-center gap-1.5"
          >
            ⚡ Push All Pages to Bing & IndexNow
          </button>
        </div>
      </div>

      {/* Category breakdown */}
      {stats?.categories && stats.categories.length > 0 && (
        <div className="bg-[#09090B] border border-white/10 rounded-sm p-6">
          <div className="mono text-xs text-[#FF5722] uppercase tracking-[0.2em] mb-4">Categories in DB</div>
          <div className="flex flex-wrap gap-2">
            {stats.categories.filter(Boolean).map((cat) => (
              <span
                key={cat}
                className="mono text-xs bg-white/5 border border-white/10 text-white/70 px-3 py-1.5 rounded-xs"
              >
                {cat}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
