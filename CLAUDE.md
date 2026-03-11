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
- `emails/` — Frappe app installed on each ERPNext site
- `templates/` — Vercel serverless function at `/api/send`

**Multi-site setup:** Each ERPNext site gets its own Vercel project (same repo, different env vars) pointing to its own Resend account. This avoids Resend's single-domain-per-free-account limitation.

| Site | Vercel Project | Resend Account | Domain |
|------|---------------|----------------|--------|
| Alumicraft | `emails-alumicraft` | Alumicraft account | alumicraft.com |
| Dealer Capital | `emails-dcr` | send2tristan account | dealercapital.net |

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
│   ├── payment-entry.tsx
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
"Payment Entry"          → "payment-entry"
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
- `app_include_js`: Loads `send_email_button.js` globally — registers form handlers for all supported doctypes synchronously at load time
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

Vercel Root Directory must be set to `templates/` in each project's Build and Deployment settings.

### Adding a new site deployment
1. Create a new Vercel project from the same `email` GitHub repo
2. Set Root Directory to `templates/`
3. Add `RESEND_API_KEY` and `SERVICE_API_KEY` environment variables (for Production)
4. Deploy
5. In the new ERPNext site's Email Service Settings:
   - Set Vercel Service URL to `https://<project-name>.vercel.app` (no `/api/send` — the client appends it automatically)
   - Set Vercel Service API Key to match the `SERVICE_API_KEY` in Vercel

### Backend (Frappe)
Standard Frappe app install:
```bash
bench get-app emails
bench --site site.local install-app emails
```

## Environment Variables (Vercel)
- `RESEND_API_KEY` — Resend API key (from the Resend account that owns the sending domain)
- `SERVICE_API_KEY` — Auth token for incoming requests from ERPNext (must match the Vercel Service API Key in Email Service Settings)

Each Vercel project has its own set of env vars. The same git repo is deployed to multiple Vercel projects with different environment variables.

## Common Tasks

### Adding a new document email template
1. Create `templates/emails/{doctype-name}.tsx` following existing patterns
2. Add component to template registry in `templates/src/send.tsx`
3. Add doctype mapping in `generic_email.py` `DOCTYPE_TEMPLATE_MAP`
4. Add doctype to the list in `send_email_button.js` (for the Send Email button)
5. Add per-doctype prop mapping in `build_template_data()`
6. Run `npm run build` in `templates/`

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

## Send Email Button

The custom "Send Email" button appears on submitted documents. A single file handles everything:

- **`send_email_button.js`** — Loaded globally via `app_include_js`. Registers `refresh` and `after_submit` handlers for all supported doctypes synchronously at load time, then defines the `emails.*` functions (setup button, show dialog, send email, etc.)

`frappe.ui.form.on()` just registers handlers in a lookup table — it doesn't need the form to exist. Calling it synchronously at script load time is safe, avoids all timing issues, and doesn't interfere with ERPNext's own handlers (including the "Create" button dropdown).

**Payment Request anti-flicker:** For Payment Request, a `setup` handler monkey-patches `frm.add_custom_button` to silently block any call with the label "Resend Payment Email" (returning an empty jQuery object). Since `setup` fires once at form init before any `refresh` handlers, ERPNext's native button is never created — eliminating the flicker that occurred with reactive DOM removal. A `setInterval` fallback (every 2s) still re-adds our button if something removes it from the DOM.

**Button behavior:**
- Before first send: `btn-primary` "Send Email" button
- After first send: grey `btn-default` "Resend Email" button
- Post-submit: confirmation dialog "Would you like to send an email?"
- The standard Frappe "+ New Email" button is hidden for template-supported doctypes

**Dialog fields:** Recipient Email (required), CC, BCC, Custom Message.

**To add a new doctype to the button system:** add to BOTH `DOCTYPE_TEMPLATE_MAP` in `generic_email.py` AND the doctype list in `send_email_button.js`.

## Important Notes

- `api/send.js` is a 1.9MB compiled bundle — never edit directly, always edit `src/send.tsx` or template files and rebuild
- The `custom_message` prop on templates is for user-provided messages only — do not pass ERPNext-rendered HTML through it (it gets escaped by React)
- `items` data is extracted by `build_template_data()` but not currently rendered by any template — it's available for future use
- Payment Request subject uses the reference document number (e.g., "Invoice SINV-001 from Company") rather than Payment Request name
- The Vercel Service URL in ERPNext should NOT include `/api/send` — `vercel_client.py` appends it automatically
- Each Resend free account only supports one domain — use separate Vercel deployments (same repo) for multi-domain setups

## Known Issues / Changelog

### Payment Request button flicker (resolved)

**Bug:** ERPNext's "Resend Payment Email" button and our "Send Email" button both briefly appeared before ERPNext's was removed, causing visible flicker.

**Root cause:** Both handlers ran on `refresh`. Our reactive approach (add button → scan DOM → remove ERPNext's) was inherently racy.

**Fix:** Monkey-patch `frm.add_custom_button` in the `setup` event (fires once before `refresh`) to silently block "Resend Payment Email" creation. Removed all reactive DOM removal code (`_hide_erpnext_payment_button`, `setTimeout` delays, DOM scans).

### Payment Entry receipt email template (added)

Added a dedicated `payment-entry` template replacing the reused `payment-request` template. Displays Receipt No., Date, Payment Method, Reference No., Applied To (invoice/SO names from references child table), and Amount Paid. Subject line: "Payment Receipt PE-00001 from Company". Uses `paid_from_account_currency` for correct currency formatting.

### Send Email button styling (fixed)

Changed Send Email button from `btn-primary-light` to `btn-primary` so it matches the Update button styling instead of appearing greyed out.

### Sales Order emoji (added)

Added 🏁 emoji to the Sales Order confirmation heading.
