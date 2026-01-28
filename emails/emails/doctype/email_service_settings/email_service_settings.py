# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


# Registry of known doctypes and their source apps with default configurations
DOCTYPE_REGISTRY = {
    # ERPNext Selling
    "Sales Invoice": {
        "app": "erpnext",
        "category": "Selling",
        "recipient_field": "customer",
        "recipient_doctype": "Customer",
    },
    "Quotation": {
        "app": "erpnext",
        "category": "Selling",
        "recipient_field": "party_name",
        "recipient_doctype": "Customer",
    },
    "Sales Order": {
        "app": "erpnext",
        "category": "Selling",
        "recipient_field": "customer",
        "recipient_doctype": "Customer",
    },
    "Delivery Note": {
        "app": "erpnext",
        "category": "Stock",
        "recipient_field": "customer",
        "recipient_doctype": "Customer",
    },
    # ERPNext Buying
    "Purchase Order": {
        "app": "erpnext",
        "category": "Buying",
        "recipient_field": "supplier",
        "recipient_doctype": "Supplier",
    },
    "Purchase Invoice": {
        "app": "erpnext",
        "category": "Buying",
        "recipient_field": "supplier",
        "recipient_doctype": "Supplier",
    },
    # ERPNext Accounts
    "Payment Entry": {
        "app": "erpnext",
        "category": "Accounts",
        "recipient_field": "party",
        "recipient_doctype": None,  # Dynamic based on party_type
    },
    "Payment Request": {
        "app": "erpnext",
        "category": "Accounts",
        "recipient_field": "email_to",
        "recipient_doctype": None,  # Uses email_to field directly
    },
    # Lending Module
    "Loan Application": {
        "app": "lending",
        "category": "Lending",
        "recipient_field": "applicant",
        "recipient_doctype": "Customer",
    },
    "Loan": {
        "app": "lending",
        "category": "Lending",
        "recipient_field": "applicant",
        "recipient_doctype": "Customer",
    },
    "Loan Repayment": {
        "app": "lending",
        "category": "Lending",
        "recipient_field": "applicant",
        "recipient_doctype": "Customer",
    },
}


class EmailServiceSettings(Document):
    def validate(self):
        if self.enabled:
            if not self.resend_api_key:
                frappe.throw(_("Resend API Key is required when service is enabled"))
            if not self.default_sender_email:
                frappe.throw(_("Default Sender Email is required when service is enabled"))

            # Validate API key format
            api_key = self.get_password("resend_api_key")
            if api_key and not api_key.startswith("re_"):
                frappe.throw(_("Invalid Resend API Key format. Key should start with 're_'"))

        # Validate doctype configurations
        self._validate_doctype_configurations()

    def _validate_doctype_configurations(self):
        """Validate that configured doctypes exist and their apps are installed."""
        if not self.supported_doctypes:
            return

        installed_apps = frappe.get_installed_apps()
        warnings = []

        for row in self.supported_doctypes:
            if not row.doctype_name:
                continue

            # Check if doctype exists
            if not frappe.db.exists("DocType", row.doctype_name):
                if row.enabled:
                    warnings.append(
                        _("DocType '{0}' does not exist. Configuration will be disabled.").format(
                            row.doctype_name
                        )
                    )
                    row.enabled = 0
                continue

            # Check if source app is installed
            if row.source_app and row.source_app not in installed_apps:
                if row.enabled:
                    warnings.append(
                        _("App '{0}' for '{1}' is not installed. Configuration will be disabled.").format(
                            row.source_app, row.doctype_name
                        )
                    )
                    row.enabled = 0

        if warnings:
            frappe.msgprint(
                "<br>".join(warnings),
                title=_("Doctype Configuration Warnings"),
                indicator="orange",
            )

    def get_template_id(self, doctype):
        """Get template ID for a given doctype from child table or legacy fields."""
        # First check child table
        config = self.get_doctype_config(doctype)
        if config and config.resend_template_id:
            return config.resend_template_id

        # Fallback to legacy fields for backward compatibility
        return self._get_legacy_template_id(doctype)

    def _get_legacy_template_id(self, doctype):
        """Fallback to old hardcoded fields for migration period."""
        legacy_map = {
            "Sales Invoice": getattr(self, "invoice_template_id", None),
            "Quotation": self.quotation_template_id,
            "Sales Order": self.sales_order_template_id,
            "Delivery Note": getattr(self, "delivery_note_template_id", None),
            "Payment Entry": getattr(self, "receipt_template_id", None),
            "Purchase Order": getattr(self, "purchase_order_template_id", None),
            "Payment Request": getattr(self, "payment_request_template_id", None),
        }
        return legacy_map.get(doctype)

    def get_doctype_config(self, doctype):
        """Get full configuration for a doctype from the child table."""
        if not self.supported_doctypes:
            return None

        for row in self.supported_doctypes:
            if row.doctype_name == doctype and row.enabled:
                return row

        return None

    def is_doctype_supported(self, doctype):
        """Check if a doctype is configured for Resend emails."""
        # Check child table first
        if self.supported_doctypes:
            for row in self.supported_doctypes:
                if row.doctype_name == doctype and row.enabled:
                    return True

        # Fallback: check if doctype has legacy template configured
        legacy_doctypes = ["Sales Invoice", "Quotation", "Sales Order", "Payment Request"]
        if doctype in legacy_doctypes and self._get_legacy_template_id(doctype):
            return True

        return False

    def get_available_doctypes(self):
        """Get list of doctypes available for email configuration based on installed apps."""
        installed_apps = frappe.get_installed_apps()
        available = []

        for doctype, info in DOCTYPE_REGISTRY.items():
            # Check if the app is installed
            if info["app"] not in installed_apps:
                continue

            # Check if the doctype actually exists
            if not frappe.db.exists("DocType", doctype):
                continue

            # Check if already configured
            is_configured = False
            if self.supported_doctypes:
                is_configured = any(
                    row.doctype_name == doctype for row in self.supported_doctypes
                )

            available.append(
                {
                    "doctype": doctype,
                    "app": info["app"],
                    "category": info["category"],
                    "default_recipient_field": info["recipient_field"],
                    "default_recipient_doctype": info["recipient_doctype"],
                    "is_configured": is_configured,
                }
            )

        return available

    def get_sender(self):
        """Get formatted sender string."""
        if self.default_sender_name:
            return f"{self.default_sender_name} <{self.default_sender_email}>"
        return self.default_sender_email


@frappe.whitelist()
def get_available_doctypes_for_site():
    """
    API endpoint to get doctypes available for email configuration.
    Used by the UI to populate the doctype selector.
    """
    settings = frappe.get_single("Email Service Settings")
    return settings.get_available_doctypes()


@frappe.whitelist()
def get_doctype_defaults(doctype):
    """Get default configuration values for a doctype."""
    if doctype not in DOCTYPE_REGISTRY:
        return {}

    info = DOCTYPE_REGISTRY[doctype]

    # Try to auto-detect source app
    source_app = info["app"]
    try:
        meta = frappe.get_meta(doctype)
        module = meta.module
        module_app = frappe.db.get_value("Module Def", module, "app_name")
        if module_app:
            source_app = module_app
    except Exception:
        pass

    return {
        "recipient_field": info["recipient_field"],
        "recipient_doctype": info["recipient_doctype"],
        "source_app": source_app,
    }
