# Emails - Project Guide

Custom email service for ERPNext that renders branded React Email templates via a Vercel serverless function and sends through Resend.

## Architecture

```
ERPNext (Python/Frappe)  →  Vercel Serverless (TypeScript/React)  →  Resend API
         ↓                            ↓
   emails/                    templates/
   (backend logic)            (email templates + API handler)
```

**Two deployment targets:**
- `emails/` — Frappe app installed on the ERPNext site
- `templates/` — Vercel serverless function at `/api/send`

## Project Structure

```
emails/                              # Frappe app (Python backend)
├── api.py                           # @frappe.whitelist() endpoints
├── hooks.py                         # Frappe hooks, overrides, fixtures
├── email_service/
│   ├── generic_email.py             # Main entry: send_document_email()
│   ├── email_override.py            # Override Communication.email.make
│   ├── sendmail_override.py         # Override frappe.sendmail for system emails
│   ├── payment_request_override.py  # Custom PaymentRequest.send_email()
│   ├── vercel_client.py             # HTTP client → Vercel /api/send
│   ├── resend_client.py             # Direct Resend API client (fallback)
│   ├── branding.py                  # Fetch company branding from settings
│   ├── utils.py                     # PDF gen, email lookups, communication logs
│   └── webhooks.py                  # Resend webhook handlers
├── emails/doctype/
│   ├── email_service_settings/      # Single doctype: API keys, branding, config
│   ├── email_branding/              # Branding template doctype
│   └── email_doctype_configuration/ # Per-doctype email config

templates/                           # Vercel deployment (TypeScript frontend)
├── src/send.tsx                     # API handler source (renders + sends)
├── api/send.js                      # Built bundle (esbuild output, DO NOT EDIT)
├── emails/                          # React Email templates
│   ├── shared.tsx                   # Layout, InfoCard, InfoRow, Footer, Logo, etc.
│   ├── sales-invoice.tsx
│   ├── quotation.tsx
│   ├── sales-order.tsx
│   ├── purchase-order.tsx
│   ├── request-for-quotation.tsx
│   ├── payment-request.tsx
│   ├── document.tsx                 # Generic fallback template
│   ├── magic-link.tsx
│   ├── password-reset.tsx
│   ├── email-verification.tsx
│   └── welcome.tsx
├── vercel.json
├── tsconfig.json
├── tailwind.config.ts
└── package.json
```

## Email Flow

1. User triggers email from ERPNext (Send button, Payment Request, etc.)
2. Python intercepts via `email_override.py` or `sendmail_override.py`
3. `generic_email.py` builds template data from document fields
4. `vercel_client.py` POSTs to Vercel `/api/send` with template name, data, and branding
5. `src/send.tsx` renders React component to HTML via `@react-email/render`
6. Sends through Resend API, returns message_id
7. Python creates Communication log in ERPNext

**Fallback chain:** Vercel → Direct Resend → ERPNext native email

## Template Conventions

### File naming
- Templates: `kebab-case.tsx` (e.g., `sales-invoice.tsx`)
- Components: PascalCase (e.g., `SalesInvoiceEmail`)
- Props interface: `{ComponentName}Props` (e.g., `SalesInvoiceEmailProps`)

### Template structure
Every template file exports:
1. `Branding` re-export from shared
2. Props interface
3. Named component export
4. Default export with preview/sample data

### Shared components (from `shared.tsx`)
- `Layout` — Full email wrapper with dark mode CSS, header logo, footer, confidentiality
- `InfoCard` — Table container for key-value data rows
- `InfoRow` — Label + value row (monospace value, right-aligned)
- `InfoAmount` — Highlighted amount row with background color
- `Footer` — Divider, secondary logo, contact info, address (linked to Google Maps)
- `Logo` — Light/dark mode image swap via CSS
- `Confidentiality` — Standard confidentiality notice
- `Button` — CTA button with branding colors

### Dark mode
Every template supports dark mode via CSS `@media (prefers-color-scheme: dark)` in the Layout component. All color-bearing classes use `email-*` prefixed class names for dark mode targeting. Gmail dark mode is handled with special `u ~ div` selectors for logo swap.

### Branding object
Templates receive a `Branding` object with 40+ fields:
- Light colors: `primary_color`, `text_color`, `background_color`, `card_color`, `table_color`, `border_color`, `amount_bg_color`, etc.
- Dark variants: same keys with `_dark` suffix
- Logos: `logo_url`, `logo_url_dark`, `logo_url_secondary`, `logo_url_secondary_dark`
- Company: `company`, `company_email`, `company_phone`, `mailing_address`, `website_url`
- Typography: `font_family`

## Python Backend

### DOCTYPE_TEMPLATE_MAP (generic_email.py)
Maps ERPNext doctypes to React template names:
```python
"Sales Invoice"          → "sales-invoice"
"Quotation"              → "quotation"
"Sales Order"            → "sales-order"
"Purchase Order"         → "purchase-order"
"Request for Quotation"  → "request-for-quotation"
"Payment Request"        → "payment-request"
"Payment Entry"          → "payment-request"
# Anything else          → "document" (generic fallback)
```

### DOCTYPE_REGISTRY (email_service_settings.py)
Maps doctypes to recipient resolution logic (which field holds the party, which doctype to look up email from).

### Key functions
- `send_document_email()` — Main entry point for all document emails
- `build_template_data()` — Extracts all fields from a document + per-doctype prop mapping
- `resolve_recipient_email()` — Smart recipient lookup via registry + contact fallback
- `get_company_branding()` — Fetch branding from Email Service Settings

### Hooks overview
- `override_doctype_class`: PaymentRequest → CustomPaymentRequest
- `override_whitelisted_methods`: Communication.email.make → custom handler
- `on_session_creation`: Monkey-patches `frappe.sendmail` for system email routing
- `doc_events`: Communication on_update handler

## Building & Deploying

### Templates (Vercel)
```bash
cd templates
npm install
npm run build          # esbuild → api/send.js
# Deploy via Vercel CLI or git push
```

The build output `api/send.js` is a single bundled file. It IS committed to git (required by Vercel).

### Backend (Frappe)
Standard Frappe app install:
```bash
bench get-app emails
bench --site site.local install-app emails
```

## Environment Variables (Vercel)
- `RESEND_API_KEY` — Resend API key
- `SERVICE_API_KEY` — Auth token for incoming requests from ERPNext

## Common Tasks

### Adding a new document email template
1. Create `templates/emails/{doctype-name}.tsx` following existing patterns
2. Add component to template registry in `templates/src/send.tsx`
3. Add doctype mapping in `generic_email.py` `DOCTYPE_TEMPLATE_MAP`
4. Add per-doctype prop mapping in `build_template_data()`
5. Run `npm run build` in `templates/`

### Modifying branding/styling
- Shared styles: `templates/emails/shared.tsx`
- Dark mode: CSS block in `Layout` component
- Per-template: edit the specific `.tsx` file
- Rebuild after changes: `npm run build`

### Testing templates locally
```bash
cd templates
npx email dev    # Opens react-email preview server
```

## Important Notes

- `api/send.js` is a 1.9MB compiled bundle — never edit directly, always edit `src/send.tsx` or template files and rebuild
- The `custom_message` prop on templates is for user-provided messages only — do not pass ERPNext-rendered HTML through it (it gets escaped by React)
- `items` data is extracted by `build_template_data()` but not currently rendered by any template — it's available for future use
- Payment Request subject uses the reference document number (e.g., "Invoice SINV-001 from Company") rather than Payment Request name
