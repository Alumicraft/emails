# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Vercel Email Service Client

HTTP client for communicating with the Vercel-hosted react-email service.
Handles authentication, request building, and error handling.
"""

import json
import frappe
import requests
from frappe import _


class VercelEmailError(Exception):
    """Custom exception for Vercel email service errors."""
    pass


def get_service_config() -> dict:
    """
    Get Vercel service configuration from Email Service Settings.

    Returns:
        dict: Configuration with url, key, from_email, from_name

    Raises:
        VercelEmailError: If service is not properly configured
    """
    settings = frappe.get_single("Email Service Settings")

    if not settings.enabled:
        raise VercelEmailError(_("Email Service is not enabled"))

    vercel_url = getattr(settings, "vercel_service_url", None)
    if not vercel_url:
        raise VercelEmailError(_("Vercel service URL not configured"))

    service_key = settings.get_password("vercel_service_key")
    if not service_key:
        raise VercelEmailError(_("Vercel service API key not configured"))

    return {
        "url": vercel_url.rstrip("/") + "/api/send",
        "key": service_key,
        "from_email": settings.default_sender_email,
        "from_name": settings.default_sender_name or "",
    }


def send_email(
    template: str,
    to_email,
    subject: str,
    data: dict,
    branding: dict,
    cc=None,
    bcc=None,
    attachments: list = None,
    reply_to: str = None,
    tags: list = None,
) -> dict:
    """
    Send email via Vercel react-email service.

    Args:
        template: Template name ("document", "notification", "auth")
        to_email: Recipient email(s) - string or list
        subject: Email subject
        data: Template-specific data dict
        branding: Branding dict from get_company_branding()
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        attachments: List of {"filename": str, "content": base64_str} (optional)
        reply_to: Reply-to address (optional)
        tags: List of {"name": str, "value": str} for tracking (optional)

    Returns:
        dict: {"message_id": str} on success

    Raises:
        VercelEmailError: On API failure or configuration error
    """
    config = get_service_config()

    # Normalize recipients to lists
    if isinstance(to_email, str):
        to_email = [to_email]
    if cc and isinstance(cc, str):
        cc = [cc]
    if bcc and isinstance(bcc, str):
        bcc = [bcc]

    # Build request payload
    payload = {
        "template": template,
        "to": to_email,
        "subject": subject,
        "data": data,
        "branding": branding,
        "from_email": config["from_email"],
        "from_name": config["from_name"],
    }

    if cc:
        payload["cc"] = cc
    if bcc:
        payload["bcc"] = bcc
    if attachments:
        payload["attachments"] = attachments
    if reply_to:
        payload["reply_to"] = reply_to
    if tags:
        payload["tags"] = tags

    # Make API request
    headers = {
        "Authorization": f"Bearer {config['key']}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            config["url"],
            json=payload,
            headers=headers,
            timeout=30,
        )

        result = response.json()

        if response.status_code == 200:
            # Log if enabled
            settings = frappe.get_single("Email Service Settings")
            if settings.log_all_attempts:
                frappe.log_error(
                    title="Vercel Email Sent",
                    message=f"To: {to_email}\nSubject: {subject}\nMessage ID: {result.get('message_id')}"
                )
            return {"message_id": result.get("message_id")}

        # Handle error response
        error_msg = result.get("error", "Unknown error")
        frappe.log_error(
            title="Vercel Email Error",
            message=f"Status: {response.status_code}\nError: {error_msg}\nPayload: {json.dumps(payload, indent=2)[:2000]}"
        )
        raise VercelEmailError(f"Vercel service error: {error_msg}")

    except requests.exceptions.Timeout:
        frappe.log_error(
            title="Vercel Email Timeout",
            message=f"Request timed out after 30 seconds\nTo: {to_email}"
        )
        raise VercelEmailError(_("Email service request timed out"))

    except requests.exceptions.ConnectionError as e:
        frappe.log_error(
            title="Vercel Email Connection Error",
            message=str(e)
        )
        raise VercelEmailError(_("Failed to connect to email service"))

    except requests.exceptions.RequestException as e:
        frappe.log_error(
            title="Vercel Email Request Error",
            message=str(e)
        )
        raise VercelEmailError(_("Email service request failed: {0}").format(str(e)))


def test_connection() -> dict:
    """
    Test connection to Vercel email service.

    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        config = get_service_config()

        # Just check if we can reach the service
        # The actual endpoint would need to support a health check
        response = requests.get(
            config["url"].replace("/api/send", "/api/health"),
            headers={"Authorization": f"Bearer {config['key']}"},
            timeout=10,
        )

        if response.status_code == 200:
            return {
                "success": True,
                "message": _("Vercel email service connection successful"),
            }
        else:
            return {
                "success": False,
                "message": _("Service returned status {0}").format(response.status_code),
            }

    except VercelEmailError as e:
        return {
            "success": False,
            "message": str(e),
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": _("Connection failed: {0}").format(str(e)),
        }
