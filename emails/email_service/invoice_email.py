import frappe
from frappe.utils import formatdate

from emails.email_service.resend_client import send_template_email, ResendError
from emails.email_service.utils import (
    get_email_settings,
    get_company_info,
    get_customer_primary_email,
    format_currency_amount,
    get_document_pdf,
    pdf_to_base64,
    create_communication_log,
    get_document_link,
)


def send_invoice_email(invoice_name, to_email=None, cc=None, bcc=None, custom_message=None):
    """Send Sales Invoice email via Resend."""
    settings = get_email_settings()

    invoice = frappe.get_doc("Sales Invoice", invoice_name)

    if invoice.docstatus != 1:
        frappe.throw(f"Invoice {invoice_name} must be submitted before sending email")

    if not to_email:
        to_email = get_customer_primary_email(invoice.customer)

    if not to_email:
        frappe.throw(f"No email address found for customer {invoice.customer}")

    company_info = get_company_info(invoice.company)

    template_id = settings.invoice_template_id
    if not template_id:
        frappe.throw("Invoice template ID not configured in Email Service Settings")

    template_data = {
        "document_type": "Invoice",
        "customer_name": invoice.customer_name or invoice.customer,
        "invoice_number": invoice.name,
        "document_number": invoice.name,
        "invoice_date": formatdate(invoice.posting_date),
        "document_date": formatdate(invoice.posting_date),
        "due_date": formatdate(invoice.due_date) if invoice.due_date else "",
        "total_amount": format_currency_amount(invoice.grand_total, invoice.currency),
        "outstanding_amount": format_currency_amount(invoice.outstanding_amount, invoice.currency),
        "currency": invoice.currency,
        "company_name": company_info["company_name"],
        "company_logo": company_info["company_logo"] or "",
        "company_address": company_info["company_address"] or "",
        "company_phone": company_info["phone"] or "",
        "company_email": company_info["email"] or "",
        "document_link": get_document_link("Sales Invoice", invoice_name),
        "custom_message": custom_message or "",
        "subject": f"Invoice {invoice.name} from {company_info['company_name']}",
    }

    items_summary = []
    for item in invoice.items[:5]:
        items_summary.append({
            "item_name": item.item_name,
            "qty": item.qty,
            "rate": format_currency_amount(item.rate, invoice.currency),
            "amount": format_currency_amount(item.amount, invoice.currency),
        })
    template_data["items"] = items_summary
    template_data["items_count"] = len(invoice.items)

    try:
        pdf_bytes, filename = get_document_pdf("Sales Invoice", invoice_name)
        attachments = [{
            "filename": filename,
            "content": pdf_to_base64(pdf_bytes)
        }]
    except Exception as e:
        frappe.log_error(title="Invoice PDF Generation Failed", message=str(e))
        attachments = None

    try:
        result = send_template_email(
            template_id=template_id,
            to_email=to_email,
            template_data=template_data,
            subject=template_data["subject"],
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            tags=[
                {"name": "doctype", "value": "Sales Invoice"},
                {"name": "document", "value": invoice_name}
            ]
        )

        create_communication_log(
            doctype="Sales Invoice",
            docname=invoice_name,
            recipient=to_email,
            subject=template_data["subject"],
            content=f"Invoice email sent via Resend",
            status="Sent",
            message_id=result.get("message_id")
        )

        return {
            "success": True,
            "message": "Invoice email sent successfully",
            "message_id": result.get("message_id"),
            "recipient": to_email
        }

    except ResendError as e:
        create_communication_log(
            doctype="Sales Invoice",
            docname=invoice_name,
            recipient=to_email,
            subject=template_data["subject"],
            content=f"Invoice email failed",
            status="Error",
            error_msg=str(e)
        )

        if settings.fallback_to_erpnext:
            return _send_fallback_email(invoice, to_email, template_data, attachments)

        raise


def _send_fallback_email(invoice, to_email, template_data, attachments):
    """Send email using ERPNext's default email system as fallback."""
    try:
        frappe.sendmail(
            recipients=[to_email],
            subject=template_data["subject"],
            message=f"""
                <p>Dear {template_data['customer_name']},</p>
                <p>Please find attached your invoice {template_data['invoice_number']}.</p>
                <p>Total Amount: {template_data['total_amount']}</p>
                <p>Due Date: {template_data['due_date']}</p>
                <p>Best regards,<br>{template_data['company_name']}</p>
            """,
            reference_doctype="Sales Invoice",
            reference_name=invoice.name,
        )

        return {
            "success": True,
            "message": "Invoice email sent via ERPNext fallback",
            "fallback": True,
            "recipient": to_email
        }

    except Exception as e:
        frappe.log_error(title="Fallback Email Failed", message=str(e))
        raise
