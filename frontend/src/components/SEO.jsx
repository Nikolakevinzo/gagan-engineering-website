import { useEffect } from "react";
import { BUSINESS } from "@/lib/business";

/**
 * Universal SEO & Schema.org JSON-LD Manager for React 19
 * Optimizes Google, Bing, Social Media cards, and Generative AI search (GEO).
 */
export default function SEO({
  title,
  description,
  keywords,
  canonicalUrl,
  ogImage,
  ogType = "website",
  productData = null,
  faqData = null,
  breadcrumbs = null
}) {
  const siteTitle = title
    ? `${title} | Gagan Engineering Works`
    : "Gagan Engineering Works | Industrial Machinery Manufacturer in India";

  const siteDescription =
    description ||
    "Premier manufacturer of Bra Cup Moulding Machines, 10 Ton Hydraulic Decoilers, Roll Forming Machines, Cut To Length (CTL) Lines, and Roofing Machinery from Khopoli, Maharashtra.";

  const siteKeywords =
    keywords ||
    "Bra Cup Moulding Machine, Roll Forming Machine, 10 Ton Hydraulic Decoiler, Automatic Cut To Length Machine, C Z Purlin Machine, Roofing Sheet Crimping Machine, Industrial Machinery Manufacturer Khopoli Maharashtra India";

  const currentUrl =
    canonicalUrl || (typeof window !== "undefined" ? window.location.href : BUSINESS.websiteUrl);

  const metaImage = ogImage || `${BUSINESS.websiteUrl}/logo.png`;

  useEffect(() => {
    // 1. Update Document Title
    document.title = siteTitle;

    // Helper to update or create meta tags
    const updateMetaTag = (attribute, name, content) => {
      let element = document.querySelector(`meta[${attribute}="${name}"]`);
      if (!element) {
        element = document.createElement("meta");
        element.setAttribute(attribute, name);
        document.head.appendChild(element);
      }
      element.setAttribute("content", content);
    };

    // 2. Standard Meta Tags
    updateMetaTag("name", "description", siteDescription);
    updateMetaTag("name", "keywords", siteKeywords);
    updateMetaTag("name", "robots", "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1");
    updateMetaTag("name", "author", BUSINESS.name);

    // 3. OpenGraph Tags
    updateMetaTag("property", "og:title", siteTitle);
    updateMetaTag("property", "og:description", siteDescription);
    updateMetaTag("property", "og:url", currentUrl);
    updateMetaTag("property", "og:image", metaImage);
    updateMetaTag("property", "og:type", ogType);
    updateMetaTag("property", "og:site_name", BUSINESS.name);

    // 4. Twitter Card Tags
    updateMetaTag("name", "twitter:card", "summary_large_image");
    updateMetaTag("name", "twitter:title", siteTitle);
    updateMetaTag("name", "twitter:description", siteDescription);
    updateMetaTag("name", "twitter:image", metaImage);

    // 5. Canonical Link
    let canonicalLink = document.querySelector("link[rel='canonical']");
    if (!canonicalLink) {
      canonicalLink = document.createElement("link");
      canonicalLink.setAttribute("rel", "canonical");
      document.head.appendChild(canonicalLink);
    }
    canonicalLink.setAttribute("href", currentUrl);

    // 6. Schema.org JSON-LD Structured Data
    const schemas = [];

    // Base Organization & LocalBusiness Schema
    schemas.push({
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "@id": `${BUSINESS.websiteUrl}/#organization`,
      "name": BUSINESS.name,
      "legalName": BUSINESS.legalName,
      "url": BUSINESS.websiteUrl,
      "logo": `${BUSINESS.websiteUrl}/logo.png`,
      "image": metaImage,
      "description": BUSINESS.description,
      "telephone": BUSINESS.phone,
      "email": BUSINESS.email,
      "priceRange": "₹₹₹",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": BUSINESS.streetAddress,
        "addressLocality": BUSINESS.city,
        "addressRegion": BUSINESS.state,
        "postalCode": BUSINESS.postalCode,
        "addressCountry": BUSINESS.country
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": BUSINESS.geo.latitude,
        "longitude": BUSINESS.geo.longitude
      },
      "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "opens": "09:00",
        "closes": "19:30"
      },
      "sameAs": [
        BUSINESS.indiamartUrl
      ],
      "areaServed": BUSINESS.serviceAreas
    });

    // Product Schema (if on product detail page)
    if (productData) {
      schemas.push({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": productData.name,
        "image": productData.image,
        "description": productData.description || productData.tagline,
        "sku": productData.id,
        "mpn": productData.id,
        "category": productData.category,
        "brand": {
          "@type": "Brand",
          "name": BUSINESS.name
        },
        "manufacturer": {
          "@type": "Organization",
          "name": BUSINESS.name,
          "url": BUSINESS.websiteUrl
        },
        "offers": {
          "@type": "Offer",
          "url": currentUrl,
          "priceCurrency": "INR",
          "price": "Contact for Best Price",
          "priceValidUntil": "2027-12-31",
          "availability": "https://schema.org/InStock",
          "itemCondition": "https://schema.org/NewCondition",
          "seller": {
            "@type": "Organization",
            "name": BUSINESS.name
          }
        },
        "aggregateRating": {
          "@type": "AggregateRating",
          "ratingValue": "4.8",
          "reviewCount": "24",
          "bestRating": "5"
        }
      });
    }

    // FAQPage Schema (for SERP rich snippets)
    if (faqData && faqData.length > 0) {
      schemas.push({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faqData.map((item) => ({
          "@type": "Question",
          "name": item.q,
          "acceptedAnswer": {
            "@type": "Answer",
            "text": item.a
          }
        }))
      });
    }

    // BreadcrumbList Schema
    if (breadcrumbs && breadcrumbs.length > 0) {
      schemas.push({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumbs.map((b, index) => ({
          "@type": "ListItem",
          "position": index + 1,
          "name": b.name,
          "item": b.url
        }))
      });
    }

    // Inject JSON-LD Script tag
    let schemaScript = document.getElementById("jsonld-seo-schema");
    if (!schemaScript) {
      schemaScript = document.createElement("script");
      schemaScript.id = "jsonld-seo-schema";
      schemaScript.type = "application/ld+json";
      document.head.appendChild(schemaScript);
    }
    schemaScript.text = JSON.stringify(schemas.length === 1 ? schemas[0] : schemas);
  }, [siteTitle, siteDescription, siteKeywords, currentUrl, metaImage, ogType, productData, faqData, breadcrumbs]);

  return null;
}
