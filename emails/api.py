"""API Module - Whitelisted methods for frontend calls"""

import frappe
from frappe import _


@frappe.whitelist()
def send_invoice_email(invoice_name, to_email=None, cc=None, bcc=None, custom_message=None):
    """Send Sales Invoice email via Resend."""
    try:
        frappe.has_permission("Sales Invoice", "email", invoice_name, throw=True)

        from emails.email_service.invoice_email import send_invoice_email as _send

        result = _send(
            invoice_name,
            to_email=to_email,
            cc=cc,
            bcc=bcc,
            custom_message=custom_message
        )

        return result

    except frappe.PermissionError:
        return {
            "success": False,
            "message": _("You don't have permission to send email for this invoice")
        }
    except Exception as e:
        frappe.log_error(
            title="Send Invoice Email API Error",
            message=frappe.get_traceback()
        )
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def send_quotation_email(quotation_name, to_email=None, cc=None, bcc=None, custom_message=None):
    """Send Quotation email via Resend."""
    try:
        frappe.has_permission("Quotation", "email", quotation_name, throw=True)

        from emails.email_service.quotation_email import send_quotation_email as _send

        result = _send(
            quotation_name,
            to_email=to_email,
            cc=cc,
            bcc=bcc,
            custom_message=custom_message
        )

        return result

    except frappe.PermissionError:
        return {
            "success": False,
            "message": _("You don't have permission to send email for this quotation")
        }
    except Exception as e:
        frappe.log_error(
            title="Send Quotation Email API Error",
            message=frappe.get_traceback()
        )
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def send_sales_order_email(sales_order_name, to_email=None, cc=None, bcc=None, custom_message=None):
    """Send Sales Order confirmation email via Resend."""
    try:
        frappe.has_permission("Sales Order", "email", sales_order_name, throw=True)

        from emails.email_service.sales_order_email import send_sales_order_email as _send

        result = _send(
            sales_order_name,
            to_email=to_email,
            cc=cc,
            bcc=bcc,
            custom_message=custom_message
        )

        return result

    except frappe.PermissionError:
        return {
            "success": False,
            "message": _("You don't have permission to send email for this sales order")
        }
    except Exception as e:
        frappe.log_error(
            title="Send Sales Order Email API Error",
            message=frappe.get_traceback()
        )
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def send_document_email(doctype, docname, to_email=None, cc=None, bcc=None, custom_message=None):
    """Generic method to send email for any supported document type."""
    handlers = {
        "Sales Invoice": send_invoice_email,
        "Quotation": send_quotation_email,
        "Sales Order": send_sales_order_email,
    }

    handler = handlers.get(doctype)

    if not handler:
        return {
            "success": False,
            "message": _("Email sending not supported for {0}").format(doctype)
        }

    return handler(docname, to_email=to_email, cc=cc, bcc=bcc, custom_message=custom_message)


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
            "message": _("You don't have permission to test the connection")
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def get_resend_status():
    """Get current Resend service status and configuration."""
    try:
        from emails.email_service.email_override import check_resend_status

        return check_resend_status()

    except Exception as e:
        return {
            "enabled": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_customer_email(customer_name):
    """Get primary email for a customer."""
    try:
        from emails.email_service.utils import get_customer_primary_email

        email = get_customer_primary_email(customer_name)

        if email:
            return {
                "success": True,
                "email": email
            }
        else:
            return {
                "success": False,
                "message": _("No email found for customer {0}").format(customer_name)
            }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


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
            tags=[{"name": "type", "value": "test"}]
        )

        return {
            "success": True,
            "message": _("Test email sent successfully to {0}").format(to_email),
            "message_id": result.get("message_id")
        }

    except Exception as e:
        frappe.log_error(title="Test Email Failed", message=str(e))
        return {
            "success": False,
            "message": str(e)
        }
