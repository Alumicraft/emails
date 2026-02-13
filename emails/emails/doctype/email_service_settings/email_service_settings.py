# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


# Registry of known doctypes and their source apps with default configurations
DOCTYPE_REGISTRY = {
    # ERPNext Selling
    "Sales Invoice": {
        "app": "erpnext",
        "category": "Selling",
        "recipient_field": "customer",
        "recipient_doctype": "Customer",
    },
    "Quotation": {
        "app": "erpnext",
        "category": "Selling",
        "recipient_field": "party_name",
        "recipient_doctype": "Customer",
    },
    "Sales Order": {
        "app": "erpnext",
        "category": "Selling",
        "recipient_field": "customer",
        "recipient_doctype": "Customer",
    },
    "Delivery Note": {
        "app": "erpnext",
        "category": "Stock",
        "recipient_field": "customer",
        "recipient_doctype": "Customer",
    },
    # ERPNext Buying
    "Purchase Order": {
        "app": "erpnext",
        "category": "Buying",
        "recipient_field": "supplier",
        "recipient_doctype": "Supplier",
    },
    "Purchase Invoice": {
        "app": "erpnext",
        "category": "Buying",
        "recipient_field": "supplier",
        "recipient_doctype": "Supplier",
    },
    # ERPNext Accounts
    "Payment Entry": {
        "app": "erpnext",
        "category": "Accounts",
        "recipient_field": "party",
        "recipient_doctype": None,  # Dynamic based on party_type
    },
    "Payment Request": {
        "app": "erpnext",
        "category": "Accounts",
        "recipient_field": "email_to",
        "recipient_doctype": None,  # Uses email_to field directly
    },
    # Lending Module
    "Loan Application": {
        "app": "lending",
        "category": "Lending",
        "recipient_field": "applicant",
        "recipient_doctype": "Customer",
    },
    "Loan": {
        "app": "lending",
        "category": "Lending",
        "recipient_field": "applicant",
        "recipient_doctype": "Customer",
    },
    "Loan Repayment": {
        "app": "lending",
        "category": "Lending",
        "recipient_field": "applicant",
        "recipient_doctype": "Customer",
    },
}


