import { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAdminAuth } from "@/components/AdminLayout";
import {
  Plus, Search, Trash2, Edit3, Star, StarOff,
  Filter, RefreshCw, ChevronLeft, ChevronRight, Eye
} from "lucide-react";
import { getBackendUrl } from "@/lib/adminConfig";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";

const BACKEND_URL = getBackendUrl();

const CATEGORY_OPTIONS = [
  { id: "all", name: "All Categories" },
  { id: "bra-cup-moulding-machine", name: "Bra Cup Moulding Machine" },
  { id: "roll-forming-sheet-metal", name: "Roll Forming & Sheet Metal" },
  { id: "cut-to-length-line", name: "Cut To Length Line" },
];

export default function AdminProductList() {
  const { getAuthHeader } = useAdminAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);
  const [togglingId, setTogglingId] = useState(null);

  const page = parseInt(searchParams.get("page") || "1");
  const search = searchParams.get("search") || "";
  const category = searchParams.get("category") || "all";
  const LIMIT = 20;

  const fetchProducts = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ page, limit: LIMIT });
      if (search) params.set("search", search);
      if (category !== "all") params.set("category", category);

      const res = await fetch(`${BACKEND_URL}/api/admin/products?${params}`, {
        headers: getAuthHeader(),
      });
      if (!res.ok) throw new Error("Failed to fetch products from backend");
      const data = await res.json();
      if (data.products && data.products.length > 0) {
        setProducts(data.products);
        setTotal(data.total || data.products.length);
      } else {
        // Fallback to catalogue if empty
        setProducts(CATALOGUE_PRODUCTS);
        setTotal(CATALOGUE_PRODUCTS.length);
      }
    } catch (err) {
      // Gracefully show catalogue products so admin is never blocked
      console.warn("Backend products fetch failed, using fallback catalogue:", err);
      let filtered = CATALOGUE_PRODUCTS;
      if (category !== "all") {
        filtered = filtered.filter((p) => p.categorySlug === category);
      }
      if (search) {
        filtered = filtered.filter((p) => p.name.toLowerCase().includes(search.toLowerCase()));
      }
      setProducts(filtered);
      setTotal(filtered.length);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchProducts(); }, [page, search, category]);



  const handleSearch = (val) => {
    const p = new URLSearchParams(searchParams);
    p.set("search", val);
    p.set("page", "1");
    setSearchParams(p);
  };

  const handleCategory = (val) => {
    const p = new URLSearchParams(searchParams);
    p.set("category", val);
    p.set("page", "1");
    setSearchParams(p);
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"?\n\nThis cannot be undone.`)) return;
    setDeletingId(id);
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/products/${id}`, {
        method: "DELETE",
        headers: getAuthHeader(),
      });
      if (!res.ok) throw new Error("Delete failed");
      setProducts((prev) => prev.filter((p) => p.id !== id));
      setTotal((prev) => prev - 1);
    } catch (err) {
      alert("Failed to delete product. Please try again.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleToggleFeatured = async (product) => {
    setTogglingId(product.id);
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/products/${product.id}`, {
        method: "PUT",
        headers: { ...getAuthHeader(), "Content-Type": "application/json" },
        body: JSON.stringify({ featured: !product.featured }),
      });
      if (!res.ok) throw new Error("Toggle failed");
      setProducts((prev) =>
        prev.map((p) => p.id === product.id ? { ...p, featured: !p.featured } : p)
      );
    } catch (err) {
      alert("Failed to update product.");
    } finally {
      setTogglingId(null);
    }
  };

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="font-display text-3xl text-white tracking-wider uppercase">Products</h1>
          <p className="mono text-xs text-white/40 mt-1 uppercase tracking-wider">
            {total} machine{total !== 1 ? "s" : ""} in database
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchProducts}
            className="flex items-center gap-2 text-xs text-white/60 hover:text-white border border-white/15 hover:border-white/30 px-3 py-2 rounded-sm transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
          <Link
            to="/admin/products/new"
            className="flex items-center gap-2 bg-[#FF5722] hover:bg-[#F4511E] text-white font-semibold text-xs uppercase tracking-wider px-4 py-2.5 rounded-sm transition-colors"
          >
            <Plus className="w-4 h-4" /> Add Product
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-[#09090B] border border-white/10 rounded-sm p-4 mb-5 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
          <input
            type="text"
            defaultValue={search}
            onKeyDown={(e) => e.key === "Enter" && handleSearch(e.target.value)}
            onBlur={(e) => handleSearch(e.target.value)}
            placeholder="Search by name, description..."
            className="w-full bg-black/60 border border-white/15 text-white text-sm pl-10 pr-4 py-2.5 rounded-sm focus:outline-none focus:border-[#FF5722]"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-white/40 shrink-0" />
          <select
            value={category}
            onChange={(e) => handleCategory(e.target.value)}
            className="bg-black/60 border border-white/15 text-white text-sm px-3 py-2.5 rounded-sm focus:outline-none focus:border-[#FF5722]"
          >
            {CATEGORY_OPTIONS.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-[#09090B] border border-white/10 rounded-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-black/40">
                <th className="text-left px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium">Product</th>
                <th className="text-left px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium hidden md:table-cell">Category</th>
                <th className="text-center px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium">Featured</th>
                <th className="text-right px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 bg-white/5 rounded-sm shrink-0" />
                          <div className="h-4 bg-white/10 rounded w-40" />
                        </div>
                      </td>
                      <td className="px-4 py-4 hidden md:table-cell"><div className="h-4 bg-white/10 rounded w-24" /></td>
                      <td className="px-4 py-4"><div className="h-4 bg-white/10 rounded w-12 mx-auto" /></td>
                      <td className="px-4 py-4"><div className="h-4 bg-white/10 rounded w-20 ml-auto" /></td>
                    </tr>
                  ))
                : products.length === 0
                ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-12 text-center text-white/40 text-sm">
                        No products found.{" "}
                        <Link to="/admin/products/new" className="text-[#FF5722] hover:underline">Add one →</Link>
                      </td>
                    </tr>
                  )
                : products.map((product) => (
                    <tr key={product.id} className="hover:bg-white/3 transition-colors">
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-14 h-12 bg-black/80 rounded-xs border border-white/10 shrink-0 p-1 flex items-center justify-center overflow-hidden">
                            <img
                              src={product.image}
                              alt={product.name}
                              className="w-full h-full object-contain"
                              onError={(e) => { e.target.src = "https://via.placeholder.com/48"; }}
                            />
                          </div>
                          <div>
                            <div className="font-medium text-white line-clamp-1">{product.name}</div>
                            <div className="mono text-[10px] text-white/40 mt-0.5">/{product.id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 hidden md:table-cell">
                        <span className="mono text-xs bg-white/5 border border-white/10 text-white/60 px-2 py-1 rounded-xs">
                          {product.category}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-center">
                        <button
                          onClick={() => handleToggleFeatured(product)}
                          disabled={togglingId === product.id}
                          title={product.featured ? "Remove from featured" : "Mark as featured"}
                          className={`p-1.5 rounded-sm transition-colors ${
                            product.featured
                              ? "text-yellow-400 hover:text-yellow-300"
                              : "text-white/20 hover:text-yellow-400"
                          } disabled:opacity-40`}
                        >
                          {product.featured
                            ? <Star className="w-4 h-4 fill-current" />
                            : <StarOff className="w-4 h-4" />}
                        </button>
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex items-center justify-end gap-1">
                          <a
                            href={`/products/${product.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            title="View on website"
                            className="p-2 text-white/40 hover:text-white rounded-sm hover:bg-white/5 transition-all"
                          >
                            <Eye className="w-4 h-4" />
                          </a>
                          <Link
                            to={`/admin/products/edit/${product.id}`}
                            title="Edit product"
                            className="p-2 text-white/40 hover:text-[#FF5722] rounded-sm hover:bg-[#FF5722]/10 transition-all"
                          >
                            <Edit3 className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(product.id, product.name)}
                            disabled={deletingId === product.id}
                            title="Delete product"
                            className="p-2 text-white/40 hover:text-red-400 rounded-sm hover:bg-red-400/10 transition-all disabled:opacity-40"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-4 py-4 border-t border-white/10 flex items-center justify-between text-xs text-white/50">
            <span className="mono">
              Showing {(page - 1) * LIMIT + 1}–{Math.min(page * LIMIT, total)} of {total}
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 1}
                onClick={() => { const p = new URLSearchParams(searchParams); p.set("page", page - 1); setSearchParams(p); }}
                className="p-1.5 rounded-sm hover:bg-white/10 disabled:opacity-30 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="mono">{page} / {totalPages}</span>
              <button
                disabled={page >= totalPages}
                onClick={() => { const p = new URLSearchParams(searchParams); p.set("page", page + 1); setSearchParams(p); }}
                className="p-1.5 rounded-sm hover:bg-white/10 disabled:opacity-30 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
