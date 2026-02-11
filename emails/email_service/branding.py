# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Email Branding Utilities

Provides functions to fetch company branding and prepare it for the Vercel
email service. Supports logo embedding as base64 for CID references.
"""

import base64
import frappe


def get_company_branding(company_name: str = None) -> dict:
    """
    Get branding dict for a company.

    Looks up Email Branding for the specified company. If not found or
    company is None, falls back to the default branding (is_default=1).
    If no branding is configured, returns default values.

    Args:
        company_name: Company to get branding for. If None, uses default.

    Returns:
        dict: Branding configuration ready for Vercel API payload
    """
    branding_doc = None

    # Try company-specific branding
    if company_name:
        branding_name = frappe.db.get_value(
            "Email Branding",
            {"company": company_name, "enabled": 1}
        )
        if branding_name:
            branding_doc = frappe.get_doc("Email Branding", branding_name)

    # Fall back to default branding
    if not branding_doc:
        branding_name = frappe.db.get_value(
            "Email Branding",
            {"is_default": 1, "enabled": 1}
        )
        if branding_name:
            branding_doc = frappe.get_doc("Email Branding", branding_name)

    # No branding configured - return defaults
    if not branding_doc:
        return get_default_branding()

    # Get branding dict from document
    branding = branding_doc.get_branding_dict()

    # Add logos as base64 for CID embedding
    if branding_doc.logo:
        logo_data = get_file_as_base64(branding_doc.logo)
        if logo_data:
            branding["logo_base64"] = logo_data[0]
            branding["logo_type"] = logo_data[1]

    if branding_doc.logo_dark:
        logo_dark_data = get_file_as_base64(branding_doc.logo_dark)
        if logo_dark_data:
            branding["logo_dark_base64"] = logo_dark_data[0]
            branding["logo_dark_type"] = logo_dark_data[1]

    return branding


def get_default_branding() -> dict:
    """
    Return default branding values when no branding is configured.

    These defaults provide a clean, professional look without
    requiring any configuration.
    """
    return {
        "company": "",
        "logo_height": 40,
        "logo_alt": "",
        "primary_color": "#0066cc",
        "secondary_color": "",
        "text_color": "#333333",
        "background_color": "#f8f9fa",
        "primary_color_dark": "#4d9fff",
        "secondary_color_dark": "",
        "text_color_dark": "#ffffff",
        "background_color_dark": "#1a1a1a",
        "font_family": "Arial, Helvetica, sans-serif",
        "footer_text": "",
        "preheader": "",
        "website_url": "",
        "social_links": [],
    }


def get_file_as_base64(file_url: str) -> tuple:
    """
    Read a Frappe file and return as base64.

    Handles both public (/files/) and private (/private/files/) paths.

    Args:
        file_url: URL path to the file (e.g., /files/logo.png)

    Returns:
        tuple: (base64_content, media_type) or None if file not found
    """
    if not file_url:
        return None

    try:
        # Determine file path based on URL
        if file_url.startswith("/private/files/"):
            file_path = frappe.get_site_path(file_url.lstrip("/"))
        elif file_url.startswith("/files/"):
            file_path = frappe.get_site_path("public", file_url.lstrip("/"))
        else:
            # Assume it's a relative path in public files
            file_path = frappe.get_site_path("public", "files", file_url.lstrip("/"))

        with open(file_path, "rb") as f:
            content = f.read()

        base64_content = base64.b64encode(content).decode("utf-8")
        media_type = get_media_type(file_url)

        return base64_content, media_type

    except FileNotFoundError:
        frappe.log_error(
            title="Email Branding: Logo file not found",
            message=f"File: {file_url}"
        )
        return None
    except Exception as e:
        frappe.log_error(
            title="Email Branding: Failed to read logo",
            message=f"File: {file_url}\nError: {str(e)}"
        )
        return None


def get_media_type(filename: str) -> str:
    """
    Return MIME type based on file extension.

    Args:
        filename: File name or path

    Returns:
        str: MIME type (defaults to image/png)
    """
    ext = filename.lower().split(".")[-1]
    types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
    }
    return types.get(ext, "image/png")
