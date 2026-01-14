import frappe
from frappe.utils import formatdate, add_days

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


def send_quotation_email(quotation_name, to_email=None, cc=None, bcc=None, custom_message=None, skip_communication=False):
    """Send Quotation email via Resend."""
    settings = get_email_settings()

    quotation = frappe.get_doc("Quotation", quotation_name)

    if quotation.docstatus != 1:
        frappe.throw(f"Quotation {quotation_name} must be submitted before sending email")

    if not to_email:
        if quotation.quotation_to == "Customer" and quotation.party_name:
            to_email = get_customer_primary_email(quotation.party_name)
        elif quotation.contact_email:
            to_email = quotation.contact_email

    if not to_email:
        frappe.throw(f"No email address found for {quotation.party_name}")

    company_info = get_company_info(quotation.company)

    template_id = settings.quotation_template_id or ""

    valid_until = ""
    if quotation.valid_till:
        valid_until = formatdate(quotation.valid_till)
    elif quotation.transaction_date:
        valid_until = formatdate(add_days(quotation.transaction_date, 30))

    template_data = {
        "document_type": "Quotation",
        "customer_name": quotation.customer_name or quotation.party_name,
        "quotation_number": quotation.name,
        "document_number": quotation.name,
        "quotation_date": formatdate(quotation.transaction_date),
        "document_date": formatdate(quotation.transaction_date),
        "valid_until": valid_until,
        "total_amount": format_currency_amount(quotation.grand_total, quotation.currency),
        "currency": quotation.currency,
        "company_name": company_info["company_name"],
        "company_logo": company_info["company_logo"] or "",
        "company_address": company_info["company_address"] or "",
        "company_phone": company_info["phone"] or "",
        "company_email": company_info["email"] or "",
        "document_link": get_document_link("Quotation", quotation_name),
        "custom_message": custom_message or "",
        "subject": f"Quotation {quotation.name} from {company_info['company_name']}",
    }

    items_summary = []
    for item in quotation.items[:5]:
        items_summary.append({
            "item_name": item.item_name,
            "qty": item.qty,
            "rate": format_currency_amount(item.rate, quotation.currency),
            "amount": format_currency_amount(item.amount, quotation.currency),
        })
    template_data["items"] = items_summary
    template_data["items_count"] = len(quotation.items)

    try:
        pdf_bytes, filename = get_document_pdf("Quotation", quotation_name)
        attachments = [{
            "filename": filename,
            "content": pdf_to_base64(pdf_bytes)
        }]
    except Exception as e:
        frappe.log_error(title="Quotation PDF Generation Failed", message=str(e))
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
                {"name": "doctype", "value": "quotation"},
                {"name": "document", "value": quotation_name.replace("-", "_").replace(" ", "_")}
            ]
        )

        if not skip_communication:
            create_communication_log(
                doctype="Quotation",
                docname=quotation_name,
                recipient=to_email,
                subject=template_data["subject"],
                content=f"Quotation email sent via Resend",
                status="Sent",
                message_id=result.get("message_id")
            )

        return {
            "success": True,
            "message": "Quotation email sent successfully",
            "message_id": result.get("message_id"),
            "recipient": to_email
        }

    except ResendError as e:
        if not skip_communication:
            create_communication_log(
                doctype="Quotation",
                docname=quotation_name,
                recipient=to_email,
                subject=template_data["subject"],
                content=f"Quotation email failed",
                status="Error",
                error_msg=str(e)
            )

        raise
