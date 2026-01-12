app_name = "emails"
app_title = "Emails"
app_publisher = "Alumicraft"
app_description = "Professional branded emails via Resend for invoices, quotations, receipts, and other documents"
app_email = "your@email.com"
app_license = "MIT"

# Apps
required_apps = ["frappe", "erpnext"]

# Document Events - Intercept Communication creation for email override
doc_events = {
    "Communication": {
        "before_insert": "emails.email_service.email_override.before_communication_insert",
        "on_update": "emails.email_service.email_override.on_communication_update"
    }
}

# Fixtures - Export Email Service Settings
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
