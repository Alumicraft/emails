# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Migration patch: Move legacy template fields to new Email Doctype Configuration child table.

This patch migrates existing Email Service Settings configurations from the old
hardcoded template ID fields to the new dynamic child table structure.
"""

import frappe


def execute():
    """Migrate existing Email Service Settings to new child table structure."""

    # Legacy field to doctype mapping with default configurations
    legacy_mapping = [
        {
            "legacy_field": "invoice_template_id",
            "doctype_name": "Sales Invoice",
            "recipient_field": "customer",
            "recipient_doctype": "Customer",
            "source_app": "erpnext",
        },
        {
            "legacy_field": "quotation_template_id",
            "doctype_name": "Quotation",
            "recipient_field": "party_name",
            "recipient_doctype": "Customer",
            "source_app": "erpnext",
        },
        {
            "legacy_field": "sales_order_template_id",
            "doctype_name": "Sales Order",
            "recipient_field": "customer",
            "recipient_doctype": "Customer",
            "source_app": "erpnext",
        },
        {
            "legacy_field": "delivery_note_template_id",
            "doctype_name": "Delivery Note",
            "recipient_field": "customer",
            "recipient_doctype": "Customer",
            "source_app": "erpnext",
        },
        {
            "legacy_field": "receipt_template_id",
            "doctype_name": "Payment Entry",
            "recipient_field": "party",
            "recipient_doctype": None,
            "source_app": "erpnext",
        },
        {
            "legacy_field": "purchase_order_template_id",
            "doctype_name": "Purchase Order",
            "recipient_field": "supplier",
            "recipient_doctype": "Supplier",
            "source_app": "erpnext",
        },
    ]

    try:
        settings = frappe.get_single("Email Service Settings")
    except Exception:
        # Settings don't exist yet, nothing to migrate
        return

    # Skip if already migrated (child table has entries)
    if settings.supported_doctypes and len(settings.supported_doctypes) > 0:
        frappe.log_error(
            title="Email Settings Migration Skipped",
            message="Child table already has entries, skipping migration.",
        )
        return

    migrated_count = 0

    for config in legacy_mapping:
        legacy_field = config["legacy_field"]
        doctype_name = config["doctype_name"]

        # Get template ID from legacy field
        template_id = getattr(settings, legacy_field, None)

        # Only migrate if the doctype exists in this installation
        if not frappe.db.exists("DocType", doctype_name):
            continue

        # Create child table entry
        settings.append(
            "supported_doctypes",
            {
                "doctype_name": doctype_name,
                "enabled": 1,
                "resend_template_id": template_id or "",
                "recipient_field": config["recipient_field"],
                "recipient_doctype": config["recipient_doctype"],
                "email_field_path": "",
                "subject_template": "",
                "require_submit": 1,
                "print_format": None,
                "source_app": config["source_app"],
            },
        )
        migrated_count += 1

    if migrated_count > 0:
        settings.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.log_error(
            title="Email Settings Migration Complete",
            message=f"Migrated {migrated_count} doctype configurations to child table.",
        )
