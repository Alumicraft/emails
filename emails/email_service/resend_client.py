import json
import frappe
import requests

RESEND_API_URL = "https://api.resend.com/emails"


class ResendError(Exception):
    """Custom exception for Resend API errors"""
    pass


def get_api_key():
    """Get Resend API key from settings"""
    settings = frappe.get_single("Email Service Settings")
    if not settings.enabled:
        raise ResendError("Email Service is not enabled")

    api_key = settings.get_password("resend_api_key")
    if not api_key:
        raise ResendError("Resend API key not configured")

    return api_key


def send_email(
    to_email,
    subject,
    html_content=None,
    text_content=None,
    from_email=None,
    from_name=None,
    reply_to=None,
    cc=None,
    bcc=None,
    attachments=None,
    tags=None
):
    """
    Send email directly with HTML/text content (no template).

    Args:
        to_email: Recipient email (string or list)
        subject: Email subject
        html_content: HTML body content
        text_content: Plain text body content
        from_email: Sender email (optional, uses default)
        from_name: Sender name (optional)
        reply_to: Reply-to email address
        cc: CC recipients (string or list)
        bcc: BCC recipients (string or list)
        attachments: List of attachment dicts [{filename, content (base64)}]
        tags: List of tag dicts for tracking [{name, value}]

    Returns:
        dict: Response with message_id on success

    Raises:
        ResendError: On API failure
    """
    api_key = get_api_key()
    settings = frappe.get_single("Email Service Settings")

    # Build sender
    if not from_email:
        from_email = settings.default_sender_email
    if not from_name:
        from_name = settings.default_sender_name

    if from_name:
        sender = f"{from_name} <{from_email}>"
    else:
        sender = from_email

    # Normalize recipients to lists
    if isinstance(to_email, str):
        to_email = [to_email]
    if cc and isinstance(cc, str):
        cc = [cc]
    if bcc and isinstance(bcc, str):
        bcc = [bcc]

    # Build request payload
    payload = {
        "from": sender,
        "to": to_email,
        "subject": subject,
    }

    if html_content:
        payload["html"] = html_content
    if text_content:
        payload["text"] = text_content
    if reply_to:
        payload["reply_to"] = reply_to
    if cc:
        payload["cc"] = cc
    if bcc:
        payload["bcc"] = bcc
    if attachments:
        payload["attachments"] = attachments
    if tags:
        payload["tags"] = tags

    # Make API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            RESEND_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        response_data = response.json()

        if response.status_code == 200:
            return {
                "success": True,
                "message_id": response_data.get("id"),
                "response": response_data
            }
        else:
            error_msg = response_data.get("message", response_data.get("error", "Unknown error"))
            frappe.log_error(
                title="Resend API Error",
                message=f"Status: {response.status_code}\nResponse: {json.dumps(response_data, indent=2)}\nPayload: {json.dumps(payload, indent=2)}"
            )
            raise ResendError(f"Resend API error: {error_msg}")

    except requests.exceptions.Timeout:
        frappe.log_error(title="Resend API Timeout", message="Request timed out after 30 seconds")
        raise ResendError("Resend API request timed out")
    except requests.exceptions.RequestException as e:
        frappe.log_error(title="Resend API Request Error", message=str(e))
        raise ResendError(f"Resend API request failed: {str(e)}")


