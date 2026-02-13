import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Send Payment Request email via Resend instead of frappe.sendmail."""
        if not should_use_resend("Payment Request"):
            return super().send_email()

        from emails.email_service.generic_email import send_document_email

        try:
            result = send_document_email(
                doctype="Payment Request",
                docname=self.name,
                to_email=self.email_to,
            )
            if not result or not result.get("success"):
                frappe.log_error(
                    title="Resend Payment Email Failed",
                    message=str(result),
                )
                return super().send_email()
        except Exception:
            frappe.log_error(
                title="Resend Payment Email Error",
                message=frappe.get_traceback(),
            )
            return super().send_email()

    def make_communication_entry(self):
        """Skip when Resend handles it — send_document_email already creates a Communication log."""
        if should_use_resend("Payment Request"):
            return
        super().make_communication_entry()
