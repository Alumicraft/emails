# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Generic Email Handler - Sends emails for any doctype.

This module provides a universal email sending mechanism that works with any
doctype. It dynamically resolves recipients, builds template data from document
fields, and handles PDF generation.
"""

import re

import frappe
from frappe import _
from frappe.utils import formatdate, fmt_money, get_url

from emails.email_service.resend_client import send_template_email, ResendError
from emails.email_service.vercel_client import send_email as vercel_send_email, VercelEmailError
from emails.email_service.branding import get_company_branding
from emails.email_service.utils import (
    get_email_settings,
    get_company_info,
    get_customer_primary_email,
    get_supplier_primary_email,
    get_document_pdf,
    pdf_to_base64,
    create_communication_log,
    get_document_link,
    get_email_recipients_from_doc,
)
from emails.emails.doctype.email_service_settings.email_service_settings import DOCTYPE_REGISTRY

# Map ERPNext doctypes to Vercel react-email template names
DOCTYPE_TEMPLATE_MAP = {
    "Sales Invoice": "sales-invoice",
    "Quotation": "quotation",
    "Sales Order": "sales-order",
    "Purchase Order": "purchase-order",
    "Request for Quotation": "request-for-quotation",
    "Payment Request": "payment-request",
    "Payment Entry": "payment-entry",
}


def send_document_email(
    doctype,
    docname,
    to_email=None,
    cc=None,
    bcc=None,
    custom_message=None,
    skip_communication=False,
):
    """
    Generic email sender that works with any doctype.

    Args:
        doctype: The document type
        docname: The document name
        to_email: Override recipient email (optional)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        custom_message: Custom message to include (optional)
        skip_communication: Skip creating Communication log (optional)

    Returns:
        dict: Result with success status, message_id, and recipient
    """
    settings = get_email_settings()

    # Get the document
    doc = frappe.get_doc(doctype, docname)

    # Check submission status for submittable documents
    if hasattr(doc, "docstatus") and doc.docstatus != 1:
        frappe.throw(
            _("{0} {1} must be submitted before sending email").format(doctype, docname)
        )

    # Resolve recipient email
    if not to_email:
        to_email = resolve_recipient_email(doc)

    if not to_email:
        frappe.throw(
            _("No email address found for {0} {1}").format(doctype, docname)
        )

    # Get company info
    company_name = getattr(doc, "company", None) or frappe.defaults.get_global_default(
        "company"
    )
    company_info = get_company_info(company_name) if company_name else get_default_company_info()

    # Build template data dynamically
    template_data = build_template_data(doc, doctype, company_info, custom_message)

    # Use default subject
    subject = template_data["subject"]

    # Generate PDF attachment (skip for Payment Request — only attach reference doc)
    if doctype == "Payment Request":
        attachments = []
        # Attach reference document PDF (e.g., Sales Invoice)
        if getattr(doc, "reference_doctype", None) and getattr(doc, "reference_name", None):
            ref_attachments = generate_pdf_attachment(doc.reference_doctype, doc.reference_name)
            if ref_attachments:
                attachments.extend(ref_attachments)
        # Attach wire instructions PDF if enabled
        if getattr(settings, "attach_wire_instructions", 0) and getattr(settings, "wire_instructions_url", None):
            wire_attachment = fetch_url_pdf_attachment(settings.wire_instructions_url, "wire_instructions.pdf")
            if wire_attachment:
                attachments.append(wire_attachment)
    else:
        attachments = generate_pdf_attachment(doctype, docname)

    # Check if Vercel service is configured
    use_vercel = bool(getattr(settings, "vercel_service_url", None))

    if use_vercel:
        # Send via Vercel react-email service
        return _send_via_vercel(
            doctype=doctype,
            docname=docname,
            to_email=to_email,
            subject=subject,
            template_data=template_data,
            company_name=company_name,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            skip_communication=skip_communication,
            settings=settings,
        )
    else:
        # Fall back to direct Resend template
        return _send_via_resend(
            doctype=doctype,
            docname=docname,
            to_email=to_email,
            subject=subject,
            template_data=template_data,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            skip_communication=skip_communication,
            settings=settings,
            doc=doc,
        )


def _send_via_vercel(
    doctype,
    docname,
    to_email,
    subject,
    template_data,
    company_name,
    cc,
    bcc,
    attachments,
    skip_communication,
    settings,
):
    """Send email via Vercel react-email service with branding."""
    # Get branding
    branding = get_company_branding(company_name)

    # Determine template from DOCTYPE_TEMPLATE_MAP, fallback to generic "document"
    template = DOCTYPE_TEMPLATE_MAP.get(doctype, "document")

    try:
        result = vercel_send_email(
            template=template,
            to_email=to_email,
            subject=subject,
            data=template_data,
            branding=branding,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            tags=[
                {"name": "doctype", "value": frappe.scrub(doctype)},
                {"name": "document", "value": docname.replace("-", "_").replace(" ", "_")},
            ],
        )

        message_id = result.get("message_id")
        rendered_html = result.get("html", "")

        if not skip_communication:
            content = rendered_html or _build_email_preview(doctype, template_data, to_email)
            create_communication_log(
                doctype=doctype,
                docname=docname,
                recipient=to_email,
                subject=subject,
                content=content,
                status="Sent",
                message_id=message_id,
            )

        return {
            "success": True,
            "message": _("{0} email sent successfully").format(doctype),
            "message_id": message_id,
            "recipient": to_email,
        }

    except VercelEmailError as e:
        if not skip_communication:
            create_communication_log(
                doctype=doctype,
                docname=docname,
                recipient=to_email,
                subject=subject,
                content=_("{0} email failed: {1}").format(doctype, str(e)),
                status="Error",
                error_msg=str(e),
            )

        if settings.fallback_to_erpnext:
            return send_fallback_email(
                frappe.get_doc(doctype, docname),
                doctype,
                docname,
                to_email,
                template_data
            )

        raise


def _send_via_resend(
    doctype,
    docname,
    to_email,
    subject,
    template_data,
    cc,
    bcc,
    attachments,
    skip_communication,
    settings,
    doc,
):
    """Send email via direct Resend template (legacy fallback)."""
    try:
        result = send_template_email(
            template_id="",
            to_email=to_email,
            template_data=template_data,
            subject=subject,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            tags=[
                {"name": "doctype", "value": frappe.scrub(doctype)},
                {"name": "document", "value": docname.replace("-", "_").replace(" ", "_")},
            ],
        )

        message_id = result.get("message_id")

        if not skip_communication:
            preview = _build_email_preview(doctype, template_data, to_email)
            create_communication_log(
                doctype=doctype,
                docname=docname,
                recipient=to_email,
                subject=subject,
                content=preview,
                status="Sent",
                message_id=message_id,
            )

        return {
            "success": True,
            "message": _("{0} email sent successfully").format(doctype),
            "message_id": message_id,
            "recipient": to_email,
        }

    except ResendError as e:
        if not skip_communication:
            create_communication_log(
                doctype=doctype,
                docname=docname,
                recipient=to_email,
                subject=subject,
                content=_("{0} email failed: {1}").format(doctype, str(e)),
                status="Error",
                error_msg=str(e),
            )

        if settings.fallback_to_erpnext:
            return send_fallback_email(doc, doctype, docname, to_email, template_data)

        raise


def resolve_recipient_email(doc):
    """
    Resolve recipient email using DOCTYPE_REGISTRY defaults and fallback logic.

    Args:
        doc: The document

    Returns:
        str: Email address or None
    """
    doctype = doc.doctype

    # Check DOCTYPE_REGISTRY for recipient resolution defaults
    registry_info = DOCTYPE_REGISTRY.get(doctype)

    if registry_info:
        recipient_field = registry_info.get("recipient_field")
        recipient_doctype = registry_info.get("recipient_doctype")

        if recipient_field:
            party_name = getattr(doc, recipient_field, None)
            if party_name:
                # If the field value is already an email address, return it directly
                if "@" in str(party_name):
                    return party_name

                # Handle Payment Entry special case where party_type is dynamic
                if not recipient_doctype and hasattr(doc, "party_type"):
                    recipient_doctype = doc.party_type

                if recipient_doctype and party_name:
                    email = get_party_email(recipient_doctype, party_name)
                    if email:
                        return email

    # Fallback to legacy email resolution
    recipients = get_email_recipients_from_doc(doc)
    return recipients[0] if recipients else None


def resolve_field_path(doc, field_path):
    """
    Resolve a dot-notation field path to get a value.

    Args:
        doc: The document
        field_path: Dot-notation path like 'customer.email_id' or 'email_id'

    Returns:
        str: Field value or None
    """
    if not field_path:
        return None

    parts = field_path.split(".")

    if len(parts) == 1:
        # Direct field on document
        return getattr(doc, field_path, None)

    # Linked document field
    linked_field = parts[0]
    remaining_path = ".".join(parts[1:])

    linked_name = getattr(doc, linked_field, None)
    if not linked_name:
        return None

    # Try to determine the linked doctype
    try:
        meta = frappe.get_meta(doc.doctype)
        field_meta = meta.get_field(linked_field)
        if field_meta and field_meta.fieldtype == "Link":
            linked_doctype = field_meta.options
            linked_doc = frappe.get_doc(linked_doctype, linked_name)
            return resolve_field_path(linked_doc, remaining_path)
    except Exception:
        pass

    return None


def get_party_email(doctype, party_name):
    """
    Get email for a party (Customer, Supplier, or any other doctype).

    Args:
        doctype: The party doctype (e.g., 'Customer', 'Supplier')
        party_name: The party name

    Returns:
        str: Email address or None
    """
    if doctype == "Customer":
        return get_customer_primary_email(party_name)
    elif doctype == "Supplier":
        return get_supplier_primary_email(party_name)
    else:
        # Generic lookup for other party types
        return get_generic_party_email(doctype, party_name)


def get_generic_party_email(doctype, party_name):
    """
    Get email for any party type by checking common email fields and Contact links.

    Args:
        doctype: The party doctype
        party_name: The party name

    Returns:
        str: Email address or None
    """
    try:
        party = frappe.get_doc(doctype, party_name)

        # Try common email field names
        for field in ["email_id", "email", "contact_email", "primary_email", "email_address"]:
            email = getattr(party, field, None)
            if email:
                return email

        # Try to find via Contact link
        contact_name = frappe.db.get_value(
            "Dynamic Link",
            {"link_doctype": doctype, "link_name": party_name, "parenttype": "Contact"},
            "parent",
        )

        if contact_name:
            contact = frappe.get_doc("Contact", contact_name)
            if contact.email_id:
                return contact.email_id

            # Check email_ids child table
            if contact.email_ids:
                for email_row in contact.email_ids:
                    if email_row.is_primary:
                        return email_row.email_id
                return contact.email_ids[0].email_id

    except Exception:
        pass

    return None


def _build_email_preview(doctype, template_data, to_email):
    """Build an HTML preview of the email for the Communication content field."""
    customer = template_data.get("customer_name") or template_data.get("party_name") or ""
    doc_number = template_data.get("document_number", "")
    total = template_data.get("total_amount", "")
    date = template_data.get("document_date", "")

    rows = []
    if doc_number:
        rows.append(f"<b>{doctype}:</b> {doc_number}")
    if total:
        rows.append(f"<b>Amount:</b> {total}")
    if date:
        rows.append(f"<b>Date:</b> {date}")

    details = "<br>".join(rows)

    greeting = f"Dear {customer}," if customer else ""

    return f"""<div>
