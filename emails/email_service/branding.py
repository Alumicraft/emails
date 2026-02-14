# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Email Branding Utilities

Provides functions to fetch branding from Email Service Settings and
prepare it for the Vercel email service.
"""

import frappe


def get_company_branding(company_name: str = None) -> dict:
    """
    Get branding configuration for emails.

    Fetches branding from the Email Service Settings Single DocType.
    If not configured or disabled, returns default values.

    Args:
        company_name: Ignored (kept for backward compatibility)

    Returns:
        dict: Branding configuration ready for Vercel API payload
    """
    try:
        branding_doc = frappe.get_single("Email Service Settings")
        if not branding_doc.branding_enabled:
            return get_default_branding()
        return branding_doc.get_branding_dict()
    except Exception:
        return get_default_branding()


def get_default_branding() -> dict:
    """
    Return default branding values when no branding is configured.

    These defaults provide a clean, professional look without
    requiring any configuration.
    """
    return {
        "company": "",
        "logo_url": "",
        "logo_url_dark": "",
        "logo_url_secondary": "",
        "logo_url_secondary_dark": "",
        "logo_height": 40,
        "logo_alt": "",
        "background_image_url": "",
        "primary_color": "#0066cc",
        "secondary_color": "",
        "tertiary_color": "#6b7280",
        "text_color": "#333333",
        "background_color": "#f8f9fa",
        "button_text_color": "#ffffff",
        "primary_color_dark": "#4d9fff",
        "secondary_color_dark": "",
        "tertiary_color_dark": "#9ca3af",
        "text_color_dark": "#ffffff",
        "background_color_dark": "#1a1a1a",
        "button_text_color_dark": "",
        "font_family": "Arial, Helvetica, sans-serif",
        "footer_text": "",
        "preheader": "",
        "company_email": "",
        "company_phone": "",
        "mailing_address": "",
        "website_url": "",
        "social_links": [],
    }
