from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Skip auto-send on submit — user sends manually via the Send Email button."""
        if should_use_resend("Payment Request"):
            return
        return super().send_email()

    def make_communication_entry(self):
        """Skip auto communication entry — send_document_email creates it when the user sends."""
        if should_use_resend("Payment Request"):
            return
        super().make_communication_entry()
