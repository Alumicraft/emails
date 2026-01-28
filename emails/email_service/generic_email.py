# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Generic Email Handler - Sends emails for any configured doctype.

This module provides a universal email sending mechanism that works with any
doctype configured in Email Service Settings. It dynamically resolves recipients,
builds template data from document fields, and handles PDF generation.
"""

import frappe
from frappe import _
from frappe.utils import formatdate, fmt_money, get_url

from emails.email_service.resend_client import send_template_email, ResendError
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
    Generic email sender that works with any configured doctype.

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
    config = settings.get_doctype_config(doctype)

    # Get the document
    doc = frappe.get_doc(doctype, docname)

    # Check submission status if required
    if config and config.require_submit:
        if doc.docstatus != 1:
            frappe.throw(
                _("{0} {1} must be submitted before sending email").format(doctype, docname)
            )
    elif not config:
        # Legacy fallback - require submission for known doctypes
        if hasattr(doc, "docstatus") and doc.docstatus != 1:
            frappe.throw(
                _("{0} {1} must be submitted before sending email").format(doctype, docname)
            )

    # Resolve recipient email
    if not to_email:
        to_email = resolve_recipient_email(doc, config)

    if not to_email:
        frappe.throw(
            _("No email address found for {0} {1}").format(doctype, docname)
        )

    # Get company info
    company_name = getattr(doc, "company", None) or frappe.defaults.get_global_default(
        "company"
    )
    company_info = get_company_info(company_name) if company_name else get_default_company_info()

    # Get template ID
    template_id = settings.get_template_id(doctype) or ""

    # Build template data dynamically
    template_data = build_template_data(doc, doctype, company_info, config, custom_message)

    # Generate subject from template or default
    subject = template_data["subject"]
    if config and config.subject_template:
        subject = render_subject_template(config.subject_template, doc, company_info)
        template_data["subject"] = subject

    # Generate PDF attachment
    print_format = config.print_format if config else None
    attachments = generate_pdf_attachment(doctype, docname, print_format)

    # Send email
    try:
        result = send_template_email(
            template_id=template_id,
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

        if not skip_communication:
            create_communication_log(
                doctype=doctype,
                docname=docname,
                recipient=to_email,
                subject=subject,
                content=_("{0} email sent via Resend").format(doctype),
                status="Sent",
                message_id=result.get("message_id"),
            )

        return {
            "success": True,
            "message": _("{0} email sent successfully").format(doctype),
            "message_id": result.get("message_id"),
            "recipient": to_email,
        }

    except ResendError as e:
        if not skip_communication:
            create_communication_log(
                doctype=doctype,
                docname=docname,
                recipient=to_email,
                subject=subject,
                content=_("{0} email failed").format(doctype),
                status="Error",
                error_msg=str(e),
            )

        if settings.fallback_to_erpnext:
            return send_fallback_email(doc, doctype, docname, to_email, template_data)

        raise


def resolve_recipient_email(doc, config):
    """
    Resolve recipient email based on configuration.

    Args:
        doc: The document
        config: Email Doctype Configuration row (or None)

    Returns:
        str: Email address or None
    """
    # Try direct email field path first (if configured)
    if config and config.email_field_path:
        email = resolve_field_path(doc, config.email_field_path)
        if email:
            return email

    # Try recipient field + doctype lookup
    if config and config.recipient_field:
        party_name = getattr(doc, config.recipient_field, None)
        if party_name:
            recipient_doctype = config.recipient_doctype

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


def build_template_data(doc, doctype, company_info, config, custom_message=None):
    """
    Build template data dictionary from document fields.

    Args:
        doc: The document
        doctype: The document type
        company_info: Company information dict
        config: Email Doctype Configuration row (or None)
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
                data[field.fieldname] = str(field_value) if field_value else ""

    # Extract items if present (for invoice-like documents)
    data["items"] = extract_items_summary(doc, currency)
    data["items_count"] = len(doc.items) if hasattr(doc, "items") else 0

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
