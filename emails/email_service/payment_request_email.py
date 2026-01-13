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


def send_payment_request_email(payment_request_name, to_email=None, cc=None, bcc=None, custom_message=None, skip_communication=False):
    """Send Payment Request email via Resend."""
    settings = get_email_settings()

    payment_request = frappe.get_doc("Payment Request", payment_request_name)

    if payment_request.docstatus != 1:
        frappe.throw(f"Payment Request {payment_request_name} must be submitted before sending email")

    # Determine recipient email
    if not to_email:
        if payment_request.email_to:
            to_email = payment_request.email_to
        elif payment_request.party_type == "Customer" and payment_request.party:
            to_email = get_customer_primary_email(payment_request.party)
        elif hasattr(payment_request, "contact_email") and payment_request.contact_email:
            to_email = payment_request.contact_email

    if not to_email:
        frappe.throw(f"No email address found for Payment Request {payment_request_name}")

    company_info = get_company_info(payment_request.company)

    template_id = settings.payment_request_template_id or ""

    # Get the stripe_invoice_url custom field if it exists
    stripe_invoice_url = ""
    if hasattr(payment_request, "stripe_invoice_url"):
        stripe_invoice_url = payment_request.stripe_invoice_url or ""

    # Get party name for display
    party_name = ""
    if payment_request.party_type == "Customer" and payment_request.party:
        party_name = frappe.db.get_value("Customer", payment_request.party, "customer_name") or payment_request.party
    elif payment_request.party:
        party_name = payment_request.party

    template_data = {
        "document_type": "Payment Request",
        "customer_name": party_name,
        "party_name": party_name,
        "payment_request_number": payment_request.name,
        "document_number": payment_request.name,
        "transaction_date": formatdate(payment_request.transaction_date) if payment_request.transaction_date else "",
        "document_date": formatdate(payment_request.transaction_date) if payment_request.transaction_date else "",
        "grand_total": format_currency_amount(payment_request.grand_total, payment_request.currency),
        "total_amount": format_currency_amount(payment_request.grand_total, payment_request.currency),
        "currency": payment_request.currency,
        "company_name": company_info["company_name"],
        "company_logo": company_info["company_logo"] or "",
        "company_address": company_info["company_address"] or "",
        "company_phone": company_info["phone"] or "",
        "company_email": company_info["email"] or "",
        "document_link": get_document_link("Payment Request", payment_request_name),
        "custom_message": custom_message or "",
        "subject": f"Payment Request {payment_request.name} from {company_info['company_name']}",

        # Stripe-specific field
        "stripe_invoice_url": stripe_invoice_url,
        "payment_url": stripe_invoice_url or payment_request.payment_url or "",

        # Reference document info
        "reference_doctype": payment_request.reference_doctype or "",
        "reference_name": payment_request.reference_name or "",

        # Payment gateway info
        "payment_gateway": payment_request.payment_gateway or "",
        "payment_gateway_account": payment_request.payment_gateway_account or "",

        # Message from payment request
        "message": payment_request.message or "",
    }

    # Attempt to get PDF
    attachments = None
    try:
        pdf_bytes, filename = get_document_pdf("Payment Request", payment_request_name)
        attachments = [{
            "filename": filename,
            "content": pdf_to_base64(pdf_bytes)
        }]
    except Exception as e:
        frappe.log_error(title="Payment Request PDF Generation Failed", message=str(e))

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
                {"name": "doctype", "value": "payment_request"},
                {"name": "document", "value": payment_request_name.replace("-", "_").replace(" ", "_")}
            ]
        )

        if not skip_communication:
            create_communication_log(
                doctype="Payment Request",
                docname=payment_request_name,
                recipient=to_email,
                subject=template_data["subject"],
                content=f"Payment Request email sent via Resend",
                status="Sent",
                message_id=result.get("message_id")
            )

        return {
            "success": True,
            "message": "Payment Request email sent successfully",
            "message_id": result.get("message_id"),
            "recipient": to_email
        }

    except ResendError as e:
        if not skip_communication:
            create_communication_log(
                doctype="Payment Request",
                docname=payment_request_name,
                recipient=to_email,
                subject=template_data["subject"],
                content=f"Payment Request email failed: {str(e)}",
                status="Error",
                error_msg=str(e)
            )

        if settings.fallback_to_erpnext:
            return _send_fallback_email(payment_request, to_email, template_data, attachments)

        raise


def _send_fallback_email(payment_request, to_email, template_data, attachments):
    """Send email using ERPNext's default email system as fallback."""
    try:
        payment_url = template_data.get("stripe_invoice_url") or template_data.get("payment_url", "")
        payment_link = f'<p><a href="{payment_url}">Click here to pay</a></p>' if payment_url else ""

        frappe.sendmail(
            recipients=[to_email],
            subject=template_data["subject"],
            message=f"""
                <p>Dear {template_data['customer_name']},</p>
                <p>Please find your payment request {template_data['payment_request_number']}.</p>
                <p>Amount Due: {template_data['total_amount']}</p>
                {payment_link}
                <p>Best regards,<br>{template_data['company_name']}</p>
            """,
            reference_doctype="Payment Request",
            reference_name=payment_request.name,
        )

        return {
            "success": True,
            "message": "Payment Request email sent via ERPNext fallback",
            "fallback": True,
            "recipient": to_email
        }

    except Exception as e:
        frappe.log_error(title="Fallback Email Failed", message=str(e))
        raise