class EmailServiceSettings(Document):
    def validate(self):
        if self.enabled:
            if not self.resend_api_key:
                frappe.throw(_("Resend API Key is required when service is enabled"))
            if not self.default_sender_email:
                frappe.throw(_("Default Sender Email is required when service is enabled"))

            # Validate API key format
            api_key = self.get_password("resend_api_key")
            if api_key and not api_key.startswith("re_"):
                frappe.throw(_("Invalid Resend API Key format. Key should start with 're_'"))

        # Validate doctype configurations
        self._validate_doctype_configurations()

        # Set branding defaults
        self.set_defaults()

    def set_defaults(self):
        """Set sensible defaults for branding fields."""
        if not self.font_family:
            self.font_family = "Arial, Helvetica, sans-serif"
        if not self.primary_color:
            self.primary_color = "#0066cc"
        if not self.text_color:
            self.text_color = "#333333"
        if not self.background_color:
            self.background_color = "#f8f9fa"
        if not self.logo_height:
            self.logo_height = 40
        if not self.logo_alt_text and self.company:
            self.logo_alt_text = self.company

    def _validate_doctype_configurations(self):
        """Validate that configured doctypes exist and their apps are installed."""
        if not self.supported_doctypes:
            return

        installed_apps = frappe.get_installed_apps()
        warnings = []

        for row in self.supported_doctypes:
            if not row.doctype_name:
                continue

            # Check if doctype exists
            if not frappe.db.exists("DocType", row.doctype_name):
                if row.enabled:
                    warnings.append(
                        _("DocType '{0}' does not exist. Configuration will be disabled.").format(
                            row.doctype_name
                        )
                    )
                    row.enabled = 0
                continue

            # Check if source app is installed
            if row.source_app and row.source_app not in installed_apps:
                if row.enabled:
                    warnings.append(
                        _("App '{0}' for '{1}' is not installed. Configuration will be disabled.").format(
                            row.source_app, row.doctype_name
                        )
                    )
                    row.enabled = 0

        if warnings:
            frappe.msgprint(
                "<br>".join(warnings),
                title=_("Doctype Configuration Warnings"),
                indicator="orange",
            )

    def get_template_id(self, doctype):
        """Get template ID for a given doctype from child table or legacy fields."""
        # First check child table
        config = self.get_doctype_config(doctype)
        if config and config.resend_template_id:
            return config.resend_template_id

        return None

    def get_doctype_config(self, doctype):
        """Get full configuration for a doctype from the child table."""
        if not self.supported_doctypes:
            return None

        for row in self.supported_doctypes:
            if row.doctype_name == doctype and row.enabled:
                return row

        return None

    def is_doctype_supported(self, doctype):
        """Check if a doctype is configured for Resend emails."""
        # Check child table first
        if self.supported_doctypes:
            for row in self.supported_doctypes:
                if row.doctype_name == doctype and row.enabled:
                    return True

        # Fallback: check if doctype has legacy template configured
        legacy_doctypes = ["Sales Invoice", "Quotation", "Sales Order", "Payment Request"]
        if doctype in legacy_doctypes and self._get_legacy_template_id(doctype):
            return True

        return False

    def get_available_doctypes(self):
        """Get list of doctypes available for email configuration based on installed apps."""
        installed_apps = frappe.get_installed_apps()
        available = []

        for doctype, info in DOCTYPE_REGISTRY.items():
            # Check if the app is installed
            if info["app"] not in installed_apps:
                continue

            # Check if the doctype actually exists
            if not frappe.db.exists("DocType", doctype):
                continue

            # Check if already configured
            is_configured = False
            if self.supported_doctypes:
                is_configured = any(
                    row.doctype_name == doctype for row in self.supported_doctypes
                )

            available.append(
                {
                    "doctype": doctype,
                    "app": info["app"],
                    "category": info["category"],
                    "default_recipient_field": info["recipient_field"],
                    "default_recipient_doctype": info["recipient_doctype"],
                    "is_configured": is_configured,
                }
            )

        return available

    def get_sender(self):
        """Get formatted sender string."""
        if self.default_sender_name:
            return f"{self.default_sender_name} <{self.default_sender_email}>"
        return self.default_sender_email

    def get_branding_dict(self) -> dict:
        """
        Return branding as dict for Vercel API payload.

        Includes both light and dark mode colors, logo info,
        contact info from Company, and rendered footer text.
        """
        social_links = []
        # Order: instagram, tiktok, facebook, youtube, x
        platforms = [
            ("instagram", getattr(self, "instagram_url", None)),
            ("tiktok", getattr(self, "tiktok_url", None)),
            ("facebook", getattr(self, "facebook_url", None)),
            ("youtube", getattr(self, "youtube_url", None)),
            ("twitter", getattr(self, "twitter_url", None)),
        ]
        for platform, url in platforms:
            if url:
                social_links.append({"platform": platform, "url": url})

        # Get contact info from Company
        company_email, company_phone, mailing_address = self._get_company_contact_info()

        return {
            # Company
            "company": self.company or "",

            # Logo
            "logo_url": self.logo_url or "",
            "logo_url_secondary": self.logo_url_secondary or self.logo_url or "",
            "logo_height": self.logo_height or 40,
            "logo_alt": self.logo_alt_text or self.company or "",
            "background_image_url": getattr(self, "background_image_url", "") or "",

            # Light mode colors
            "primary_color": self.primary_color or "#0066cc",
            "secondary_color": self.secondary_color or "",
            "tertiary_color": self.tertiary_color or "#6b7280",
            "text_color": self.text_color or "#333333",
            "background_color": self.background_color or "#f8f9fa",

            # Dark mode colors
            "primary_color_dark": self.primary_color_dark or self.primary_color or "#0066cc",
            "secondary_color_dark": self.secondary_color_dark or self.secondary_color or "",
            "tertiary_color_dark": getattr(self, "tertiary_color_dark", None) or self.tertiary_color or "#9ca3af",
            "text_color_dark": self.text_color_dark or "#ffffff",
            "background_color_dark": self.background_color_dark or "#1a1a1a",

            # Typography
            "font_family": self.font_family or "Arial, Helvetica, sans-serif",

            # Content
            "footer_text": self.render_footer(),
            "preheader": self.preheader_text or "",

            # Contact info (from Company)
            "company_email": company_email,
            "company_phone": company_phone,
            "mailing_address": mailing_address,

            # Social
            "website_url": self.website_url or "",
            "social_links": social_links,
            "instagram_url": getattr(self, "instagram_url", "") or "",
            "tiktok_url": getattr(self, "tiktok_url", "") or "",
            "facebook_url": getattr(self, "facebook_url", "") or "",
            "youtube_url": getattr(self, "youtube_url", "") or "",
            "twitter_url": getattr(self, "twitter_url", "") or "",
        }

    def _format_phone_number(self, phone: str) -> str:
        """
        Format phone number to +1 (XXX) XXX-XXXX format.

        Args:
            phone: Raw phone number string

        Returns:
            str: Formatted phone number or original if can't format
        """
        if not phone:
            return ""

        # Remove all non-digit characters
        digits = "".join(c for c in phone if c.isdigit())

        # Handle 10-digit US numbers
        if len(digits) == 10:
            return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"

        # Handle 11-digit numbers starting with 1
        if len(digits) == 11 and digits[0] == "1":
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

        # Return original if can't format
        return phone

    def _get_company_contact_info(self) -> tuple:
        """
        Fetch contact info from the linked Company record.

        Returns:
            tuple: (company_email, company_phone, mailing_address)
        """
        company_email = ""
        company_phone = ""
        mailing_address = ""

        if not self.company:
            return company_email, company_phone, mailing_address

        try:
            # Get Company details
            company_doc = frappe.get_doc("Company", self.company)
            company_email = company_doc.email or ""
            company_phone = self._format_phone_number(company_doc.phone_no or "")

            # Get primary address
            address_name = frappe.db.get_value(
                "Dynamic Link",
                {
                    "link_doctype": "Company",
                    "link_name": self.company,
                    "parenttype": "Address"
                },
                "parent"
            )

            if address_name:
                address = frappe.get_doc("Address", address_name)
                address_parts = []
                if address.address_line1:
                    address_parts.append(address.address_line1)
                if address.address_line2:
                    address_parts.append(address.address_line2)
                if address.city:
                    city_line = address.city
                    if address.state:
                        city_line += f", {address.state}"
                    if address.pincode:
                        city_line += f" {address.pincode}"
                    address_parts.append(city_line)
                mailing_address = ", ".join(address_parts)

        except Exception:
            pass

        return company_email, company_phone, mailing_address

    def render_footer(self) -> str:
        """Render Jinja footer template with company and year variables."""
        if not self.footer_text:
            return ""
        try:
            from jinja2 import Template
            t = Template(self.footer_text)
            return t.render(
                company=self.company or "",
                year=frappe.utils.now_datetime().year
            )
        except Exception:
            return self.footer_text


