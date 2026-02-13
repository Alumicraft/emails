import frappe


def execute():
    """Remove Email Doctype Configuration child table data.

    The Supported Document Types child table has been removed from
    Email Service Settings. All doctypes are now supported when the
    service is enabled, using hardcoded DOCTYPE_REGISTRY for recipient
    resolution and DOCTYPE_TEMPLATE_MAP for template selection.
    """
    # Clear child table data from the singles table
    frappe.db.sql(
        "DELETE FROM tabSingles WHERE doctype = 'Email Service Settings' AND field IN ('supported_doctypes', 'auto_detect_modules')"
    )

    # Drop the child table if it exists
    if frappe.db.exists("DocType", "Email Doctype Configuration"):
        frappe.delete_doc("DocType", "Email Doctype Configuration", force=True)

    frappe.db.commit()
