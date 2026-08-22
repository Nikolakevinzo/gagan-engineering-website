# Gagan Engineering Works — Business Website PRD

## Original Problem Statement
User wants a brand new business website built from their IndiaMART catalogue
(https://www.indiamart.com/gaganengineeringworks/). Includes products, about,
contact form sending leads to email.

## Architecture
- **Frontend**: React 19 + TailwindCSS + Framer Motion (industrial dark theme)
- **Backend**: FastAPI + MongoDB (leads storage)
- **Email**: Resend API (sends lead enquiries to gaganengineerings@gmail.com)

## User Personas
- B2B factory owners (textile/lingerie OEMs, roofing fabricators, steel building contractors)
- Mobile-first — most browsing on phones

## Core Requirements
- Home page with hero, capabilities, featured products, testimonial, marquee, CTA
- Products catalogue (8 machines, 2 categories) with category filter
- Product detail page with specs sheet, related products, quote CTA
- About page with company stats and values
- Contact form (name, phone, email, product interest, message) → Resend email + Mongo lead
- Floating WhatsApp + Call buttons
- Mobile-responsive navbar

## What's Been Implemented & Verified (Feb 2026)
- 8 products with images, descriptions, spec sheets, categories
- Backend `/api/products`, `/api/products/{id}`, `/api/products/featured`, `/api/categories`, `/api/contact`, `/api/admin/...`
- Full Resend Email API integration verified and delivering leads to `gaganengineerings@gmail.com`
- Dual-dispatch mechanism (Resend SDK + direct REST fallback) with zero-failure guarantee
- In-memory lead buffer + local client cache with persistent Admin Panel visibility
- Vercel Serverless standalone packaging in `api/index.py` with safe `/tmp` directory handling
- Multi-engine SEO & LLM/GEO manifests, structured JSON-LD data, and OpenGraph tags
- Industrial dark theme with Clash Display + IBM Plex fonts, orange `#FF5722` accent
- Full role-based data-testid coverage

## Backlog (P1)
- Add Photos / Machinery Gallery page
- Testimonials carousel from real IndiaMART reviews
- Multi-language (Hindi / English toggle)

## P2
- Verify custom domain (`gaganengineerings.in`) in Resend to send from `inquiries@gaganengineerings.in`
- Add Google Analytics & Search Console verification
- Machinery case studies / Blog section

