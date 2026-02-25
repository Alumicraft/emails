"""API Module - Whitelisted methods for frontend calls"""

import frappe
from frappe import _


@frappe.whitelist()
def send_invoice_email(invoice_name, to_email=None, cc=None, bcc=None, custom_message=None):
    """Send Sales Invoice email via Resend."""
    return send_document_email(
        "Sales Invoice",
        invoice_name,
        to_email=to_email,
        cc=cc,
        bcc=bcc,
        custom_message=custom_message,
    )


@frappe.whitelist()
def send_quotation_email(quotation_name, to_email=None, cc=None, bcc=None, custom_message=None):
    """Send Quotation email via Resend."""
    return send_document_email(
        "Quotation",
        quotation_name,
        to_email=to_email,
        cc=cc,
        bcc=bcc,
        custom_message=custom_message,
    )


@frappe.whitelist()
def send_sales_order_email(
    sales_order_name, to_email=None, cc=None, bcc=None, custom_message=None
):
    """Send Sales Order confirmation email via Resend."""
    return send_document_email(
        "Sales Order",
        sales_order_name,
        to_email=to_email,
        cc=cc,
        bcc=bcc,
        custom_message=custom_message,
    )


@frappe.whitelist()
def send_payment_request_email(payment_request_name, to_email=None, cc=None, bcc=None, custom_message=None):
    """Send Payment Request email via Resend."""
    return send_document_email(
        "Payment Request",
        payment_request_name,
        to_email=to_email,
        cc=cc,
        bcc=bcc,
        custom_message=custom_message,
    )


@frappe.whitelist()
def send_document_email(doctype, docname, to_email=None, cc=None, bcc=None, custom_message=None):
    """Generic method to send email for any document type."""
    try:
        frappe.has_permission(doctype, "email", docname, throw=True)

        settings = frappe.get_single("Email Service Settings")

        if not settings.enabled:
            return {
                "success": False,
                "message": _("Email service is not enabled"),
            }

        from emails.email_service.generic_email import send_document_email as _send

        return _send(
            doctype,
            docname,
            to_email=to_email,
            cc=cc,
            bcc=bcc,
            custom_message=custom_message,
        )

    except frappe.PermissionError:
        return {
            "success": False,
            "message": _("You don't have permission to send email for this document"),
        }
    except Exception as e:
        frappe.log_error(
            title=f"Send {doctype} Email API Error", message=frappe.get_traceback()
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def test_resend_connection():
    """Test Resend API connection."""
    try:
        frappe.has_permission("Email Service Settings", "read", throw=True)

        from emails.email_service.resend_client import test_connection

        return test_connection()

    except frappe.PermissionError:
        return {
            "success": False,
            "message": _("You don't have permission to test the connection"),
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_resend_status():
    """Get current Resend service status and configuration."""
    try:
        from emails.email_service.email_override import check_resend_status

        return check_resend_status()

    except Exception as e:
        return {"enabled": False, "error": str(e)}


@frappe.whitelist()
def get_customer_email(customer_name):
    """Get primary email for a customer."""
    try:
        from emails.email_service.utils import get_customer_primary_email

        email = get_customer_primary_email(customer_name)

        if email:
            return {"success": True, "email": email}
        else:
            return {
                "success": False,
                "message": _("No email found for customer {0}").format(customer_name),
            }

    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_party_email(doctype, party_name):
    """Get primary email for any party type."""
    try:
        from emails.email_service.generic_email import get_party_email as _get_party_email

        email = _get_party_email(doctype, party_name)

        if email:
            return {"success": True, "email": email}
        else:
            return {
                "success": False,
                "message": _("No email found for {0} {1}").format(doctype, party_name),
            }

    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def send_test_email(to_email):
    """Send a test email to verify Resend configuration."""
    try:
        if "System Manager" not in frappe.get_roles():
            frappe.throw(_("Only System Managers can send test emails"))

        from emails.email_service.resend_client import send_email

        result = send_email(
            to_email=to_email,
            subject="Test Email from Emails App",
            html_content="""
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Test Email</h2>
                    <p>This is a test email from your Emails app integration.</p>
                    <p>If you received this email, your Resend configuration is working correctly!</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Sent via Emails App
                    </p>
                </div>
            """,
            tags=[{"name": "type", "value": "test"}],
        )

        return {
            "success": True,
            "message": _("Test email sent successfully to {0}").format(to_email),
            "message_id": result.get("message_id"),
        }

    except Exception as e:
        frappe.log_error(title="Test Email Failed", message=str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def check_doctype_email_enabled(doctype):
    """Check if email sending is enabled (service enabled and configured)."""
    try:
        settings = frappe.get_single("Email Service Settings")

        if not settings.enabled:
            return {"enabled": False}

        if not settings.get_password("resend_api_key"):
            return {"enabled": False}

        return {"enabled": True}

    except Exception:
        return {"enabled": False}


@frappe.whitelist()
def get_document_recipient(doctype, docname):
    """Get default recipient email for a document."""
    try:
        from emails.email_service.utils import (
            get_customer_primary_email,
            get_supplier_primary_email
        )
        from emails.email_service.generic_email import resolve_recipient_email
        from emails.emails.doctype.email_service_settings.email_service_settings import DOCTYPE_REGISTRY

        doc = frappe.get_doc(doctype, docname)

        # Try using the generic resolver (uses DOCTYPE_REGISTRY internally)
        email = resolve_recipient_email(doc)

        if email:
            return {"email": email}

        # Fallback to legacy resolution
        if hasattr(doc, "customer") and doc.customer:
            email = get_customer_primary_email(doc.customer)
        elif doctype == "Quotation":
            if doc.quotation_to == "Customer" and doc.party_name:
                email = get_customer_primary_email(doc.party_name)
            elif hasattr(doc, "contact_email") and doc.contact_email:
                email = doc.contact_email
        elif doctype == "Payment Request":
            if hasattr(doc, "email_to") and doc.email_to:
                email = doc.email_to
            elif doc.party_type == "Customer" and doc.party:
                email = get_customer_primary_email(doc.party)
        elif hasattr(doc, "supplier") and doc.supplier:
            email = get_supplier_primary_email(doc.supplier)

        if not email and hasattr(doc, "contact_email") and doc.contact_email:
            email = doc.contact_email

        return {"email": email} if email else {"email": None}

    except Exception as e:
        frappe.log_error(title="Get Document Recipient Error", message=str(e))
        return {"email": None}


@frappe.whitelist()
def get_email_supported_doctypes():
    """Return list of doctypes that have an email template configured."""
    from emails.email_service.generic_email import DOCTYPE_TEMPLATE_MAP

    return list(DOCTYPE_TEMPLATE_MAP.keys())
