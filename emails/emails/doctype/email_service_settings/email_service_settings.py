import frappe
from frappe.model.document import Document


class EmailServiceSettings(Document):
    def validate(self):
        if self.enabled:
            if not self.resend_api_key:
                frappe.throw("Resend API Key is required when service is enabled")
            if not self.default_sender_email:
                frappe.throw("Default Sender Email is required when service is enabled")

            # Validate API key format
            api_key = self.get_password("resend_api_key")
            if api_key and not api_key.startswith("re_"):
                frappe.throw("Invalid Resend API Key format. Key should start with 're_'")

    def get_template_id(self, doctype):
        """Get template ID for a given doctype"""
        template_map = {
            "Sales Invoice": self.invoice_template_id,
            "Quotation": self.quotation_template_id,
            "Sales Order": self.sales_order_template_id,
            "Payment Entry": self.receipt_template_id,
            "Purchase Order": self.purchase_order_template_id,
            "Payment Request": self.payment_request_template_id,
        }
        return template_map.get(doctype)

    def get_sender(self):
        """Get formatted sender string"""
        if self.default_sender_name:
            return f"{self.default_sender_name} <{self.default_sender_email}>"
        return self.default_sender_email
