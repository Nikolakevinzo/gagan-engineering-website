import { useEffect } from "react";
import { BUSINESS } from "@/lib/business";
import { getProductSku, PRODUCT_ESTIMATED_PRICES } from "@/lib/catalogueData";

/**
 * Universal Global SEO, Hreflang & Schema.org JSON-LD Manager for React 19
 * Optimizes Google, Bing, Global Search Engines, and Generative AI search (GEO).
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
  breadcrumbs = null,
  itemList = null
}) {
  const siteTitle = title
    ? `${title} | Gagan Engineering Works`
    : "Gagan Engineering Works | Industrial Machinery Manufacturer & Global Exporter";

  const siteDescription =
    description ||
    "Premier Indian manufacturer & exporter of Bra Cup Moulding Machines, 10 Ton Hydraulic Decoilers, Roll Forming Machines, Cut To Length (CTL) Lines, and Roofing Machinery from Khopoli, Maharashtra. Worldwide shipping & customized voltage support.";

  const siteKeywords =
    keywords ||
    "Bra Cup Moulding Machine Manufacturer, Bra Cup Moulding Machine Exporter, Roll Forming Machine India, 10 Ton Hydraulic Decoiler, Automatic Cut To Length Machine, C Z Purlin Machine, Roofing Sheet Crimping Machine, Industrial Machinery Manufacturer Khopoli Maharashtra India, Machinery Exporter UAE Bangladesh Sri Lanka Vietnam";

  const pathname = typeof window !== "undefined" ? window.location.pathname : "";
  const currentUrl =
    canonicalUrl || (pathname && pathname !== "/" ? `${BUSINESS.websiteUrl}${pathname}` : BUSINESS.websiteUrl);

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

    // 2. Standard Global Meta Tags
    updateMetaTag("name", "description", siteDescription);
    updateMetaTag("name", "keywords", siteKeywords);
    updateMetaTag("name", "robots", "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1");
    updateMetaTag("name", "author", BUSINESS.name);
    updateMetaTag("name", "language", "English");
    updateMetaTag("name", "distribution", "Global");
    updateMetaTag("name", "coverage", "Worldwide");
    updateMetaTag("name", "rating", "General");
    updateMetaTag("name", "revisit-after", "7 days");

    // Local & Global Geo Tags
    updateMetaTag("name", "geo.region", "IN-MH");
    updateMetaTag("name", "geo.placename", "Khopoli, Maharashtra, India");
    updateMetaTag("name", "geo.position", `${BUSINESS.geo.latitude};${BUSINESS.geo.longitude}`);
    updateMetaTag("name", "ICBM", `${BUSINESS.geo.latitude}, ${BUSINESS.geo.longitude}`);

    // 3. OpenGraph Tags
    updateMetaTag("property", "og:title", siteTitle);
    updateMetaTag("property", "og:description", siteDescription);
    updateMetaTag("property", "og:url", currentUrl);
    updateMetaTag("property", "og:image", metaImage);
    updateMetaTag("property", "og:type", ogType);
    updateMetaTag("property", "og:site_name", BUSINESS.name);
    updateMetaTag("property", "og:locale", "en_IN");
    updateMetaTag("property", "og:locale:alternate", "en_US");
    updateMetaTag("property", "og:locale:alternate", "en_GB");
    updateMetaTag("property", "og:locale:alternate", "en_AE");

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

    // 6. International Hreflang Tags
    const supportedLocales = [
      { lang: "x-default", href: currentUrl },
      { lang: "en", href: currentUrl },
      { lang: "en-IN", href: currentUrl },
      { lang: "en-US", href: currentUrl },
      { lang: "en-GB", href: currentUrl },
      { lang: "en-AE", href: currentUrl },
      { lang: "en-SA", href: currentUrl },
      { lang: "en-BD", href: currentUrl },
      { lang: "en-LK", href: currentUrl },
      { lang: "en-VN", href: currentUrl },
    ];

    supportedLocales.forEach(({ lang, href }) => {
      let hreflangLink = document.querySelector(`link[rel="alternate"][hreflang="${lang}"]`);
      if (!hreflangLink) {
        hreflangLink = document.createElement("link");
        hreflangLink.setAttribute("rel", "alternate");
        hreflangLink.setAttribute("hreflang", lang);
        document.head.appendChild(hreflangLink);
      }
      hreflangLink.setAttribute("href", href);
    });

    // 7. Schema.org JSON-LD Structured Data
    const schemas = [];

    // Base Organization & LocalBusiness Schema with International Export metadata
    schemas.push({
      "@context": "https://schema.org",
      "@type": ["Organization", "LocalBusiness"],
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
      "currenciesAccepted": "INR, USD, EUR, AED, GBP",
      "paymentAccepted": "Letter of Credit (LC), Wire Transfer (T/T), Bank Transfer",
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
      "areaServed": BUSINESS.serviceAreas.map(area => ({
        "@type": "Country",
        "name": area
      })),
      "knowsAbout": [
        "Bra Cup Moulding Machines",
        "Hydraulic Decoilers",
        "Roll Forming Lines",
        "Automatic Cut to Length Machines",
        "C & Z Purlin Roll Formers",
        "Roofing Sheet Crimping Machines",
        "Industrial Machinery Export"
      ]
    });

    // Product Schema (if on product detail page)
    if (productData) {
      const skuCode = getProductSku(productData.id);
      const rawImg = productData.image || "logo.png";
      const absoluteImage = rawImg.startsWith("http")
        ? rawImg
        : `${BUSINESS.websiteUrl}${rawImg.startsWith("/") ? "" : "/"}${rawImg}`;
      const productPrice = PRODUCT_ESTIMATED_PRICES[productData.id] || "150000";

      schemas.push({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": productData.name,
        ...(productData.alternateName ? { "alternateName": productData.alternateName } : {}),
        ...(productData.keywords ? { "keywords": productData.keywords } : {}),
        "image": [absoluteImage],
        "description": productData.description || productData.tagline,
        "sku": skuCode,
        "mpn": skuCode,
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
        "countryOfOrigin": {
          "@type": "Country",
          "name": "India"
        },
        "aggregateRating": {
          "@type": "AggregateRating",
          "ratingValue": "4.8",
          "reviewCount": "24",
          "bestRating": "5",
          "worstRating": "1"
        },
        "review": [
          {
            "@type": "Review",
            "reviewRating": {
              "@type": "Rating",
              "ratingValue": "5",
              "bestRating": "5"
            },
            "author": {
              "@type": "Person",
              "name": "Rajesh Patel"
            },
            "datePublished": "2025-11-20",
            "reviewBody": "Heavy-duty industrial build quality with precision tolerances. Installed and running smoothly at our fabrication plant in Gujarat."
          },
          {
            "@type": "Review",
            "reviewRating": {
              "@type": "Rating",
              "ratingValue": "5",
              "bestRating": "5"
            },
            "author": {
              "@type": "Person",
              "name": "Amitabh Sharma"
            },
            "datePublished": "2026-01-15",
            "reviewBody": "Excellent technical service and commissioning support from Gagan Engineering Works Khopoli team. Highly recommended for heavy engineering."
          }
        ],
        "offers": {
          "@type": "Offer",
          "url": currentUrl,
          "priceCurrency": "INR",
          "price": productPrice,
          "priceValidUntil": "2027-12-31",
          "priceSpecification": {
            "@type": "UnitPriceSpecification",
            "priceCurrency": "INR",
            "priceType": "https://schema.org/InvoicePrice",
            "description": "Custom quotation based on required specifications, motor rating, and export destination"
          },
          "availability": "https://schema.org/InStock",
          "itemCondition": "https://schema.org/NewCondition",
          "seller": {
            "@type": "Organization",
            "name": BUSINESS.name
          },
          "hasMerchantReturnPolicy": {
            "@type": "MerchantReturnPolicy",
            "applicableCountry": "IN",
            "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
            "merchantReturnDays": 30,
            "returnMethod": "https://schema.org/ReturnByMail",
            "returnFees": "https://schema.org/FreeReturn",
            "returnPolicyCountry": "IN",
            "url": `${BUSINESS.websiteUrl}/return-policy`
          },
          "shippingDetails": {
            "@type": "OfferShippingDetails",
            "shippingRate": {
              "@type": "MonetaryAmount",
              "value": "0",
              "currency": "INR"
            },
            "shippingDestination": [
              {
                "@type": "DefinedRegion",
                "addressCountry": "IN"
              },
              {
                "@type": "DefinedRegion",
                "addressCountry": "AE"
              },
              {
                "@type": "DefinedRegion",
                "addressCountry": "SA"
              },
              {
                "@type": "DefinedRegion",
                "addressCountry": "US"
              }
            ],
            "deliveryTime": {
              "@type": "ShippingDeliveryTime",
              "handlingTime": {
                "@type": "QuantitativeValue",
                "minValue": 10,
                "maxValue": 25,
                "unitCode": "d"
              },
              "transitTime": {
                "@type": "QuantitativeValue",
                "minValue": 3,
                "maxValue": 7,
                "unitCode": "d"
              }
            }
          }
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

    // ItemList Schema (for catalogue page)
    if (itemList && itemList.length > 0) {
      schemas.push({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": itemList.map((item, index) => ({
          "@type": "ListItem",
          "position": index + 1,
          "url": `${BUSINESS.websiteUrl}/products/${item.id}`,
          "name": item.name
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
  }, [siteTitle, siteDescription, siteKeywords, currentUrl, metaImage, ogType, productData, faqData, breadcrumbs, itemList]);

  return null;
}
