import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Toaster } from "sonner";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import FloatingCTA from "@/components/FloatingCTA";
import AIAssistant from "@/components/AIAssistant";
import AdminLayout, { AdminAuthProvider } from "@/components/AdminLayout";
import Home from "@/pages/Home";
import Products from "@/pages/Products";
import ProductDetail from "@/pages/ProductDetail";
import About from "@/pages/About";
import Contact from "@/pages/Contact";
import ReturnPolicy from "@/pages/ReturnPolicy";
import PrivacyPolicy from "@/pages/PrivacyPolicy";
import Terms from "@/pages/Terms";
import NotFound from "@/pages/NotFound";
import AdminLogin from "@/pages/Admin/Login";
import AdminDashboard from "@/pages/Admin/Dashboard";
import AdminProductList from "@/pages/Admin/ProductList";
import AdminProductForm from "@/pages/Admin/ProductForm";
import AdminLeadsList from "@/pages/Admin/LeadsList";

// Automatically scrolls to top of page on any route / page change
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "instant"
    });
  }, [pathname]);

  return null;
}

// Public site layout wrapper
function PublicLayout({ children }) {
  return (
    <div className="App bg-[#050505] min-h-screen text-white flex flex-col justify-between selection:bg-[#FF5722] selection:text-white">
      <Navbar />
      <main className="flex-grow">{children}</main>
      <Footer />
      <FloatingCTA />
      <AIAssistant />
      <Toaster
        position="bottom-center"
        theme="dark"
        toastOptions={{
          style: {
            background: "#0a0a0c",
            border: "1px solid #27272A",
            color: "#F9FAFB",
            borderRadius: "2px",
            fontSize: "12px",
            fontFamily: "IBM Plex Sans, sans-serif"
          },
        }}
      />
    </div>
  );
}

function App() {
  return (
    <AdminAuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <Routes>
          {/* Admin Login (standalone, no sidebar) */}
          <Route path="/admin/login" element={<AdminLogin />} />

          {/* Admin Panel (protected, with sidebar layout) */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="products" element={<AdminProductList />} />
            <Route path="products/new" element={<AdminProductForm />} />
            <Route path="products/edit/:id" element={<AdminProductForm />} />
            <Route path="leads" element={<AdminLeadsList />} />
            <Route path="*" element={<Navigate to="/admin" replace />} />
          </Route>

          {/* Public Website */}
          <Route path="/" element={
            <PublicLayout>
              <Home />
            </PublicLayout>
          } />
          <Route path="/products" element={
            <PublicLayout>
              <Products />
            </PublicLayout>
          } />
          <Route path="/products/category/:categorySlug" element={
            <PublicLayout>
              <Products />
            </PublicLayout>
          } />
          <Route path="/category/:categorySlug" element={
            <PublicLayout>
              <Products />
            </PublicLayout>
          } />
          <Route path="/product" element={<Navigate to="/products" replace />} />
          <Route path="/products/:id" element={
            <PublicLayout>
              <ProductDetail />
            </PublicLayout>
          } />
          <Route path="/about" element={
            <PublicLayout>
              <About />
            </PublicLayout>
          } />
          <Route path="/contact" element={
            <PublicLayout>
              <Contact />
            </PublicLayout>
          } />
          <Route path="/return-policy" element={
            <PublicLayout>
              <ReturnPolicy />
            </PublicLayout>
          } />
          <Route path="/returns" element={<Navigate to="/return-policy" replace />} />
          <Route path="/privacy-policy" element={
            <PublicLayout>
              <PrivacyPolicy />
            </PublicLayout>
          } />
          <Route path="/terms" element={
            <PublicLayout>
              <Terms />
            </PublicLayout>
          } />
          {/* 404 Catch-all */}
          <Route path="*" element={
            <PublicLayout>
              <NotFound />
            </PublicLayout>
          } />
        </Routes>
      </BrowserRouter>
    </AdminAuthProvider>
  );
}

export default App;
