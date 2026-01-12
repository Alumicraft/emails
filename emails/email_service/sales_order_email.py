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


def send_sales_order_email(sales_order_name, to_email=None, cc=None, bcc=None, custom_message=None, skip_communication=False):
    """Send Sales Order confirmation email via Resend."""
    settings = get_email_settings()

    sales_order = frappe.get_doc("Sales Order", sales_order_name)

    if sales_order.docstatus != 1:
        frappe.throw(f"Sales Order {sales_order_name} must be submitted before sending email")

    if not to_email:
        to_email = get_customer_primary_email(sales_order.customer)

    if not to_email:
        frappe.throw(f"No email address found for customer {sales_order.customer}")

    company_info = get_company_info(sales_order.company)

    template_id = settings.sales_order_template_id or ""

    template_data = {
        "document_type": "Sales Order",
        "customer_name": sales_order.customer_name or sales_order.customer,
        "sales_order_number": sales_order.name,
        "document_number": sales_order.name,
        "order_date": formatdate(sales_order.transaction_date),
        "document_date": formatdate(sales_order.transaction_date),
        "delivery_date": formatdate(sales_order.delivery_date) if sales_order.delivery_date else "",
        "total_amount": format_currency_amount(sales_order.grand_total, sales_order.currency),
        "currency": sales_order.currency,
        "company_name": company_info["company_name"],
        "company_logo": company_info["company_logo"] or "",
        "company_address": company_info["company_address"] or "",
        "company_phone": company_info["phone"] or "",
        "company_email": company_info["email"] or "",
        "document_link": get_document_link("Sales Order", sales_order_name),
        "custom_message": custom_message or "",
        "subject": f"Order Confirmation {sales_order.name} - {company_info['company_name']}",
        "po_no": sales_order.po_no or "",
    }

    if sales_order.shipping_address_name:
        shipping_address = frappe.get_doc("Address", sales_order.shipping_address_name)
        template_data["shipping_address"] = get_formatted_address(shipping_address)
    else:
        template_data["shipping_address"] = ""

    items_summary = []
    for item in sales_order.items[:5]:
        items_summary.append({
            "item_name": item.item_name,
            "qty": item.qty,
            "rate": format_currency_amount(item.rate, sales_order.currency),
            "amount": format_currency_amount(item.amount, sales_order.currency),
        })
    template_data["items"] = items_summary
    template_data["items_count"] = len(sales_order.items)

    try:
        pdf_bytes, filename = get_document_pdf("Sales Order", sales_order_name)
        attachments = [{
            "filename": filename,
            "content": pdf_to_base64(pdf_bytes)
        }]
    except Exception as e:
        frappe.log_error(title="Sales Order PDF Generation Failed", message=str(e))
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
                {"name": "doctype", "value": "sales_order"},
                {"name": "document", "value": sales_order_name.replace("-", "_").replace(" ", "_")}
            ]
        )

        if not skip_communication:
            create_communication_log(
                doctype="Sales Order",
                docname=sales_order_name,
                recipient=to_email,
                subject=template_data["subject"],
                content=f"Sales Order confirmation email sent via Resend",
                status="Sent",
                message_id=result.get("message_id")
            )

        return {
            "success": True,
            "message": "Sales Order email sent successfully",
            "message_id": result.get("message_id"),
            "recipient": to_email
        }

    except ResendError as e:
        if not skip_communication:
            create_communication_log(
                doctype="Sales Order",
                docname=sales_order_name,
                recipient=to_email,
                subject=template_data["subject"],
                content=f"Sales Order email failed",
                status="Error",
                error_msg=str(e)
            )

        if settings.fallback_to_erpnext:
            return _send_fallback_email(sales_order, to_email, template_data, attachments)

        raise


def get_formatted_address(address):
    """Format address for display."""
    parts = []
    if address.address_line1:
        parts.append(address.address_line1)
    if address.address_line2:
        parts.append(address.address_line2)
    if address.city:
        city_part = address.city
        if address.state:
            city_part += f", {address.state}"
        if address.pincode:
            city_part += f" {address.pincode}"
        parts.append(city_part)
    if address.country:
        parts.append(address.country)
    return ", ".join(parts)


def _send_fallback_email(sales_order, to_email, template_data, attachments):
    """Send email using ERPNext's default email system as fallback."""
    try:
        frappe.sendmail(
            recipients=[to_email],
            subject=template_data["subject"],
            message=f"""
                <p>Dear {template_data['customer_name']},</p>
                <p>Thank you for your order! Please find attached your order confirmation {template_data['sales_order_number']}.</p>
                <p>Total Amount: {template_data['total_amount']}</p>
                <p>Expected Delivery: {template_data['delivery_date']}</p>
                <p>Best regards,<br>{template_data['company_name']}</p>
            """,
            reference_doctype="Sales Order",
            reference_name=sales_order.name,
        )

        return {
            "success": True,
            "message": "Sales Order email sent via ERPNext fallback",
            "fallback": True,
            "recipient": to_email
        }

    except Exception as e:
        frappe.log_error(title="Fallback Email Failed", message=str(e))
        raise
