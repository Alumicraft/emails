import base64
import frappe
from frappe.utils import get_url, formatdate, fmt_money


def get_email_settings():
    """Get Email Service Settings document."""
    settings = frappe.get_single("Email Service Settings")

    if not settings.enabled:
        frappe.throw("Email Service is not enabled. Please enable it in Email Service Settings.")

    if not settings.get_password("resend_api_key"):
        frappe.throw("Resend API Key not configured in Email Service Settings.")

    return settings


def get_company_info(company_name):
    """Get company information for email templates."""
    company = frappe.get_doc("Company", company_name)

    logo_url = None
    if company.company_logo:
        logo_url = get_absolute_url(company.company_logo)

    address = get_company_address(company_name)

    return {
        "company_name": company.company_name,
        "company_logo": logo_url,
        "company_address": address,
        "phone": company.phone_no,
        "email": company.email,
        "website": company.website,
        "tax_id": company.tax_id,
    }


def get_company_address(company_name):
    """Get formatted company address."""
    address_name = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Company", "link_name": company_name, "parenttype": "Address"},
        "parent"
    )

    if not address_name:
        return ""

    address = frappe.get_doc("Address", address_name)
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

    return "\n".join(parts)


def get_customer_primary_email(customer_name):
    """Get primary email address for a customer."""
    customer = frappe.get_doc("Customer", customer_name)

    if customer.email_id:
        return customer.email_id

    contact_name = frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": "Customer",
            "link_name": customer_name,
            "parenttype": "Contact"
        },
        "parent"
    )

    if contact_name:
        contact = frappe.get_doc("Contact", contact_name)
        if contact.email_id:
            return contact.email_id

        if contact.email_ids:
            for email in contact.email_ids:
                if email.is_primary:
                    return email.email_id
            return contact.email_ids[0].email_id

    return None


def get_supplier_primary_email(supplier_name):
    """Get primary email address for a supplier."""
    supplier = frappe.get_doc("Supplier", supplier_name)

    if supplier.email_id:
        return supplier.email_id

    contact_name = frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": "Supplier",
            "link_name": supplier_name,
            "parenttype": "Contact"
        },
        "parent"
    )

    if contact_name:
        contact = frappe.get_doc("Contact", contact_name)
        if contact.email_id:
            return contact.email_id

    return None


def format_currency_amount(amount, currency="USD"):
    """Format currency amount with proper symbol and decimals."""
    return fmt_money(amount, currency=currency)


def format_date(date, format_string=None):
    """Format date for display in emails."""
    if not date:
        return ""
    return formatdate(date, format_string)


def get_document_link(doctype, docname):
    """Get full URL to document in ERPNext."""
    return f"{get_url()}/app/{frappe.scrub(doctype)}/{docname}"


def get_absolute_url(relative_url):
    """Convert relative URL to absolute URL."""
    if not relative_url:
        return None

    if relative_url.startswith(("http://", "https://")):
        return relative_url

    base_url = get_url()
    if relative_url.startswith("/"):
        return f"{base_url}{relative_url}"
    return f"{base_url}/{relative_url}"


def pdf_to_base64(pdf_bytes):
    """Convert PDF bytes to base64 string."""
    return base64.b64encode(pdf_bytes).decode("utf-8")


def get_document_pdf(doctype, docname, print_format=None):
    """Generate PDF for a document."""
    pdf_bytes = frappe.get_print(
        doctype,
        docname,
        print_format=print_format,
        as_pdf=True
    )

    filename = f"{frappe.scrub(doctype)}_{docname}.pdf".replace(" ", "_")

    return pdf_bytes, filename


def create_communication_log(
    doctype,
    docname,
    recipient,
    subject,
    content,
    status="Sent",
    message_id=None,
    error_msg=None,
    sender=None
):
    """Create Communication document to log email."""
    settings = frappe.get_single("Email Service Settings")

    comm = frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "sent_or_received": "Sent",
        "subject": subject,
        "content": content,
        "sender": sender or settings.default_sender_email,
        "recipients": recipient,
        "reference_doctype": doctype,
        "reference_name": docname,
        "status": "Linked" if status == "Sent" else "Open",
        "email_status": "Open",
    })

    if message_id:
        comm.message_id = message_id

    if error_msg and status != "Sent":
        comm.add_comment("Comment", f"Email send failed: {error_msg}")

    comm.insert(ignore_permissions=True)
    frappe.db.commit()

    return comm


def get_print_format_for_doctype(doctype):
    """Get default print format for a doctype."""
    default_format = frappe.db.get_value(
        "Property Setter",
        {
            "doc_type": doctype,
            "property": "default_print_format"
        },
        "value"
    )

    if default_format:
        return default_format

    print_format = frappe.db.get_value(
        "Print Format",
        {"doc_type": doctype, "disabled": 0},
        "name"
    )

    return print_format


def get_email_recipients_from_doc(doc):
    """Extract email recipients from a document."""
    recipients = []

    if hasattr(doc, "email_id") and doc.email_id:
        recipients.append(doc.email_id)

    if hasattr(doc, "contact_email") and doc.contact_email:
        recipients.append(doc.contact_email)

    if hasattr(doc, "customer") and doc.customer:
        email = get_customer_primary_email(doc.customer)
        if email:
            recipients.append(email)

    if hasattr(doc, "supplier") and doc.supplier:
        email = get_supplier_primary_email(doc.supplier)
        if email:
            recipients.append(email)

    seen = set()
    unique_recipients = []
    for email in recipients:
        if email and email not in seen:
            seen.add(email)
            unique_recipients.append(email)

    return unique_recipients


def should_use_resend(doctype):
    """Check if Resend should be used for a given doctype."""
    try:
        settings = frappe.get_single("Email Service Settings")

        if not settings.enabled:
            return False

        # Check if API key is configured
        if not settings.get_password("resend_api_key"):
            return False

        # Check if this is a supported doctype
        supported_doctypes = [
            "Sales Invoice",
            "Quotation",
            "Sales Order",
            "Payment Entry",
            "Purchase Order",
            "Payment Request",
        ]
        return doctype in supported_doctypes

    except Exception:
        return False
