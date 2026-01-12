"""
Email Override Module - Intercepts ERPNext email sending for specific doctypes.
"""

import frappe
from frappe import _

from emails.email_service.utils import should_use_resend, get_email_settings
from emails.email_service.resend_client import ResendError


DOCTYPE_EMAIL_HANDLERS = {
    "Sales Invoice": "emails.email_service.invoice_email.send_invoice_email",
    "Quotation": "emails.email_service.quotation_email.send_quotation_email",
    "Sales Order": "emails.email_service.sales_order_email.send_sales_order_email",
}


def before_communication_insert(doc, method):
    """Hook called before Communication document is inserted."""
    if doc.communication_medium != "Email":
        return

    if doc.sent_or_received != "Sent":
        return

    if not doc.reference_doctype or not doc.reference_name:
        return

    if not should_use_resend(doc.reference_doctype):
        return

    handler_path = DOCTYPE_EMAIL_HANDLERS.get(doc.reference_doctype)
    if not handler_path:
        return

    try:
        doc.flags.resend_handled = True

        to_email = doc.recipients
        if not to_email:
            return

        cc = doc.cc if hasattr(doc, "cc") and doc.cc else None
        bcc = doc.bcc if hasattr(doc, "bcc") and doc.bcc else None

        handler = frappe.get_attr(handler_path)

        result = handler(
            doc.reference_name,
            to_email=to_email,
            cc=cc,
            bcc=bcc,
            custom_message=doc.content
        )

        if result.get("success"):
            doc.message_id = result.get("message_id")
            doc.email_status = "Sent"
            doc.flags.skip_email_sending = True

            frappe.msgprint(
                _("Email sent successfully via Resend"),
                indicator="green",
                alert=True
            )
        else:
            frappe.msgprint(
                _("Email sending failed. Check Error Log for details."),
                indicator="red",
                alert=True
            )

    except ResendError as e:
        frappe.log_error(
            title="Resend Email Override Failed",
            message=f"DocType: {doc.reference_doctype}\nDocument: {doc.reference_name}\nError: {str(e)}"
        )

        try:
            settings = get_email_settings()
            if not settings.fallback_to_erpnext:
                frappe.throw(f"Email sending failed: {str(e)}")
        except Exception:
            pass

    except Exception as e:
        frappe.log_error(
            title="Email Override Error",
            message=frappe.get_traceback()
        )


def on_communication_update(doc, method):
    """Hook called when Communication document is updated."""
    pass


def get_resend_email_action(doctype, docname):
    """Get the email action link for sending via Resend."""
    if not should_use_resend(doctype):
        return None

    return {
        "label": _("Send via Resend"),
        "action": f"emails.api.send_document_email",
        "args": {
            "doctype": doctype,
            "docname": docname
        }
    }


def check_resend_status():
    """Check if Resend service is properly configured and enabled."""
    try:
        settings = frappe.get_single("Email Service Settings")

        return {
            "enabled": settings.enabled,
            "configured": bool(settings.get_password("resend_api_key")),
            "sender_email": settings.default_sender_email,
            "templates_configured": {
                "Sales Invoice": bool(settings.invoice_template_id),
                "Quotation": bool(settings.quotation_template_id),
                "Sales Order": bool(settings.sales_order_template_id),
            }
        }
    except Exception as e:
        return {
            "enabled": False,
            "error": str(e)
        }
