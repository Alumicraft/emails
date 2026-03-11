# Emails

Professional branded emails via Resend for ERPNext documents. Renders React Email templates via a Vercel serverless function.

## Features

- Branded React Email templates for Sales Invoices, Quotations, Sales Orders, Purchase Orders, Payment Requests, and more
- Dark mode support across all templates
- Automatic PDF attachment generation
- Customizable company branding (colors, logos, typography)
- Fallback chain: Vercel → Direct Resend → ERPNext native email
- Communication logging in ERPNext
- Multi-site support via separate Vercel deployments

## Architecture

```
ERPNext (Python/Frappe)  →  Vercel Serverless (TypeScript/React)  →  Resend API
```

- `emails/` — Frappe app installed on each ERPNext site
- `templates/` — Vercel serverless function deployed at `/api/send`

Each ERPNext site gets its own Vercel project (same repo, different env vars) with its own Resend account and sending domain.

## Installation

### Backend (Frappe app)
```bash
cd ~/frappe-bench
bench get-app https://github.com/Alumicraft/emails.git
bench --site your-site-name install-app emails
bench --site your-site-name migrate
bench restart
```

### Templates (Vercel)
1. Create a new Vercel project from this repo
2. Set **Root Directory** to `templates/`
3. Add environment variables:
   - `RESEND_API_KEY` — from your Resend account
   - `SERVICE_API_KEY` — shared secret for authenticating requests from ERPNext
4. Deploy

## Configuration

1. Set up a Resend account and verify your sending domain
2. In ERPNext, go to **Email Service Settings**
3. Enable the service and add your Resend API Key
4. Set the default sender email (e.g., `no-reply@yourdomain.com`)
5. Set the Vercel Service URL to `https://<your-vercel-project>.vercel.app`
6. Set the Vercel Service API Key to match the `SERVICE_API_KEY` in Vercel

## Usage

Once configured, a "Send Email" button appears on submitted documents for supported doctypes. The app intercepts email sending and routes through branded React templates.

### Supported Document Types

- Sales Invoice
- Quotation
- Sales Order
- Purchase Order
- Request for Quotation
- Payment Request
- Payment Entry
- Generic fallback for any other doctype

### Building Templates

```bash
cd templates
npm install
npm run build          # esbuild → api/send.js
```

### Local Preview

```bash
cd templates
npx email dev          # Opens react-email preview server
```

## License

MIT
