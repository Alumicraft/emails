# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmailDoctypeConfiguration(Document):
    """Child table for configuring email-enabled doctypes."""

    def validate(self):
        """Validate the configuration row."""
        if self.doctype_name:
            # Verify the doctype exists
            if not frappe.db.exists("DocType", self.doctype_name):
                frappe.throw(f"DocType '{self.doctype_name}' does not exist")

            # Auto-detect source app if not set
            if not self.source_app:
                self.source_app = self._detect_source_app()

    def _detect_source_app(self):
        """Detect which app provides this doctype."""
        if not self.doctype_name:
            return None

        try:
            meta = frappe.get_meta(self.doctype_name)
            module = meta.module

            # Get app from module
            module_app = frappe.db.get_value("Module Def", module, "app_name")
            return module_app
        except Exception:
            return None
