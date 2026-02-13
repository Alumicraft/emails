import frappe


# Fields to copy from Email Branding → Email Service Settings
# Maps source field name → target field name
FIELD_MAP = {
    "enabled": "branding_enabled",
    "company": "company",
    "logo_url": "logo_url",
    "logo_url_secondary": "logo_url_secondary",
    "logo_alt_text": "logo_alt_text",
    "logo_height": "logo_height",
    "background_image_url": "background_image_url",
    "primary_color": "primary_color",
    "secondary_color": "secondary_color",
    "tertiary_color": "tertiary_color",
    "text_color": "text_color",
    "background_color": "background_color",
    "primary_color_dark": "primary_color_dark",
    "secondary_color_dark": "secondary_color_dark",
    "tertiary_color_dark": "tertiary_color_dark",
    "text_color_dark": "text_color_dark",
    "background_color_dark": "background_color_dark",
    "font_family": "font_family",
    "preheader_text": "preheader_text",
    "footer_text": "footer_text",
    "website_url": "website_url",
    "instagram_url": "instagram_url",
    "tiktok_url": "tiktok_url",
    "facebook_url": "facebook_url",
    "youtube_url": "youtube_url",
    "twitter_url": "twitter_url",
}


def execute():
    """Copy existing Email Branding values into Email Service Settings."""
    if not frappe.db.exists("DocType", "Email Branding"):
        return

    # Read values from Email Branding singles table
    branding_values = {}
    for row in frappe.db.get_all(
        "Singles",
        filters={"doctype": "Email Branding"},
        fields=["field", "value"],
    ):
        branding_values[row.field] = row.value

    if not branding_values:
        return

    # Write mapped values into Email Service Settings
    for source_field, target_field in FIELD_MAP.items():
        value = branding_values.get(source_field)
        if value is not None:
            frappe.db.set_single_value("Email Service Settings", target_field, value)

    frappe.db.commit()
