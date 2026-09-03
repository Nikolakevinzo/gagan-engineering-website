import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FileText, PenTool, Plus, Search, ExternalLink, Edit3, Trash2,
  Calendar, Clock, Tag, AlertCircle, RefreshCw, Eye, CheckCircle2,
  Layers, FolderCheck
} from "lucide-react";
import { toast } from "sonner";
import { useAdminAuth } from "@/components/AdminLayout";
import { BLOG_ARTICLES } from "@/lib/blogData";

export default function AdminBlogList() {
  const { getAuthHeader } = useAdminAuth();
  const navigate = useNavigate();

  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [deleteModal, setDeleteModal] = useState({ open: false, slug: null, title: "" });
  const [deleting, setDeleting] = useState(false);

  const fetchBlogs = async () => {
    const mergeWithLocal = (baseArticles) => {
      try {
        const stored = JSON.parse(localStorage.getItem("gagan_custom_blogs") || "[]");
        if (Array.isArray(stored) && stored.length > 0) {
          const merged = [...baseArticles];
          stored.forEach((item) => {
            const idx = merged.findIndex((a) => a.slug === item.slug);
            if (idx >= 0) merged[idx] = { ...merged[idx], ...item };
            else merged.push(item);
          });
          return merged;
        }
      } catch (e) {}
      return baseArticles;
    };

    setLoading(true);
    try {
      const res = await fetch("/api/admin/blogs?limit=100", {
        headers: getAuthHeader(),
      });
      if (res.ok) {
        const data = await res.json();
        setArticles(mergeWithLocal(data.articles || []));
      } else {
        // Fallback to static blog data if API is unseeded or offline
        setArticles(mergeWithLocal(BLOG_ARTICLES.map(a => ({ ...a, published: true }))));
      }
    } catch (err) {
      console.warn("Failed to fetch from API, falling back to static blog data:", err);
      setArticles(mergeWithLocal(BLOG_ARTICLES.map(a => ({ ...a, published: true }))));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBlogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = async () => {
    if (!deleteModal.slug) return;
    setDeleting(true);
    try {
      const res = await fetch(`/api/admin/blogs/${deleteModal.slug}`, {
        method: "DELETE",
        headers: getAuthHeader(),
      });
      if (res.ok) {
        toast.success(`Article "${deleteModal.title}" deleted successfully.`);
        setArticles((prev) => prev.filter((a) => a.slug !== deleteModal.slug));
        setDeleteModal({ open: false, slug: null, title: "" });
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to delete article.");
      }
    } catch (e) {
      toast.error("Network error deleting article.");
    } finally {
      setDeleting(false);
    }
  };

  // Extract unique categories
  const categories = Array.from(new Set(articles.map((a) => a.category).filter(Boolean)));

  const filteredArticles = articles.filter((a) => {
    const q = search.toLowerCase();
    const matchesSearch =
      !search ||
      a.title?.toLowerCase().includes(q) ||
      a.summary?.toLowerCase().includes(q) ||
      a.slug?.toLowerCase().includes(q) ||
      (a.tags && a.tags.some((t) => t.toLowerCase().includes(q)));

    const matchesCategory =
      selectedCategory === "all" ||
      a.category === selectedCategory ||
      a.categorySlug === selectedCategory;

    const isPublished = a.published !== false;
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "published" && isPublished) ||
      (statusFilter === "draft" && !isPublished);

    return matchesSearch && matchesCategory && matchesStatus;
  });

  const totalCount = articles.length;
  const publishedCount = articles.filter((a) => a.published !== false).length;
  const draftCount = totalCount - publishedCount;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="mono text-[10px] tracking-[0.2em] text-[#FF5722] uppercase mb-1">
            Content Management System
          </div>
          <h1 className="font-display text-2xl sm:text-3xl text-white uppercase tracking-wider">
            Blog & Technical Publications
          </h1>
          <p className="text-white/50 text-xs sm:text-sm mt-1">
            Publish engineering articles, buyer guides, and technical specifications to dominate search rankings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchBlogs}
            disabled={loading}
            className="p-2.5 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/10 rounded-xs transition-colors"
            title="Refresh articles"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <Link
            to="/admin/blogs/new"
            className="btn-primary flex items-center gap-2 text-xs py-2.5 px-4"
          >
            <Plus className="w-4 h-4" />
            <span>Write New Article</span>
          </Link>
        </div>
      </div>

      {/* Metric Counters */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[#09090B] border border-white/10 p-4 rounded-xs">
          <div className="mono text-[10px] tracking-wider text-white/40 uppercase">Total Articles</div>
          <div className="font-display text-2xl sm:text-3xl text-white mt-1">{totalCount}</div>
        </div>
        <div className="bg-[#09090B] border border-white/10 p-4 rounded-xs">
          <div className="mono text-[10px] tracking-wider text-emerald-400/70 uppercase">Published Live</div>
          <div className="font-display text-2xl sm:text-3xl text-emerald-400 mt-1">{publishedCount}</div>
        </div>
        <div className="bg-[#09090B] border border-white/10 p-4 rounded-xs">
          <div className="mono text-[10px] tracking-wider text-amber-400/70 uppercase">Drafts</div>
          <div className="font-display text-2xl sm:text-3xl text-amber-400 mt-1">{draftCount}</div>
        </div>
        <div className="bg-[#09090B] border border-white/10 p-4 rounded-xs">
          <div className="mono text-[10px] tracking-wider text-[#FF5722]/80 uppercase">Active Categories</div>
          <div className="font-display text-2xl sm:text-3xl text-[#FF5722] mt-1">{categories.length}</div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-[#09090B] border border-white/10 p-4 rounded-xs flex flex-col md:flex-row items-stretch md:items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-white/40 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title, keywords, tags, or URL slug..."
            className="w-full bg-[#121216] border border-white/10 rounded-xs pl-9 pr-3 py-2 text-xs text-white placeholder-white/40 focus:outline-hidden focus:border-[#FF5722]"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-[#121216] border border-white/10 rounded-xs px-3 py-2 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
          >
            <option value="all">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#121216] border border-white/10 rounded-xs px-3 py-2 text-xs text-white focus:outline-hidden focus:border-[#FF5722]"
          >
            <option value="all">All Status</option>
            <option value="published">Published</option>
            <option value="draft">Drafts</option>
          </select>
        </div>
      </div>

      {/* Articles List / Cards */}
      {loading ? (
        <div className="py-20 text-center text-white/40 mono text-xs flex flex-col items-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-[#FF5722]" />
          <span>Loading articles repository...</span>
        </div>
      ) : filteredArticles.length === 0 ? (
        <div className="bg-[#09090B] border border-white/10 p-12 text-center rounded-xs">
          <FileText className="w-12 h-12 text-white/20 mx-auto mb-3" />
          <div className="font-display text-lg text-white uppercase">No Articles Found</div>
          <p className="text-white/40 text-xs mt-1 max-w-md mx-auto">
            {search || selectedCategory !== "all" || statusFilter !== "all"
              ? "Try adjusting your search terms or filters to find published articles."
              : "You have not published any technical publications yet. Write your first article to boost your SEO!"}
          </p>
          <Link to="/admin/blogs/new" className="btn-primary inline-flex items-center gap-2 text-xs mt-5">
            <Plus className="w-4 h-4" />
            <span>Create First Article</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredArticles.map((article) => {
            const isPublished = article.published !== false;
            return (
              <div
                key={article.slug}
                className="bg-[#09090B] border border-white/10 rounded-xs overflow-hidden flex flex-col justify-between hover:border-white/20 transition-all group"
              >
                <div>
                  {/* Thumbnail Cover */}
                  <div className="h-44 bg-[#121216] relative overflow-hidden border-b border-white/10">
                    <img
                      src={article.image || "/logo.png"}
                      alt={article.title}
                      onError={(e) => {
                        e.currentTarget.src = "/logo.png";
                      }}
                      className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute top-2.5 left-2.5">
                      <span className="mono text-[9px] uppercase tracking-wider bg-black/80 backdrop-blur px-2 py-0.5 border border-white/10 text-white/80 rounded-xs">
                        {article.category || "General"}
                      </span>
                    </div>
                    <div className="absolute top-2.5 right-2.5">
                      <span
                        className={`mono text-[9px] uppercase tracking-wider px-2 py-0.5 rounded-xs font-semibold ${
                          isPublished
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                            : "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                        }`}
                      >
                        {isPublished ? "Published" : "Draft"}
                      </span>
                    </div>
                  </div>

                  {/* Body Content */}
                  <div className="p-4 sm:p-5 space-y-3">
                    <div className="flex items-center gap-3 text-[10px] text-white/40 mono">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-[#FF5722]" />
                        {article.date || "Recent"}
                      </span>
                      <span>·</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {article.readTime || "5 min read"}
                      </span>
                    </div>

                    <h3 className="font-display text-base text-white group-hover:text-[#FF5722] transition-colors line-clamp-2 leading-snug">
                      {article.title}
                    </h3>

                    <p className="text-white/60 text-xs line-clamp-2 leading-relaxed">
                      {article.summary}
                    </p>

                    <div className="pt-1">
                      <div className="mono text-[10px] text-white/40 truncate bg-black/40 px-2 py-1 border border-white/5 rounded-xs">
                        /{article.slug}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Actions */}
                <div className="p-4 bg-[#0a0a0d] border-t border-white/5 flex items-center justify-between gap-2">
                  <a
                    href={`/blog/${article.slug}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 text-xs text-white/60 hover:text-white transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>View</span>
                  </a>

                  <div className="flex items-center gap-2">
                    <Link
                      to={`/admin/blogs/edit/${article.slug}`}
                      className="p-1.5 bg-white/5 hover:bg-[#FF5722]/20 hover:text-[#FF5722] text-white/70 rounded-xs transition-colors border border-white/10"
                      title="Edit article"
                    >
                      <Edit3 className="w-4 h-4" />
                    </Link>

                    <button
                      onClick={() => setDeleteModal({ open: true, slug: article.slug, title: article.title })}
                      className="p-1.5 bg-white/5 hover:bg-red-500/20 hover:text-red-400 text-white/70 rounded-xs transition-colors border border-white/10"
                      title="Delete article"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModal.open && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#09090B] border border-red-500/30 rounded-xs max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 mx-auto">
              <AlertCircle className="w-6 h-6" />
            </div>

            <div className="text-center space-y-1">
              <h3 className="font-display text-lg text-white uppercase">Confirm Deletion</h3>
              <p className="text-white/60 text-xs">
                Are you sure you want to permanently delete:
              </p>
              <div className="p-2 bg-white/5 rounded-xs text-xs font-semibold text-white mt-2">
                {deleteModal.title}
              </div>
              <p className="text-red-400 text-[11px] mt-2">
                This will remove the publication from the live website and MongoDB Atlas database.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => setDeleteModal({ open: false, slug: null, title: "" })}
                className="flex-1 py-2.5 px-4 bg-white/5 hover:bg-white/10 text-white text-xs rounded-xs border border-white/10 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 py-2.5 px-4 bg-red-600 hover:bg-red-700 text-white text-xs rounded-xs transition-colors font-medium disabled:opacity-50"
              >
                {deleting ? "Deleting..." : "Yes, Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
