import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { BookOpen, Calendar, Clock, ArrowRight, Search, Tag, Sparkles, Filter, Factory, Wrench } from "lucide-react";
import SEO from "@/components/SEO";
import SectionHeader from "@/components/SectionHeader";
import { BLOG_ARTICLES, BLOG_CATEGORIES } from "@/lib/blogData";
import { BUSINESS } from "@/lib/business";

export default function Blog() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeCatParam = searchParams.get("category") || "all";

  const [articles, setArticles] = useState(BLOG_ARTICLES);
  const [activeCategory, setActiveCategory] = useState(activeCatParam);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    let isMounted = true;

    const mergeWithLocal = (baseArticles) => {
      try {
        const stored = JSON.parse(localStorage.getItem("gagan_custom_blogs") || "[]");
        if (Array.isArray(stored) && stored.length > 0) {
          const merged = [...baseArticles];
          stored.forEach((item) => {
            const idx = merged.findIndex((a) => a.slug === item.slug);
            if (idx >= 0) {
              merged[idx] = { ...merged[idx], ...item };
            } else {
              merged.push(item);
            }
          });
          return merged;
        }
      } catch (e) {}
      return baseArticles;
    };

    fetch("/api/blogs?limit=100")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (isMounted && data && Array.isArray(data.articles) && data.articles.length > 0) {
          setArticles(mergeWithLocal(data.articles));
        } else if (isMounted) {
          setArticles(mergeWithLocal(BLOG_ARTICLES));
        }
      })
      .catch(() => {
        if (isMounted) setArticles(mergeWithLocal(BLOG_ARTICLES));
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleCategorySelect = (id) => {
    setActiveCategory(id);
    const newParams = new URLSearchParams(searchParams);
    if (id === "all") {
      newParams.delete("category");
    } else {
      newParams.set("category", id);
    }
    setSearchParams(newParams);
  };

  const filteredArticles = articles.filter((article) => {
    const matchesCat = activeCategory === "all" || article.categorySlug === activeCategory;
    const matchesSearch =
      searchQuery.trim() === "" ||
      article.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.summary?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (article.tags && article.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase())));
    return matchesCat && matchesSearch;
  });

  const featuredArticle = articles[0] || BLOG_ARTICLES[0];

  return (
    <div className="bg-[#050505] min-h-screen pt-24 sm:pt-28 pb-16 sm:pb-24 text-white">
      <SEO
        title="Engineering Blog & Machinery Buying Guides"
        description="In-depth technical guides on Bra Cup Moulding Machines, Automatic Cut To Length Lines, C/Z Purlin Roll Formers, and industrial machinery export guidelines from Gagan Engineering Works."
        keywords="Industrial Machinery Blog, Bra Cup Moulding Machine Guide, Automatic CTL Line Guide, Roll Forming Machine Specs, Machinery Export from India"
        canonicalUrl={`${BUSINESS.websiteUrl}/blog`}
        breadcrumbs={[
          { name: "Home", url: BUSINESS.websiteUrl },
          { name: "Blog", url: `${BUSINESS.websiteUrl}/blog` }
        ]}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Breadcrumb */}
        <div className="flex items-center gap-1.5 sm:gap-2 mono text-[10px] sm:text-[11px] text-white/50 mb-6 sm:mb-8 uppercase tracking-wider">
          <Link to="/" className="hover:text-white transition-colors">Home</Link>
          <span>/</span>
          <span className="text-[#FF5722]">Blog & Technical Guides</span>
        </div>

        {/* Section Header */}
        <SectionHeader
          as="h1"
          overline="// Technical Blog & Papers"
          title="Engineering & Machinery Buying Guides"
          description="In-depth technical papers, equipment comparison matrices, working principles, and export guidelines authored by our chief machinery engineers."
        />


        {/* Search & Category Filter Bar */}
        <div className="mt-8 sm:mt-12 bg-[#0A0A0C] border border-white/10 p-4 sm:p-5 rounded-xs space-y-4 shadow-xl">
          <div className="relative">
            <Search className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search engineering guides by machine, process, or spec..."
              className="w-full bg-black/60 border border-white/10 text-white text-xs sm:text-sm pl-10 pr-4 py-2.5 sm:py-3 rounded-xs focus:outline-none focus:border-[#FF5722] transition-colors"
            />
          </div>

          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {BLOG_CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => handleCategorySelect(cat.id)}
                className={`mono text-xs px-3.5 py-1.5 rounded-xs whitespace-nowrap transition-all ${
                  activeCategory === cat.id
                    ? "bg-[#FF5722] text-white font-semibold"
                    : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10 border border-white/10"
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Featured Article Banner (if no active search) */}
        {!searchQuery && activeCategory === "all" && featuredArticle && (
          <div className="mt-8 sm:mt-10 bg-gradient-to-br from-[#12141a] to-[#09090B] border border-[#FF5722]/30 rounded-xs overflow-hidden shadow-2xl grid md:grid-cols-12 items-center group">
            <div className="md:col-span-7 p-6 sm:p-8 lg:p-10 space-y-4">
              <div className="inline-flex items-center gap-2 bg-[#FF5722]/10 border border-[#FF5722]/40 px-2.5 py-1 rounded-xs mono text-[10px] sm:text-xs uppercase tracking-widest text-[#FF5722]">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Featured Engineering Guide</span>
              </div>

              <h2 className="font-display text-2xl sm:text-3xl lg:text-4xl text-white uppercase tracking-wide leading-tight group-hover:text-[#FF5722] transition-colors">
                <Link to={`/blog/${featuredArticle.slug}`}>
                  {featuredArticle.title}
                </Link>
              </h2>

              <p className="text-white/70 text-xs sm:text-sm leading-relaxed line-clamp-3">
                {featuredArticle.summary}
              </p>

              <div className="flex flex-wrap items-center gap-4 text-xs mono text-white/50 pt-2">
                <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5 text-[#FF5722]" /> {featuredArticle.date}</span>
                <span>•</span>
                <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-[#FF5722]" /> {featuredArticle.readTime}</span>
              </div>

              <div className="pt-2">
                <Link
                  to={`/blog/${featuredArticle.slug}`}
                  className="btn-primary inline-flex items-center gap-2 text-xs font-semibold px-5 py-2.5"
                >
                  Read Full Engineering Guide <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            <div className="md:col-span-5 h-64 md:h-full bg-[#0c0c0e] relative overflow-hidden flex items-center justify-center p-6 border-t md:border-t-0 md:border-l border-white/10">
              <img
                src={featuredArticle.image}
                alt={featuredArticle.title}
                onError={(e) => {
                  e.currentTarget.src = "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg";
                }}
                className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
              />
            </div>
          </div>
        )}

        {/* Articles Grid */}
        <div className="mt-8 sm:mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredArticles.map((article) => (
            <article
              key={article.slug}
              className="bg-[#09090B] border border-white/10 hover:border-[#FF5722]/50 rounded-xs overflow-hidden flex flex-col justify-between transition-all group shadow-lg"
            >
              <div>
                <div className="aspect-[16/9] bg-[#0c0c0e] overflow-hidden relative border-b border-white/10 flex items-center justify-center p-4">
                  <img
                    src={article.image}
                    alt={article.title}
                    onError={(e) => {
                      e.currentTarget.src = "https://5.imimg.com/data5/ANDROID/Default/2025/10/550586008/TZ/II/HL/4175789/product-jpeg-500x500.jpg";
                    }}
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                  <div className="absolute top-2.5 left-2.5 bg-black/80 backdrop-blur-md px-2 py-0.5 mono text-[9px] uppercase tracking-wider text-[#FF5722] border border-white/10 rounded-xs">
                    {article.category}
                  </div>
                </div>


                <div className="p-5 sm:p-6 space-y-3">
                  <div className="flex items-center gap-3 text-[10px] mono text-white/40">
                    <span className="flex items-center gap-1"><Calendar className="w-3 h-3 text-[#FF5722]" /> {article.date}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {article.readTime}</span>
                  </div>

                  <h3 className="font-display text-lg sm:text-xl text-white uppercase tracking-wide group-hover:text-[#FF5722] transition-colors line-clamp-2">
                    <Link to={`/blog/${article.slug}`}>
                      {article.title}
                    </Link>
                  </h3>

                  <p className="text-white/60 text-xs leading-relaxed line-clamp-3">
                    {article.summary}
                  </p>

                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {article.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="mono text-[9px] bg-white/5 text-white/50 px-2 py-0.5 rounded-xs border border-white/5">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="px-5 sm:px-6 pb-5 sm:pb-6 pt-2">
                <Link
                  to={`/blog/${article.slug}`}
                  className="text-xs font-semibold mono text-[#FF5722] hover:text-white inline-flex items-center gap-1.5 transition-colors"
                >
                  Read Technical Paper →
                </Link>
              </div>
            </article>
          ))}
        </div>

        {filteredArticles.length === 0 && (
          <div className="py-20 text-center text-white/50">
            <BookOpen className="w-10 h-10 text-[#FF5722] mx-auto mb-3" />
            <div className="font-display text-xl text-white uppercase">No Engineering Guides Located</div>
            <p className="text-xs text-white/40 mt-1 max-w-md mx-auto">
              Try searching with another keyword or reset the category filter to view all technical publications.
            </p>
            <button
              onClick={() => { setSearchQuery(""); setActiveCategory("all"); }}
              className="mt-4 btn-ghost text-xs"
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
