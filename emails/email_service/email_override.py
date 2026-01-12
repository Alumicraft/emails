"""
Email Override Module - Intercepts ERPNext email sending for specific doctypes.

This module overrides frappe.core.doctype.communication.email.make to intercept
email sending BEFORE ERPNext queues its own email, preventing duplicate sends.
"""

import frappe
from frappe import _
from frappe.core.doctype.communication import email as frappe_email

from emails.email_service.utils import should_use_resend, get_email_settings
from emails.email_service.resend_client import ResendError


DOCTYPE_EMAIL_HANDLERS = {
    "Sales Invoice": "emails.email_service.invoice_email.send_invoice_email",
    "Quotation": "emails.email_service.quotation_email.send_quotation_email",
    "Sales Order": "emails.email_service.sales_order_email.send_sales_order_email",
}


@frappe.whitelist()
def make_communication_email(
    doctype=None,
    name=None,
    content=None,
    subject=None,
    sent_or_received="Sent",
    sender=None,
    sender_full_name=None,
    recipients=None,
    communication_medium="Email",
    send_email=False,
    print_html=None,
    print_format=None,
    attachments=None,
    send_me_a_copy=False,
    cc=None,
    bcc=None,
    read_receipt=None,
    print_letterhead=True,
    email_template=None,
    communication_type=None,
):
    """
    Override for frappe.core.doctype.communication.email.make

    Intercepts email sending to route through Resend for supported doctypes,
    preventing ERPNext from sending duplicate emails.
    """
    # Check if this should be handled by Resend
    if (
        send_email
        and sent_or_received == "Sent"
        and communication_medium == "Email"
        and doctype
        and name
        and should_use_resend(doctype)
    ):
        handler_path = DOCTYPE_EMAIL_HANDLERS.get(doctype)

        if handler_path and recipients:
            try:
                handler = frappe.get_attr(handler_path)

                # Send via Resend
                result = handler(
                    name,
                    to_email=recipients,
                    cc=cc,
                    bcc=bcc,
                    custom_message=content,
                    skip_communication=True  # We'll create it via the original make
                )

                if result.get("success"):
                    # Call original make with send_email=False to create Communication only
                    comm = frappe_email.make(
                        doctype=doctype,
                        name=name,
                        content=content,
                        subject=subject,
                        sent_or_received=sent_or_received,
                        sender=sender,
                        sender_full_name=sender_full_name,
                        recipients=recipients,
                        communication_medium=communication_medium,
                        send_email=False,  # Don't let ERPNext send email
                        print_html=print_html,
                        print_format=print_format,
                        attachments=attachments,
                        send_me_a_copy=False,  # We handle this via Resend
                        cc=cc,
                        bcc=bcc,
                        read_receipt=read_receipt,
                        print_letterhead=print_letterhead,
                        email_template=email_template,
                        communication_type=communication_type,
                    )

                    # Update the Communication with Resend message ID
                    if comm and result.get("message_id"):
                        frappe.db.set_value(
                            "Communication",
                            comm.name,
                            {
                                "message_id": result.get("message_id"),
                                "email_status": "Open",
                                "delivery_status": "Sent"
                            },
                            update_modified=False
                        )

                    frappe.msgprint(
                        _("Email sent successfully via Resend"),
                        indicator="green",
                        alert=True
                    )

                    return comm

            except ResendError as e:
                frappe.log_error(
                    title="Resend Email Failed",
                    message=f"DocType: {doctype}\nDocument: {name}\nError: {str(e)}"
                )

                # Check if we should fallback to ERPNext
                try:
                    settings = get_email_settings()
                    if not settings.fallback_to_erpnext:
                        frappe.throw(_("Email sending failed: {0}").format(str(e)))
                except Exception:
                    pass

                # Fall through to original make (will use ERPNext email)
                frappe.msgprint(
                    _("Resend failed, falling back to ERPNext email"),
                    indicator="orange",
                    alert=True
                )

            except Exception as e:
                frappe.log_error(
                    title="Email Override Error",
                    message=frappe.get_traceback()
                )
                # Fall through to original make

    # For non-Resend cases or fallback, call the original function
    return frappe_email.make(
        doctype=doctype,
        name=name,
        content=content,
        subject=subject,
        sent_or_received=sent_or_received,
        sender=sender,
        sender_full_name=sender_full_name,
        recipients=recipients,
        communication_medium=communication_medium,
        send_email=send_email,
        print_html=print_html,
        print_format=print_format,
        attachments=attachments,
        send_me_a_copy=send_me_a_copy,
        cc=cc,
        bcc=bcc,
        read_receipt=read_receipt,
        print_letterhead=print_letterhead,
        email_template=email_template,
        communication_type=communication_type,
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