@frappe.whitelist()
def get_available_doctypes_for_site():
    """
    API endpoint to get doctypes available for email configuration.
    Used by the UI to populate the doctype selector.
    """
    settings = frappe.get_single("Email Service Settings")
    return settings.get_available_doctypes()


@frappe.whitelist()
def get_doctype_defaults(doctype):
    """Get default configuration values for a doctype."""
    if doctype not in DOCTYPE_REGISTRY:
        return {}

    info = DOCTYPE_REGISTRY[doctype]

    # Try to auto-detect source app
    source_app = info["app"]
    try:
        meta = frappe.get_meta(doctype)
        module = meta.module
        module_app = frappe.db.get_value("Module Def", module, "app_name")
        if module_app:
            source_app = module_app
    except Exception:
        pass

    return {
        "recipient_field": info["recipient_field"],
        "recipient_doctype": info["recipient_doctype"],
        "source_app": source_app,
    }


@frappe.whitelist()
def get_available_templates():
    """Return list of available email templates."""
    return [
        {"value": "magic-link", "label": "Magic Link"},
        {"value": "sales-invoice", "label": "Sales Invoice"},
        {"value": "quotation", "label": "Quotation"},
        {"value": "sales-order", "label": "Sales Order"},
        {"value": "purchase-order", "label": "Purchase Order"},
        {"value": "request-for-quotation", "label": "Request for Quotation"},
        {"value": "payment-request", "label": "Payment Request"},
        {"value": "password-reset", "label": "Password Reset"},
        {"value": "email-verification", "label": "Email Verification"},
        {"value": "welcome", "label": "Welcome"},
    ]


