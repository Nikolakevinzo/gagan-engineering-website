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

## What's Been Implemented (Feb 2026)
- 8 products with images, descriptions, spec sheets, categories
- Backend `/api/products`, `/api/products/{id}`, `/api/products/featured`, `/api/categories`, `/api/contact`, `/api/business-info`
- Resend integration sending leads to gaganengineerings@gmail.com (key: re_QmaYTND5...)
- Industrial dark theme with Bebas Neue + IBM Plex fonts, orange `#FF5722` accent
- Full data-testid coverage

## Backlog (P1)
- Add Photos gallery page
- Testimonials carousel from real IndiaMART reviews
- Multi-language (Hindi)
- Sitemap.xml + Open Graph meta tags for SEO

## P2
- Verify domain in Resend (currently sends from `onboarding@resend.dev`, only delivers to verified emails)
- Add Google Analytics
- Blog / case studies section
