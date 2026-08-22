import { useState, useEffect, createContext, useContext } from "react";
import { Link, NavLink, useNavigate, Outlet } from "react-router-dom";
import {
  LayoutDashboard, Package, Users, LogOut, Menu, X,
  ChevronRight, Factory, Settings, Upload
} from "lucide-react";

const AdminAuthContext = createContext(null);

export function useAdminAuth() {
  return useContext(AdminAuthContext);
}

function getStoredCredentials() {
  try {
    const stored = localStorage.getItem("admin_creds");
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

export function AdminAuthProvider({ children }) {
  const [credentials, setCredentials] = useState(getStoredCredentials);

  const login = (username, password) => {
    const creds = { username, password };
    localStorage.setItem("admin_creds", JSON.stringify(creds));
    setCredentials(creds);
  };

  const logout = () => {
    localStorage.removeItem("admin_creds");
    setCredentials(null);
  };

  const getAuthHeader = () => {
    if (!credentials) return {};
    const encoded = btoa(`${credentials.username}:${credentials.password}`);
    return {
      "Authorization": `Bearer ${encoded}`,
      "X-Admin-Auth": encoded,
      "X-Admin-User": credentials.username,
      "X-Admin-Pass": credentials.password
    };
  };

  return (
    <AdminAuthContext.Provider value={{ credentials, login, logout, getAuthHeader }}>
      {children}
    </AdminAuthContext.Provider>
  );
}

export default function AdminLayout() {
  const { credentials, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!credentials) {
      navigate("/admin/login");
    }
  }, [credentials, navigate]);

  if (!credentials) return null;

  const navItems = [
    { to: "/admin", label: "Dashboard", icon: LayoutDashboard, end: true },
    { to: "/admin/products", label: "Products", icon: Package },
    { to: "/admin/products/new", label: "Add Product", icon: Upload },
    { to: "/admin/leads", label: "Leads / Inquiries", icon: Users },
  ];

  return (
    <div className="min-h-screen bg-[#030304] text-white flex">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#09090B] border-r border-white/10 flex flex-col transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0`}
      >
        {/* Logo */}
        <div className="p-5 border-b border-white/10 flex items-center gap-3">
          <div className="w-11 h-9 flex items-center justify-center shrink-0">
            <img
              src="/logo.png"
              alt="GSK Logo"
              className="w-full h-full object-contain"
            />
          </div>
          <div>
            <div className="font-display text-base text-white tracking-wider">GAGAN ADMIN</div>
            <div className="mono text-[9px] tracking-[0.2em] text-white/40 uppercase">Control Panel</div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium transition-all ${
                  isActive
                    ? "bg-[#FF5722]/15 text-[#FF5722] border border-[#FF5722]/30"
                    : "text-white/60 hover:text-white hover:bg-white/5"
                }`
              }
            >
              <item.icon className="w-4 h-4 shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Bottom: Website Link + Logout */}
        <div className="p-4 border-t border-white/10 space-y-2">
          <Link
            to="/"
            target="_blank"
            className="flex items-center gap-2 px-3 py-2 text-xs text-white/50 hover:text-white/80 transition-colors"
          >
            <Factory className="w-3.5 h-3.5" />
            View Live Website
          </Link>
          <button
            onClick={logout}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs text-red-400/70 hover:text-red-400 transition-colors rounded-sm hover:bg-red-400/10"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Topbar */}
        <header className="sticky top-0 z-30 bg-[#09090B]/95 backdrop-blur border-b border-white/10 px-4 sm:px-6 py-3 flex items-center gap-4">
          <button
            className="lg:hidden text-white/70 hover:text-white"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <div className="flex-1" />
          <span className="mono text-xs text-white/40">
            Admin: <span className="text-[#FF5722]">{credentials.username}</span>
          </span>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
