# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Email Branding DocType (Single)

Stores global branding configuration for emails including:
- Logo (light and dark mode)
- Colors (light and dark mode)
- Typography
- Footer text with Jinja support
- Social links
"""

import frappe
from frappe import _
from frappe.model.document import Document


class EmailBranding(Document):
    def validate(self):
        self.set_defaults()

    def set_defaults(self):
        """Set sensible defaults for optional fields."""
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

    branding_doc = frappe.get_single("Email Branding")
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
