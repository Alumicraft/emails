import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend

logger = frappe.logger("emails")


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Block ERPNext native email; the post-submit dialog handles sending."""
        if not should_use_resend("Payment Request"):
            return super().send_email()
        logger.info(f"[PaymentRequest] send_email: blocked — user will send via post-submit dialog for {self.name}")

    def make_communication_entry(self):
        """Block ERPNext auto communication — send_document_email creates its own."""
        if should_use_resend("Payment Request"):
            logger.info(f"[PaymentRequest] make_communication_entry: blocked for {self.name}, Resend handles this")
            return
        super().make_communication_entry()
