import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend


def send_payment_request_email(doctype, docname):
    """Background job target — runs after the submit transaction commits."""
    try:
        from emails.email_service.generic_email import send_document_email

        send_document_email(doctype=doctype, docname=docname)
    except Exception:
        frappe.log_error(
            title=f"Payment Request Email Failed: {docname}",
            message=frappe.get_traceback(),
        )


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Route through Resend pipeline instead of ERPNext native email."""
        if not should_use_resend("Payment Request"):
            return super().send_email()

        frappe.enqueue(
            "emails.email_service.payment_request_override.send_payment_request_email",
            doctype=self.doctype,
            docname=self.name,
            enqueue_after_commit=True,
        )

    def make_communication_entry(self):
        """Block ERPNext auto communication — send_document_email creates its own."""
        if should_use_resend("Payment Request"):
            return
        super().make_communication_entry()