@frappe.whitelist()
def send_test_email(template="magic-link"):
    """
    Send a test email to the current user using the configured branding.

    Args:
        template: The email template to use (magic-link, document, notification, auth)

    Returns:
        dict: Success status and message
    """
    from emails.email_service.branding import get_company_branding
    from emails.email_service.vercel_client import send_email, VercelEmailError

    branding_doc = frappe.get_single("Email Service Settings")
    branding = get_company_branding()

    user = frappe.session.user
    user_email = frappe.db.get_value("User", user, "email")
    user_name = frappe.db.get_value("User", user, "full_name") or user

    if not user_email:
        frappe.throw(_("No email address found for current user"))

    # Template-specific data and subjects
    today = frappe.utils.formatdate(frappe.utils.today())
    due_date = frappe.utils.formatdate(frappe.utils.add_days(frappe.utils.today(), 15))

    template_configs = {
        "magic-link": {
            "subject": _("Sign in to {0}").format(branding_doc.company or "Your Account"),
            "data": {
                "magic_link": "https://example.com/auth/verify?token=test123",
                "user_name": user_name,
                "expiry_time": "10 minutes",
            },
        },
        "sales-invoice": {
            "subject": _("Invoice SINV-TEST-001 from {0}").format(branding_doc.company or "Company"),
            "data": {
                "invoice_number": "SINV-TEST-001",
                "invoice_date": today,
                "due_date": due_date,
                "project_name": "Test Project",
                "customer_name": user_name,
                "amount_due": "$1,234.56",
            },
        },
        "quotation": {
            "subject": _("Quotation QTN-TEST-001 from {0}").format(branding_doc.company or "Company"),
            "data": {
                "quotation_number": "QTN-TEST-001",
                "quotation_date": today,
                "valid_until": due_date,
                "customer_name": user_name,
                "total_amount": "$2,500.00",
            },
        },
        "sales-order": {
            "subject": _("Order SO-TEST-001 Confirmed"),
            "data": {
                "order_number": "SO-TEST-001",
                "order_date": today,
                "project_name": "Test Project",
                "customer_name": user_name,
                "order_total": "$1,500.00",
            },
        },
        "purchase-order": {
            "subject": _("Purchase Order PO-TEST-001 from {0}").format(branding_doc.company or "Company"),
            "data": {
                "po_number": "PO-TEST-001",
                "po_date": today,
                "supplier_name": user_name,
            },
        },
        "request-for-quotation": {
            "subject": _("Request for Quotation RFQ-TEST-001 from {0}").format(branding_doc.company or "Company"),
            "data": {
                "rfq_number": "RFQ-TEST-001",
                "rfq_date": today,
                "supplier_name": user_name,
                "document_link": "https://example.com/rfq/test",
            },
        },
        "payment-request": {
            "subject": _("Invoice {0} from {1}").format("SO-TEST-001", branding_doc.company or "Company"),
            "data": {
                "reference_number": "PR-TEST-001",
                "due_date": due_date,
                "project_name": "Test Project",
                "customer_name": user_name,
                "amount_requested": "$500.00",
                "stripe_payment_url": "https://example.com/pay/test",
            },
        },
        "password-reset": {
            "subject": _("Reset your {0} password").format(branding_doc.company or "Account"),
            "data": {
                "reset_link": "https://example.com/reset?token=test123",
                "user_name": user_name,
                "expiry_time": "1 hour",
            },
        },
        "email-verification": {
            "subject": _("Verify your {0} email").format(branding_doc.company or "Account"),
            "data": {
                "verification_link": "https://example.com/verify?token=test123",
                "user_name": user_name,
                "expiry_time": "24 hours",
            },
        },
        "welcome": {
            "subject": _("Welcome to {0}").format(branding_doc.company or "Our Platform"),
            "data": {
                "user_name": user_name,
                "login_link": "https://example.com/login",
            },
        },
    }

    config = template_configs.get(template, template_configs["magic-link"])

    try:
        result = send_email(
            template=template,
            to_email=user_email,
            subject=config["subject"],
            data=config["data"],
            branding=branding,
            tags=[
                {"name": "type", "value": "test"},
                {"name": "template", "value": template},
            ],
        )

        return {
            "success": True,
            "message": _("Test email ({0}) sent to {1}").format(template, user_email),
            "message_id": result.get("message_id"),
        }

    except VercelEmailError as e:
        frappe.log_error(
            title="Test Email Failed",
            message=str(e)
        )
        return {
            "success": False,
            "message": _("Failed to send test email: {0}").format(str(e)),
        }
