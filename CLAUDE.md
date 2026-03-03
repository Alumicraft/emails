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

**Button behavior:**
- Before first send: normal "Send Email" button
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

## Known Issues / Changelog

### Send Email button not appearing on Payment Request (ongoing)

**Bug:** The custom "Send Email" button does not appear on submitted Payment Request documents, despite working on other doctypes (Sales Invoice, Quotation, etc.).

**What's been tried and ruled out:**
- **Async `_service_enabled` gate** — Was blocking button setup if the API call to check Email Service Settings hadn't returned yet. Removed; button setup is now fully synchronous. (`bb00e05`)
- **Debug `console.log` statements** — Added during investigation, then cleaned up. (`921fd25`, `89af1cc`)
- **Service check dependency** — Made button setup independent of the service enabled check so the button renders regardless. (`da3f398`)
- **`setInterval` fallback** — Added polling every 2 seconds as a backup mechanism to attach the button if initial setup misses it. (`156d0a0`)
- **Cleanup commit** — Removed all debug logging and consolidated fixes. (`156d0a0`)

**Remaining suspects:**
1. **Conflicting Client Script** — A site-level Client Script on Payment Request may be interfering with or overriding the button setup
2. **Asset caching** — The browser or Frappe asset pipeline may be serving a stale version of `send_email_button.js`
3. **Permission issue** — Payment Request may have different permission rules that prevent the button from rendering
4. **ERPNext Payment Request handlers** — ERPNext's own Payment Request form logic (which adds its own "Send SMS", "Create Payment Entry" buttons) may be overriding or clearing custom buttons added by the hook

**Related commits:** `156d0a0`, `bb00e05`, `921fd25`, `89af1cc`, `da3f398`

**Next steps for debugging:**
- Check for any Client Scripts on Payment Request in the ERPNext site (`/app/client-script?doctype=Payment+Request`)
- Hard-refresh browser and clear Frappe cache (`bench clear-cache`)
- Inspect the browser console on a submitted Payment Request to verify `send_email_button.js` is executing
- Check if `frappe.ui.form.on("Payment Request", ...)` handlers are being registered but then overwritten by ERPNext's own handlers
