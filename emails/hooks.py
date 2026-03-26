app_name = "emails"
app_title = "Emails"
app_publisher = "Alumicraft"
app_description = "Professional branded emails via Resend for invoices, quotations, receipts, and other documents"
app_email = "your@email.com"
app_license = "MIT"

# Apps
required_apps = ["frappe", "erpnext"]

# Override Payment Request to route emails through Resend
override_doctype_class = {
    "Payment Request": "emails.email_service.payment_request_override.CustomPaymentRequest"
}

# Include JS in desk
app_include_js = "/assets/emails/js/send_email_button.js"

# Override the communication email make function to intercept BEFORE email is queued
override_whitelisted_methods = {
    "frappe.core.doctype.communication.email.make": "emails.email_service.email_override.make_communication_email"
}

# Document Events
doc_events = {
    "Communication": {
        "on_update": "emails.email_service.email_override.on_communication_update"
    },
}

# Session creation hook - override sendmail for system emails
on_session_creation = "emails.email_service.sendmail_override.override_sendmail"

# Also patch on every request in case session was restored from cache
# (on_session_creation only fires on fresh login, not session restore)
before_request = ["emails.email_service.sendmail_override.override_sendmail"]

# Fixtures - Export Email Service Settings custom fields
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Emails"]]
    }
]

# Website Route for Resend Webhook
website_route_rules = [
    {
        "from_route": "/api/method/emails.email_service.webhooks.handle_resend_webhook",
        "to_route": "emails.email_service.webhooks.handle_resend_webhook"
    }
]
