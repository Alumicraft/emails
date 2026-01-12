# Emails

Professional branded emails via Resend for ERPNext documents.

## Features

- Send professional branded emails for Sales Invoices, Quotations, and Sales Orders
- Automatic PDF attachment generation
- Integration with Resend email delivery platform
- Fallback to ERPNext's default email system
- Communication logging

## Installation

```bash
cd ~/frappe-bench
bench get-app https://github.com/Alumicraft/emails.git
bench --site your-site-name install-app emails
bench --site your-site-name migrate
bench restart
```

## Configuration

1. Set up Resend account and verify your domain
2. Go to **Email Service Settings** in ERPNext
3. Enable and add your Resend API Key
4. Set sender email (e.g., `no-reply@yourdomain.com`)
5. Add template IDs for each document type

## Usage

Once configured, the app intercepts email sending for supported document types. Use the standard Email button in ERPNext forms.

### API

```python
frappe.call("emails.api.send_invoice_email", invoice_name="INV-2024-00001")
frappe.call("emails.api.send_quotation_email", quotation_name="QTN-2024-00001")
frappe.call("emails.api.send_sales_order_email", sales_order_name="SO-2024-00001")
```

## License

MIT
