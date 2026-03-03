import frappe
from erpnext.accounts.doctype.payment_request.payment_request import PaymentRequest

from emails.email_service.utils import should_use_resend

logger = frappe.logger("emails")


class CustomPaymentRequest(PaymentRequest):
    def send_email(self):
        """Block ERPNext native email; route through Resend instead.

        Called in two contexts:
        1. before_submit — doc not yet saved (docstatus != 1 in DB).
           Return silently; on_submit will handle sending.
        2. Manual resend (ERPNext's "Resend Payment Email" button) — doc IS
           submitted in DB. Route through send_document_email as safety net.
        """
        if not should_use_resend("Payment Request"):
            logger.info(f"[PaymentRequest] send_email: Resend not enabled, falling through to native for {self.name}")
            return super().send_email()

        # Check if the doc is already submitted in the database
        db_docstatus = frappe.db.get_value("Payment Request", self.name, "docstatus")

        if db_docstatus != 1:
            # We're inside before_submit — doc hasn't been saved yet.
            # on_submit will fire after save and handle the email.
            logger.info(f"[PaymentRequest] send_email: skipped — not yet submitted in DB (docstatus={db_docstatus}) for {self.name}")
            return

        # Doc is submitted in DB — this is a manual resend (e.g. ERPNext button leaked through JS)
        logger.info(f"[PaymentRequest] send_email: routing manual resend to Resend for {self.name}")
        try:
            from emails.email_service.generic_email import send_document_email

            send_document_email(doctype=self.doctype, docname=self.name)
        except Exception:
            frappe.log_error(
                title=f"Payment Request Email Failed (manual resend): {self.name}",
                message=frappe.get_traceback(),
            )

    def on_submit(self):
        """Handle auto-send on submit via Resend.

        Called after the doc is saved with docstatus=1 in the DB.
        """
        # Let ERPNext do its thing first (update payment status on reference doc, etc.)
        super().on_submit()

        if not should_use_resend("Payment Request"):
            # Native email already handled by send_email() fallback above
            logger.info(f"[PaymentRequest] on_submit: Resend not enabled, skipping for {self.name}")
            return

        # Respect ERPNext's mute_email flag
        if getattr(self, "mute_email", False) or getattr(self.flags, "mute_email", False):
            logger.info(f"[PaymentRequest] on_submit: skipped — mute_email is True for {self.name}")
            return

        # Only send for Inward payment requests (customer-facing invoices)
        if getattr(self, "payment_request_type", None) != "Inward":
            logger.info(f"[PaymentRequest] on_submit: skipped — payment_request_type is '{getattr(self, 'payment_request_type', None)}' for {self.name}")
            return

        logger.info(f"[PaymentRequest] on_submit: sending email for {self.name}")
        try:
            from emails.email_service.generic_email import send_document_email

            send_document_email(doctype=self.doctype, docname=self.name)
            logger.info(f"[PaymentRequest] on_submit: email sent successfully for {self.name}")
        except Exception:
            frappe.log_error(
                title=f"Payment Request Email Failed: {self.name}",
                message=frappe.get_traceback(),
            )
            logger.info(f"[PaymentRequest] on_submit: email failed for {self.name}, see Error Log")

    def make_communication_entry(self):
        """Block ERPNext auto communication — send_document_email creates its own."""
        if should_use_resend("Payment Request"):
            logger.info(f"[PaymentRequest] make_communication_entry: blocked for {self.name}, Resend handles this")
            return
        super().make_communication_entry()