<p>{greeting}</p>
<p>Please find attached your {doctype.lower()}.</p>
{f'<p>{details}</p>' if details else ''}
<p style="color: #999; font-size: 12px;">Sent to {to_email}</p>
</div>"""


def _strip_empty_html(value):
    """Strip HTML that renders as empty/blank (e.g. Quill editor wrappers)."""
    if not value or "<" not in value:
        return value
    # Remove all HTML tags and check if anything visible remains
    stripped = re.sub(r"<[^>]+>", "", value).strip()
    if not stripped:
        return ""
    return value


def build_template_data(doc, doctype, company_info, custom_message=None):
    """
    Build template data dictionary from document fields.

    Args:
        doc: The document
        doctype: The document type
        company_info: Company information dict
        custom_message: Custom message to include

    Returns:
        dict: Template data for Resend
    """
    # Get currency
    currency = getattr(doc, "currency", None) or frappe.defaults.get_global_default(
        "currency"
    ) or "USD"

    # Common base data
    data = {
        "document_type": doctype,
        "document_number": doc.name,
        "document_name": doc.name,
        "company_name": company_info.get("company_name", ""),
        "company_logo": company_info.get("company_logo", ""),
        "company_address": company_info.get("company_address", ""),
        "company_phone": company_info.get("phone", ""),
        "company_email": company_info.get("email", ""),
        "document_link": get_document_link(doctype, doc.name),
        "custom_message": custom_message or "",
        "currency": currency,
    }

    # Extract document date
    data["document_date"] = extract_date_field(doc)

    # Extract total amount
    data["total_amount"] = extract_amount_field(doc, currency)

    # Extract party/customer name
    data["customer_name"] = extract_party_name(doc)
    data["party_name"] = data["customer_name"]

    # Build default subject
    if doctype == "Payment Request" and hasattr(doc, "reference_name") and doc.reference_name:
        # Use reference document number for Payment Request subject
        data["subject"] = _("Invoice {0} from {1}").format(
            doc.reference_name, company_info.get("company_name", "Company")
        )
    elif doctype == "Payment Entry":
        data["subject"] = _("Payment Receipt {0} from {1}").format(
            doc.name, company_info.get("company_name", "Company")
        )
    else:
        data["subject"] = _("{0} {1} from {2}").format(
            doctype, doc.name, company_info.get("company_name", "Company")
        )

    # Include all standard document fields for template flexibility
    meta = frappe.get_meta(doctype)
    for field in meta.fields:
        field_value = getattr(doc, field.fieldname, None)
        if field_value is not None and field.fieldtype in [
            "Data",
            "Link",
            "Select",
            "Int",
            "Float",
            "Currency",
            "Date",
            "Datetime",
            "Small Text",
            "Text",
            "Long Text",
        ]:
            # Format dates
            if field.fieldtype in ["Date", "Datetime"] and field_value:
                data[field.fieldname] = formatdate(field_value)
            # Format currency
            elif field.fieldtype == "Currency" and field_value:
                data[field.fieldname] = fmt_money(field_value, currency=currency)
            else:
                value = str(field_value) if field_value else ""
                # Strip empty Quill editor HTML that adds no visible content
                value = _strip_empty_html(value)
                data[field.fieldname] = value

    # Extract items if present (for invoice-like documents)
    data["items"] = extract_items_summary(doc, currency)
    data["items_count"] = len(doc.items) if hasattr(doc, "items") else 0

    # Special handling for Payment Request - use reference document as reference_number
    if doctype == "Payment Request":
        if hasattr(doc, "reference_name") and doc.reference_name:
            data["reference_number"] = doc.reference_name
        # Pull due_date and project from the reference document
        if hasattr(doc, "reference_doctype") and hasattr(doc, "reference_name"):
            if doc.reference_doctype and doc.reference_name:
                try:
                    ref_doc = frappe.get_doc(doc.reference_doctype, doc.reference_name)
                    for date_field in ("due_date", "transaction_date"):
                        if getattr(ref_doc, date_field, None):
                            data["due_date"] = formatdate(ref_doc.get(date_field))
                            break
                    if hasattr(ref_doc, "project") and ref_doc.project:
                        data["project_name"] = ref_doc.project
                except Exception:
                    pass

    # Per-doctype prop mapping: map ERPNext field names to React template prop names
    if doctype == "Payment Request":
        data["amount_requested"] = data.get("total_amount", "")
        data["stripe_payment_url"] = getattr(doc, "stripe_invoice_url", "") or getattr(doc, "payment_url", "") or ""
    elif doctype == "Sales Invoice":
        data["invoice_number"] = doc.name
        data["invoice_date"] = formatdate(getattr(doc, "posting_date", "")) if getattr(doc, "posting_date", None) else ""
        data["due_date"] = formatdate(getattr(doc, "due_date", "")) if getattr(doc, "due_date", None) else ""
        data["amount_due"] = data.get("total_amount", "")
    elif doctype == "Quotation":
        data["quotation_number"] = doc.name
        data["quotation_date"] = formatdate(getattr(doc, "transaction_date", "")) if getattr(doc, "transaction_date", None) else ""
        data["valid_until"] = formatdate(getattr(doc, "valid_till", "")) if getattr(doc, "valid_till", None) else ""
    elif doctype == "Sales Order":
        data["order_number"] = doc.name
        data["order_date"] = formatdate(getattr(doc, "transaction_date", "")) if getattr(doc, "transaction_date", None) else ""
        data["order_total"] = data.get("total_amount", "")
    elif doctype == "Purchase Order":
        data["po_number"] = doc.name
        data["po_date"] = formatdate(getattr(doc, "transaction_date", "")) if getattr(doc, "transaction_date", None) else ""
    elif doctype == "Request for Quotation":
        data["rfq_number"] = doc.name
        data["rfq_date"] = formatdate(getattr(doc, "transaction_date", "")) if getattr(doc, "transaction_date", None) else ""
    elif doctype == "Payment Entry":
        pe_currency = getattr(doc, "paid_from_account_currency", None) or currency
        data["receipt_number"] = doc.name
        data["payment_date"] = formatdate(getattr(doc, "posting_date", "")) if getattr(doc, "posting_date", None) else ""
        data["paid_amount"] = fmt_money(getattr(doc, "paid_amount", 0), currency=pe_currency)
        data["mode_of_payment"] = getattr(doc, "mode_of_payment", "") or ""
        data["reference_no"] = getattr(doc, "reference_no", "") or ""
        # Comma-joined invoice/reference names from the references child table
        if hasattr(doc, "references") and doc.references:
            data["applied_to"] = ", ".join(
                ref.reference_name for ref in doc.references if ref.reference_name
            )

    return data


def extract_date_field(doc):
    """Extract document date from common date fields."""
    for date_field in [
        "posting_date",
        "transaction_date",
        "application_date",
        "repayment_date",
        "creation",
    ]:
        if hasattr(doc, date_field) and getattr(doc, date_field):
            return formatdate(getattr(doc, date_field))
    return ""


def extract_amount_field(doc, currency):
    """Extract total amount from common amount fields."""
    for amount_field in [
        "grand_total",
        "total",
        "loan_amount",
        "total_payment",
        "outstanding_amount",
        "paid_amount",
        "total_amount",
    ]:
        if hasattr(doc, amount_field):
            amount = getattr(doc, amount_field)
            if amount:
                return fmt_money(amount, currency=currency)
    return ""


def extract_party_name(doc):
    """Extract party/customer name from common fields."""
    for party_field in [
        "customer_name",
        "party_name",
        "applicant_name",
        "borrower_name",
        "supplier_name",
        "title",
    ]:
        if hasattr(doc, party_field) and getattr(doc, party_field):
            return getattr(doc, party_field)
    return ""


def extract_items_summary(doc, currency, max_items=5):
    """Extract items summary for documents with items table."""
    items_summary = []

    if not hasattr(doc, "items"):
        return items_summary

    for item in doc.items[:max_items]:
        item_data = {
            "item_name": getattr(item, "item_name", "") or getattr(item, "description", ""),
            "qty": getattr(item, "qty", 0),
        }

        if hasattr(item, "rate"):
            item_data["rate"] = fmt_money(item.rate, currency=currency)
        if hasattr(item, "amount"):
            item_data["amount"] = fmt_money(item.amount, currency=currency)

        items_summary.append(item_data)

    return items_summary


def render_subject_template(template, doc, company_info):
    """Render subject line from Jinja template."""
    try:
        from jinja2 import Template

        t = Template(template)
        return t.render(doc=doc, company=company_info.get("company_name", ""))
    except Exception:
        return _("{0} {1}").format(doc.doctype, doc.name)


def generate_pdf_attachment(doctype, docname, print_format=None):
    """Generate PDF attachment for document."""
    try:
        pdf_bytes, filename = get_document_pdf(doctype, docname, print_format)
        return [{"filename": filename, "content": pdf_to_base64(pdf_bytes)}]
    except Exception as e:
        frappe.log_error(
            title=_("{0} PDF Generation Failed").format(doctype), message=str(e)
        )
        return None


def fetch_url_pdf_attachment(url, filename="attachment.pdf"):
    """Fetch a PDF from a public URL and return as an attachment dict."""
    try:
        import requests
        import base64

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content_b64 = base64.b64encode(response.content).decode("utf-8")
        return {"filename": filename, "content": content_b64}
    except Exception as e:
        frappe.log_error(title="Wire Instructions PDF Fetch Failed", message=str(e))
        return None


def send_fallback_email(doc, doctype, docname, to_email, template_data):
    """Send email using ERPNext's default email system as fallback."""
    try:
        frappe.sendmail(
            recipients=[to_email],
            subject=template_data.get("subject", _("{0} from ERPNext").format(doctype)),
            message=_(
                """
                <p>Dear {customer_name},</p>
                <p>Please find attached your {document_type}.</p>
                <p>Total Amount: {total_amount}</p>
                <p>Best regards,<br>{company_name}</p>
            """
            ).format(
                customer_name=template_data.get("customer_name", _("Customer")),
                document_type=doctype.lower(),
                total_amount=template_data.get("total_amount", "N/A"),
                company_name=template_data.get("company_name", _("Company")),
            ),
            reference_doctype=doctype,
            reference_name=docname,
        )

        return {
            "success": True,
            "message": _("{0} email sent via ERPNext fallback").format(doctype),
            "fallback": True,
            "recipient": to_email,
        }

    except Exception as e:
        frappe.log_error(title=_("Fallback Email Failed"), message=str(e))
        raise


def get_default_company_info():
    """Get default company info when no company is specified on document."""
    default_company = frappe.defaults.get_global_default("company")
    if default_company:
        return get_company_info(default_company)

    return {
        "company_name": "",
        "company_logo": "",
        "company_address": "",
        "phone": "",
        "email": "",
        "website": "",
        "tax_id": "",
    }
