import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Auto-send via Resend on submit instead of ERPNext's standard email."""
        if should_use_resend("Payment Request"):
            try:
                from emails.email_service.generic_email import send_document_email
                send_document_email("Payment Request", self.name)
            except Exception:
                frappe.log_error(
                    title="Payment Request Auto-Send Failed",
                    message=frappe.get_traceback()
                )
            return
        return super().send_email()

    def make_communication_entry(self):
        """Skip — send_document_email creates its own Communication log."""
        if should_use_resend("Payment Request"):
            return
        super().make_communication_entry()
