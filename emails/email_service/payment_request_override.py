import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend


def on_payment_request_submit(doc, method):
    """doc_events on_submit handler — sends email after doc is saved to DB.

    This runs after save() in the submit flow, so docstatus=1 is in the DB
    and send_document_email can re-fetch the doc safely. No background worker
    dependency — the HTTP call to Vercel/Resend happens inline.
    """
    if not should_use_resend("Payment Request"):
        return

    # Respect ERPNext's mute_email flag
    if getattr(doc, "mute_email", False) or getattr(doc.flags, "mute_email", False):
        return

    # Only send for Inward payment requests (customer-facing invoices)
    if getattr(doc, "payment_request_type", None) != "Inward":
        return

    try:
        from emails.email_service.generic_email import send_document_email

        send_document_email(doctype=doc.doctype, docname=doc.name)
    except Exception:
        frappe.log_error(
            title=f"Payment Request Email Failed: {doc.name}",
            message=frappe.get_traceback(),
        )


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Block ERPNext native email — on_payment_request_submit handles it."""
        if should_use_resend("Payment Request"):
            return
        return super().send_email()

    def make_communication_entry(self):
        """Block ERPNext auto communication — send_document_email creates its own."""
        if should_use_resend("Payment Request"):
            return
        super().make_communication_entry()
