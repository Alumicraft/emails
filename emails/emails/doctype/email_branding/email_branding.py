# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Email Branding DocType

Stores per-company branding configuration for emails including:
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
        self.validate_logo_file()
        self.validate_default_branding()
        self.set_defaults()

    def validate_logo_file(self):
        """Ensure logo is valid image under 100KB."""
        for field in ["logo", "logo_dark"]:
            logo_url = getattr(self, field, None)
            if not logo_url:
                continue

            file_doc = frappe.db.get_value(
                "File",
                {"file_url": logo_url},
                ["file_size", "file_name"],
                as_dict=True
            )

            if not file_doc:
                continue

            # Check file size
            if file_doc.file_size and file_doc.file_size > 100 * 1024:
                frappe.throw(
                    _("{0} file size must be under 100KB for optimal email delivery. "
                      "Current size: {1}KB").format(
                        field.replace("_", " ").title(),
                        round(file_doc.file_size / 1024, 1)
                    )
                )

            # Check file type
            allowed_types = (".png", ".jpg", ".jpeg", ".gif")
            if not logo_url.lower().endswith(allowed_types):
                frappe.throw(
                    _("{0} must be one of: {1}. SVG is not recommended for email.").format(
                        field.replace("_", " ").title(),
                        ", ".join(allowed_types)
                    )
                )

    def validate_default_branding(self):
        """Ensure only one branding is marked as default."""
        if self.is_default:
            frappe.db.sql("""
                UPDATE `tabEmail Branding`
                SET is_default = 0
                WHERE is_default = 1 AND name != %s
            """, self.name)

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
        and rendered footer text.
        """
        social_links = []
        platforms = [
            ("website", self.website_url),
            ("facebook", self.facebook_url),
            ("linkedin", self.linkedin_url),
            ("twitter", self.twitter_url),
            ("instagram", self.instagram_url),
        ]
        for platform, url in platforms:
            if url:
                social_links.append({"platform": platform, "url": url})

        return {
            # Company
            "company": self.company or "",

            # Logo
            "logo_height": self.logo_height or 40,
            "logo_alt": self.logo_alt_text or self.company or "",

            # Light mode colors
            "primary_color": self.primary_color or "#0066cc",
            "secondary_color": self.secondary_color or "",
            "text_color": self.text_color or "#333333",
            "background_color": self.background_color or "#f8f9fa",

            # Dark mode colors
            "primary_color_dark": self.primary_color_dark or self.primary_color or "#0066cc",
            "secondary_color_dark": self.secondary_color_dark or self.secondary_color or "",
            "text_color_dark": self.text_color_dark or "#ffffff",
            "background_color_dark": self.background_color_dark or "#1a1a1a",

            # Typography
            "font_family": self.font_family or "Arial, Helvetica, sans-serif",

            # Content
            "footer_text": self.render_footer(),
            "preheader": self.preheader_text or "",

            # Social
            "website_url": self.website_url or "",
            "social_links": social_links,
        }

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
def send_test_email(branding_name: str):
    """
    Send a test email to the current user using the specified branding.

    Args:
        branding_name: Name of the Email Branding document

    Returns:
        dict: Success status and message
    """
    from emails.email_service.branding import get_company_branding
    from emails.email_service.vercel_client import send_email, VercelEmailError

    branding_doc = frappe.get_doc("Email Branding", branding_name)
    branding = get_company_branding(branding_doc.company)

    user = frappe.session.user
    user_email = frappe.db.get_value("User", user, "email")

    if not user_email:
        frappe.throw(_("No email address found for current user"))

    try:
        result = send_email(
            template="document",
            to_email=user_email,
            subject=_("Test Email - {0} Branding").format(branding_doc.company),
            data={
                "document_type": "Test Email",
                "document_number": "TEST-001",
                "document_date": frappe.utils.formatdate(frappe.utils.today()),
                "customer_name": frappe.db.get_value("User", user, "full_name") or user,
                "total_amount": "$1,234.56",
                "custom_message": _(
                    "This is a test email to preview your email branding. "
                    "If you can see this message with your company logo and colors, "
                    "your branding is configured correctly."
                ),
                "items": [
                    {"item_name": "Sample Item 1", "qty": 2, "rate": "$100.00", "amount": "$200.00"},
                    {"item_name": "Sample Item 2", "qty": 1, "rate": "$500.00", "amount": "$500.00"},
                ],
            },
            branding=branding,
            tags=[
                {"name": "type", "value": "test"},
                {"name": "branding", "value": branding_name},
            ],
        )

        return {
            "success": True,
            "message": _("Test email sent to {0}").format(user_email),
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
