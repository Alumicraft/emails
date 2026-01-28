"""
Email Override Module - Intercepts ERPNext email sending for configured doctypes.

This module overrides frappe.core.doctype.communication.email.make to intercept
email sending BEFORE ERPNext queues its own email, preventing duplicate sends.

Now supports dynamic doctype configuration via Email Service Settings child table.
"""

import frappe
from frappe import _
from frappe.core.doctype.communication import email as frappe_email

from emails.email_service.utils import should_use_resend, get_email_settings
from emails.email_service.resend_client import ResendError


def get_email_handler(doctype):
    """
    Get the email handler for a doctype.

    For all configured doctypes, uses the generic email handler.

    Args:
        doctype: The document type

    Returns:
        str: Handler path or None
    """
    try:
        settings = frappe.get_single("Email Service Settings")

        if settings.is_doctype_supported(doctype):
            # Use generic handler for all configured doctypes
            return "emails.email_service.generic_email.send_document_email"

    except Exception:
        pass

    return None


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

    Intercepts email sending to route through Resend for configured doctypes,
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
        handler_path = get_email_handler(doctype)

        if handler_path and recipients:
            try:
                handler = frappe.get_attr(handler_path)

                # Send via Resend using generic handler
                result = handler(
                    doctype,
                    name,
                    to_email=recipients,
                    cc=cc,
                    bcc=bcc,
                    custom_message=content,
                    skip_communication=True,  # We'll create it below
                )

                if result.get("success"):
                    # Create Communication directly - bypass frappe_email.make entirely
                    # to avoid email account validation
                    settings = get_email_settings()

                    comm = frappe.get_doc(
                        {
                            "doctype": "Communication",
                            "communication_type": communication_type or "Communication",
                            "communication_medium": "Email",
                            "sent_or_received": "Sent",
                            "subject": subject or f"Email for {doctype} {name}",
                            "content": content or "",
                            "sender": sender or settings.default_sender_email,
                            "sender_full_name": sender_full_name
                            or settings.default_sender_name,
                            "recipients": recipients,
                            "cc": cc,
                            "bcc": bcc,
                            "reference_doctype": doctype,
                            "reference_name": name,
                            "message_id": result.get("message_id"),
                            "email_status": "Open",
                            "delivery_status": "Sent",
                            "status": "Linked",
                        }
                    )
                    comm.insert(ignore_permissions=True)
                    frappe.db.commit()

                    frappe.msgprint(
                        _("Email sent successfully via Resend"),
                        indicator="green",
                        alert=True,
                    )

                    return comm

            except ResendError as e:
                frappe.log_error(
                    title="Resend Email Failed",
                    message=f"DocType: {doctype}\nDocument: {name}\nError: {str(e)}",
                )

                # Check if we should fallback to ERPNext
                try:
                    settings = frappe.get_single("Email Service Settings")
                    if settings.fallback_to_erpnext:
                        frappe.msgprint(
                            _("Resend failed, falling back to ERPNext email"),
                            indicator="orange",
                            alert=True,
                        )
                        # Fall through to original make below
                    else:
                        frappe.throw(_("Email sending failed: {0}").format(str(e)))
                except Exception:
                    frappe.throw(_("Email sending failed: {0}").format(str(e)))

                # Only reaches here if fallback is enabled
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

            except Exception as e:
                frappe.log_error(
                    title="Email Override Error", message=frappe.get_traceback()
                )
                frappe.throw(_("Email sending failed. Check Error Log for details."))

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
        "action": "emails.api.send_document_email",
        "args": {"doctype": doctype, "docname": docname},
    }


def check_resend_status():
    """Check if Resend service is properly configured and enabled."""
    try:
        settings = frappe.get_single("Email Service Settings")

        # Build templates configured dict from child table
        templates_configured = {}
        if settings.supported_doctypes:
            for row in settings.supported_doctypes:
                if row.enabled:
                    templates_configured[row.doctype_name] = bool(row.resend_template_id)

        # Also check legacy fields for backward compatibility
        legacy_templates = {
            "Sales Invoice": bool(getattr(settings, "invoice_template_id", None)),
            "Quotation": bool(settings.quotation_template_id),
            "Sales Order": bool(settings.sales_order_template_id),
            "Payment Request": bool(getattr(settings, "payment_request_template_id", None)),
        }

        # Merge, preferring child table config
        for doctype, has_template in legacy_templates.items():
            if doctype not in templates_configured:
                templates_configured[doctype] = has_template

        return {
            "enabled": settings.enabled,
            "configured": bool(settings.get_password("resend_api_key")),
            "sender_email": settings.default_sender_email,
            "templates_configured": templates_configured,
            "configured_doctypes": [
                row.doctype_name
                for row in (settings.supported_doctypes or [])
                if row.enabled
            ],
        }
    except Exception as e:
        return {"enabled": False, "error": str(e)}
