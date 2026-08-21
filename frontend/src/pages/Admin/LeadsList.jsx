import { useState, useEffect } from "react";
import { useAdminAuth } from "@/components/AdminLayout";
import { RefreshCw, Download, Phone, Mail, Calendar, ChevronLeft, ChevronRight, MessageCircle } from "lucide-react";

import { getBackendUrl } from "@/lib/adminConfig";

const BACKEND_URL = getBackendUrl();

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

export default function AdminLeadsList() {
  const { getAuthHeader } = useAdminAuth();

  const [leads, setLeads] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const LIMIT = 25;

  const fetchLeads = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${BACKEND_URL}/api/admin/leads?page=${page}&limit=${LIMIT}`,
        { headers: getAuthHeader() }
      );
      if (!res.ok) throw new Error("Failed to fetch leads");
      const data = await res.json();
      setLeads(data.leads || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError("Could not load leads. Backend may be offline or no leads yet.");
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchLeads(); }, [page]);

  const exportCSV = () => {
    if (!leads.length) return;
    const headers = ["Name", "Phone", "Email", "Product Interest", "Message", "Date"];
    const rows = leads.map((l) => [
      `"${l.name || ""}"`,
      `"${l.phone || ""}"`,
      `"${l.email || ""}"`,
      `"${l.product_interest || ""}"`,
      `"${(l.message || "").replace(/"/g, '""')}"`,
      `"${formatDate(l.created_at)}"`,
    ]);
    const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gagan-leads-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="font-display text-3xl text-white tracking-wider uppercase">Leads / Inquiries</h1>
          <p className="mono text-xs text-white/40 mt-1 uppercase tracking-wider">
            {total} quotation request{total !== 1 ? "s" : ""} total
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchLeads}
            className="flex items-center gap-2 text-xs text-white/60 hover:text-white border border-white/15 hover:border-white/30 px-3 py-2 rounded-sm transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={exportCSV}
            disabled={!leads.length}
            className="flex items-center gap-2 text-xs text-white/70 hover:text-white border border-white/15 hover:border-white/30 px-3 py-2 rounded-sm transition-all disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 text-sm px-4 py-3 rounded-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-[#09090B] border border-white/10 rounded-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-black/40">
                <th className="text-left px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium">Contact</th>
                <th className="text-left px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium hidden sm:table-cell">Product Interest</th>
                <th className="text-left px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium hidden lg:table-cell">Message</th>
                <th className="text-left px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium hidden md:table-cell">Date</th>
                <th className="text-right px-4 py-3 mono text-[10px] uppercase tracking-[0.15em] text-white/40 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td className="px-4 py-4"><div className="h-4 bg-white/10 rounded w-32" /></td>
                      <td className="px-4 py-4 hidden sm:table-cell"><div className="h-4 bg-white/10 rounded w-40" /></td>
                      <td className="px-4 py-4 hidden lg:table-cell"><div className="h-4 bg-white/10 rounded w-48" /></td>
                      <td className="px-4 py-4 hidden md:table-cell"><div className="h-4 bg-white/10 rounded w-24" /></td>
                      <td className="px-4 py-4"><div className="h-4 bg-white/10 rounded w-16 ml-auto" /></td>
                    </tr>
                  ))
                : leads.length === 0
                ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-12 text-center text-white/40 text-sm">
                        No leads yet. Inquiries submitted from the contact form will appear here.
                      </td>
                    </tr>
                  )
                : leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-white/3 transition-colors">
                      <td className="px-4 py-4">
                        <div className="font-medium text-white text-sm">{lead.name}</div>
                        <div className="flex items-center gap-1 mono text-[10px] text-white/40 mt-0.5">
                          <Phone className="w-3 h-3" /> {lead.phone}
                        </div>
                        <div className="flex items-center gap-1 mono text-[10px] text-white/40 mt-0.5">
                          <Mail className="w-3 h-3" /> {lead.email}
                        </div>
                      </td>
                      <td className="px-4 py-4 hidden sm:table-cell">
                        <span className="mono text-xs text-white/60">
                          {lead.product_interest || "—"}
                        </span>
                      </td>
                      <td className="px-4 py-4 hidden lg:table-cell">
                        <p className="text-xs text-white/50 line-clamp-2 max-w-xs">
                          {lead.message || "—"}
                        </p>
                      </td>
                      <td className="px-4 py-4 hidden md:table-cell">
                        <div className="flex items-center gap-1 mono text-[10px] text-white/40">
                          <Calendar className="w-3 h-3" />
                          {formatDate(lead.created_at)}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex items-center justify-end gap-1">
                          <a
                            href={`https://wa.me/91${lead.phone?.replace(/[^0-9]/g, "")}?text=${encodeURIComponent(`Hi ${lead.name}, This is Gagan Engineering Works. We received your inquiry about ${lead.product_interest || "our machinery"}.`)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            title="Reply on WhatsApp"
                            className="p-2 text-green-400/50 hover:text-green-400 rounded-sm hover:bg-green-400/10 transition-all"
                          >
                            <MessageCircle className="w-4 h-4" />
                          </a>
                          <a
                            href={`mailto:${lead.email}?subject=Re: ${lead.product_interest || 'Your Inquiry'} — Gagan Engineering Works`}
                            title="Reply via Email"
                            className="p-2 text-white/30 hover:text-[#FF5722] rounded-sm hover:bg-[#FF5722]/10 transition-all"
                          >
                            <Mail className="w-4 h-4" />
                          </a>
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
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-sm hover:bg-white/10 disabled:opacity-30 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="mono">{page} / {totalPages}</span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
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
