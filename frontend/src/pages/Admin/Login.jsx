import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAdminAuth } from "@/components/AdminLayout";
import { Lock, User, Eye, EyeOff, Factory } from "lucide-react";

import { getBackendUrl } from "@/lib/adminConfig";

const BACKEND_URL = getBackendUrl();

export default function AdminLogin() {
  const { login } = useAdminAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const encoded = btoa(`${username}:${password}`);
      const res = await fetch(`${BACKEND_URL}/api/admin/auth/check`, {
        headers: { Authorization: `Basic ${encoded}` },
      });

      if (res.ok) {
        login(username, password);
        navigate("/admin");
      } else if (res.status === 401) {
        setError("Invalid username or password. Please try again.");
      } else {
        setError("Server error. Please try again later.");
      }
    } catch (err) {
      // If backend is offline, try to login anyway with stored creds
      setError("Cannot reach server. Check your backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030304] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-14 h-11 flex items-center justify-center shrink-0">
              <img
                src="/logo.png"
                alt="GSK Logo"
                className="w-full h-full object-contain"
              />
            </div>
            <div className="text-left">
              <div className="font-display text-2xl text-white tracking-wider">GAGAN ADMIN</div>
              <div className="mono text-[10px] tracking-[0.2em] text-white/40 uppercase">
                Secure Control Panel
              </div>
            </div>
          </div>
          <p className="text-white/40 text-sm mt-2">
            Sign in to manage products, specs, and leads.
          </p>
        </div>

        {/* Form Card */}
        <form
          onSubmit={handleSubmit}
          className="bg-[#09090B] border border-white/10 rounded-sm p-8 space-y-5 shadow-2xl"
        >
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-sm">
              {error}
            </div>
          )}

          {/* Username */}
          <div>
            <label className="block mono text-[11px] uppercase tracking-wider text-white/60 mb-2">
              Username
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="admin"
                autoComplete="username"
                className="w-full bg-black/60 border border-white/15 text-white text-sm pl-10 pr-4 py-3 rounded-sm focus:outline-none focus:border-[#FF5722] transition-colors"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block mono text-[11px] uppercase tracking-wider text-white/60 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                className="w-full bg-black/60 border border-white/15 text-white text-sm pl-10 pr-12 py-3 rounded-sm focus:outline-none focus:border-[#FF5722] transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#FF5722] hover:bg-[#F4511E] text-white font-semibold py-3 px-6 rounded-sm uppercase tracking-wider text-sm transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            <Lock className="w-4 h-4" />
            {loading ? "Signing In..." : "Sign In to Admin Panel"}
          </button>
        </form>

        <p className="text-center text-white/30 text-xs mt-6 mono">
          Default: admin / gaganworks2006 (set in .env)
        </p>
      </div>
    </div>
  );
}
