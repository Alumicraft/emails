from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Block ERPNext auto-send — user sends via the Send Email button/dialog."""
        if should_use_resend("Payment Request"):
            return
        return super().send_email()

    def make_communication_entry(self):
        """Block ERPNext auto communication — send_document_email creates its own."""
        if should_use_resend("Payment Request"):
            return
        super().make_communication_entry()