def send_template_email(
    template_id,
    to_email,
    template_data,
    from_email=None,
    from_name=None,
    subject=None,
    reply_to=None,
    cc=None,
    bcc=None,
    attachments=None,
    tags=None
):
    """
    Send email using a Resend template.

    Args:
        template_id: Resend template ID (e.g., 'template_abc123')
        to_email: Recipient email (string or list)
        template_data: Dict of variables to pass to template
        from_email: Sender email (optional, uses default)
        from_name: Sender name (optional)
        subject: Override template subject (optional)
        reply_to: Reply-to email address
        cc: CC recipients (string or list)
        bcc: BCC recipients (string or list)
        attachments: List of attachment dicts [{filename, content (base64)}]
        tags: List of tag dicts for tracking [{name, value}]

    Returns:
        dict: Response with message_id on success

    Raises:
        ResendError: On API failure
    """
    api_key = get_api_key()
    settings = frappe.get_single("Email Service Settings")

    # Build sender
    if not from_email:
        from_email = settings.default_sender_email
    if not from_name:
        from_name = settings.default_sender_name

    if from_name:
        sender = f"{from_name} <{from_email}>"
    else:
        sender = from_email

    # Normalize recipients to lists
    if isinstance(to_email, str):
        to_email = [to_email]
    if cc and isinstance(cc, str):
        cc = [cc]
    if bcc and isinstance(bcc, str):
        bcc = [bcc]

    # Build request payload for template
    payload = {
        "from": sender,
        "to": to_email,
    }

    if subject:
        payload["subject"] = subject
    if reply_to:
        payload["reply_to"] = reply_to
    if cc:
        payload["cc"] = cc
    if bcc:
        payload["bcc"] = bcc
    if attachments:
        payload["attachments"] = attachments
    if tags:
        payload["tags"] = tags

    # Build HTML from template data
    html_content = build_html_from_template_data(template_id, template_data)
    if html_content:
        payload["html"] = html_content
        if not subject:
            payload["subject"] = template_data.get("subject", "Document from ERPNext")

    # Make API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            RESEND_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        response_data = response.json()

        if response.status_code == 200:
            if frappe.get_single("Email Service Settings").log_all_attempts:
                frappe.log_error(
                    title="Resend Email Sent",
                    message=f"To: {to_email}\nMessage ID: {response_data.get('id')}"
                )
            return {
                "success": True,
                "message_id": response_data.get("id"),
                "response": response_data
            }
        else:
            error_msg = response_data.get("message", response_data.get("error", "Unknown error"))
            frappe.log_error(
                title="Resend API Error",
                message=f"Status: {response.status_code}\nResponse: {json.dumps(response_data, indent=2)}"
            )
            raise ResendError(f"Resend API error: {error_msg}")

    except requests.exceptions.Timeout:
        frappe.log_error(title="Resend API Timeout", message="Request timed out")
        raise ResendError("Resend API request timed out")
    except requests.exceptions.RequestException as e:
        frappe.log_error(title="Resend API Request Error", message=str(e))
        raise ResendError(f"Resend API request failed: {str(e)}")


def build_html_from_template_data(template_id, data):
    """
    Build HTML email from template data.

    Args:
        template_id: Template identifier
        data: Dict of template variables

    Returns:
        str: Rendered HTML content
    """
    company_name = data.get("company_name", "")
    customer_name = data.get("customer_name", "")
    document_type = data.get("document_type", "Document")
    document_number = data.get("document_number", "")
    document_date = data.get("document_date", "")
    total_amount = data.get("total_amount", "")
    due_date = data.get("due_date", "")
    custom_message = data.get("custom_message", "")

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document_type} from {company_name}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
        <h2 style="color: #2c3e50; margin-top: 0;">{document_type} from {company_name}</h2>

        <p>Hi {customer_name},</p>

        <p>Please find your {document_type.lower()} details below:</p>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>{document_type} Number:</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{document_number}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>Date:</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{document_date}</td>
            </tr>
            {"<tr><td style='padding: 10px; border-bottom: 1px solid #dee2e6;'><strong>Due Date:</strong></td><td style='padding: 10px; border-bottom: 1px solid #dee2e6;'>" + due_date + "</td></tr>" if due_date else ""}
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>Total Amount:</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-size: 18px; color: #2c3e50;"><strong>{total_amount}</strong></td>
            </tr>
        </table>

        {f"<p>{custom_message}</p>" if custom_message else ""}

        <p>Please find the detailed {document_type.lower()} attached as a PDF.</p>

        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">

        <p style="color: #6c757d; font-size: 14px;">
            Best regards,<br>
            <strong>{company_name}</strong>
        </p>
    </div>
</body>
</html>
"""
    return html


def test_connection():
    """
    Test Resend API connection.

    Returns:
        dict: Success status and message
    """
    try:
        api_key = get_api_key()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            "https://api.resend.com/domains",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return {
                "success": True,
                "message": "Resend API connection successful"
            }
        else:
            return {
                "success": False,
                "message": f"API returned status {response.status_code}"
            }

    except ResendError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}"
        }
