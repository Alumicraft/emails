# Copyright (c) 2024, Alumicraft and contributors
# For license information, please see license.txt

"""
Sendmail Override

Intercepts frappe.sendmail to route system emails (password reset, welcome,
notifications) through the Vercel react-email service with branding.

Falls back to Frappe's default email system if:
- Vercel service is not configured
- handle_system_emails is disabled
- Vercel service fails and fallback_to_erpnext is enabled
"""

import frappe
from frappe import _

# Store reference to original sendmail
_original_sendmail = None

# Keywords that indicate auth-related emails (password reset, verification, etc.)
AUTH_SUBJECTS = [
    "password",
    "reset",
    "verify",
    "verification",
    "2fa",
    "otp",
    "welcome",
    "authenticate",
]

# Keywords that indicate magic link / passwordless login emails
MAGIC_LINK_SUBJECTS = [
    "magic link",
    "login link",
    "sign in link",
    "passwordless",
    "login to",
    "sign in to",
]


def override_sendmail():
    """
    Monkey-patch frappe.sendmail to route through Vercel.

    This function should be called on session creation via hooks.py.
    It stores the original sendmail and replaces it with our patched version.
    """
    global _original_sendmail

    if _original_sendmail is None:
        _original_sendmail = frappe.sendmail

    frappe.sendmail = patched_sendmail


def patched_sendmail(
    recipients=None,
    sender=None,
    subject=None,
    message=None,
    content=None,
    reference_doctype=None,
    reference_name=None,
    add_unsubscribe_link=True,
    attachments=None,
    reply_to=None,
    cc=None,
    bcc=None,
    delayed=True,
    communication=None,
    now=False,
    print_html=None,
    print_format=None,
    send_me_a_copy=False,
    header=None,
    with_container=True,
    as_markdown=False,
    template=None,
    args=None,
    is_notification=False,
    inline_images=None,
    **kwargs
):
    """
    Patched sendmail that routes system emails through Vercel.

    If Vercel is configured and handle_system_emails is enabled, emails are
    sent via the Vercel react-email service. Otherwise, falls back to the
    original frappe.sendmail.
    """
    # Check if we should use Vercel
    use_vercel = _should_use_vercel()

    if not use_vercel:
        return _call_original(
            recipients, sender, subject, message, content,
            reference_doctype, reference_name, add_unsubscribe_link,
            attachments, reply_to, cc, bcc, delayed, communication,
            now, print_html, print_format, send_me_a_copy, header,
            with_container, as_markdown, template, args,
            is_notification, inline_images, **kwargs
        )

    # Import here to avoid circular imports
    from emails.email_service.vercel_client import send_email, VercelEmailError
    from emails.email_service.branding import get_company_branding

    # Prepare HTML content
    html_content = message or content or ""

    if template:
        html_content = frappe.render_template(template, args or {})

    if as_markdown and html_content:
        import markdown
        html_content = markdown.markdown(html_content)

    # Determine company for branding
    company_name = _get_company_from_context(reference_doctype, reference_name)
    branding = get_company_branding(company_name)

    # Normalize recipients
    if isinstance(recipients, str):
        recipients = [recipients]
    if not recipients:
        # No recipients, call original to handle the error
        return _call_original(
            recipients, sender, subject, message, content,
            reference_doctype, reference_name, add_unsubscribe_link,
            attachments, reply_to, cc, bcc, delayed, communication,
            now, print_html, print_format, send_me_a_copy, header,
            with_container, as_markdown, template, args,
            is_notification, inline_images, **kwargs
        )

    # Determine template type based on subject
    template_type = _get_system_template(subject, html_content)

    # Build data for template
    template_data = {
        "message": html_content,
        "title": subject or "",
    }

    # For magic-link emails, extract the login link
    if template_type == "magic-link":
        action_link = _extract_action_link(html_content)
        if action_link:
            template_data["magic_link"] = action_link
            template_data["button_text"] = "Sign In"
            template_data["title"] = "Sign in to your account"
            template_data["message"] = "Click the button below to securely sign in. No password required."

    # For auth emails, try to extract action link
    elif template_type == "auth":
        action_link = _extract_action_link(html_content)
        if action_link:
            template_data["reset_link"] = action_link
            template_data["action_link"] = action_link
            template_data["action_label"] = _get_action_label(subject)

    # Send via Vercel
    try:
        result = send_email(
            template=template_type,
            to_email=recipients,
            subject=subject or _("Notification"),
            data=template_data,
            branding=branding,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            tags=[
                {"name": "type", "value": "system"},
                {"name": "template", "value": template_type},
                {"name": "doctype", "value": reference_doctype or "none"},
            ],
        )

        # Log communication if reference provided
        if reference_doctype and reference_name and not communication:
            from emails.email_service.utils import create_communication_log
            create_communication_log(
                doctype=reference_doctype,
                docname=reference_name,
                recipient=", ".join(recipients) if recipients else "",
                subject=subject or "",
                content=html_content[:500] if html_content else "",
                status="Sent",
                message_id=result.get("message_id"),
            )

        return result

    except VercelEmailError as e:
        frappe.log_error(
            title="Vercel sendmail failed",
            message=str(e)
        )

        # Fallback to original sendmail
        settings = frappe.get_single("Email Service Settings")
        if getattr(settings, "fallback_to_erpnext", True):
            return _call_original(
                recipients, sender, subject, message, content,
                reference_doctype, reference_name, add_unsubscribe_link,
                attachments, reply_to, cc, bcc, delayed, communication,
                now, print_html, print_format, send_me_a_copy, header,
                with_container, as_markdown, template, args,
                is_notification, inline_images, **kwargs
            )

        raise


def _should_use_vercel() -> bool:
    """Check if Vercel should be used for system emails."""
    try:
        settings = frappe.get_single("Email Service Settings")
        return bool(
            settings.enabled
            and getattr(settings, "vercel_service_url", None)
            and settings.get_password("vercel_service_key")
            and getattr(settings, "handle_system_emails", True)
        )
    except Exception:
        return False


def _get_company_from_context(reference_doctype, reference_name) -> str:
    """Try to determine company from document context."""
    company_name = None

    if reference_doctype and reference_name:
        try:
            doc = frappe.get_doc(reference_doctype, reference_name)
            company_name = getattr(doc, "company", None)
        except Exception:
            pass

    if not company_name:
        company_name = frappe.defaults.get_global_default("company")

    return company_name


def _get_system_template(subject: str, content: str) -> str:
    """
    Determine which template to use based on email subject/content.

    Returns:
        "magic-link" for passwordless login / magic link emails
        "auth" for password reset, welcome, 2FA, etc.
        "notification" for everything else
    """
    subject_lower = (subject or "").lower()
    content_lower = (content or "").lower()

    # Check for magic link / passwordless login first
    if any(kw in subject_lower for kw in MAGIC_LINK_SUBJECTS):
        return "magic-link"
    if any(kw in content_lower for kw in ["magic link", "passwordless", "click to sign in", "click to login"]):
        return "magic-link"

    # Check for auth-related emails (password reset, verification, etc.)
    if any(kw in subject_lower for kw in AUTH_SUBJECTS):
        return "auth"
    if any(kw in content_lower for kw in ["reset your password", "verify your email", "one-time password"]):
        return "auth"

    return "notification"


def _extract_action_link(html_content: str) -> str:
    """Extract the primary action link from HTML content."""
    import re

    if not html_content:
        return None

    # Look for common link patterns
    patterns = [
        r'href=["\']([^"\']*reset[^"\']*)["\']',
        r'href=["\']([^"\']*verify[^"\']*)["\']',
        r'href=["\']([^"\']*confirm[^"\']*)["\']',
        r'href=["\']([^"\']*login[^"\']*)["\']',
        r'href=["\']([^"\']*action[^"\']*)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def _get_action_label(subject: str) -> str:
    """Get appropriate button label based on subject."""
    subject_lower = (subject or "").lower()

    if "password" in subject_lower or "reset" in subject_lower:
        return _("Reset Password")
    elif "verify" in subject_lower:
        return _("Verify Email")
    elif "welcome" in subject_lower:
        return _("Get Started")
    elif "2fa" in subject_lower or "otp" in subject_lower:
        return _("Verify")
    elif "login" in subject_lower:
        return _("Sign In")

    return _("Continue")


def _call_original(
    recipients, sender, subject, message, content,
    reference_doctype, reference_name, add_unsubscribe_link,
    attachments, reply_to, cc, bcc, delayed, communication,
    now, print_html, print_format, send_me_a_copy, header,
    with_container, as_markdown, template, args,
    is_notification, inline_images, **kwargs
):
    """Call the original frappe.sendmail."""
    return _original_sendmail(
        recipients=recipients,
        sender=sender,
        subject=subject,
        message=message,
        content=content,
        reference_doctype=reference_doctype,
        reference_name=reference_name,
        add_unsubscribe_link=add_unsubscribe_link,
        attachments=attachments,
        reply_to=reply_to,
        cc=cc,
        bcc=bcc,
        delayed=delayed,
        communication=communication,
        now=now,
        print_html=print_html,
        print_format=print_format,
        send_me_a_copy=send_me_a_copy,
        header=header,
        with_container=with_container,
        as_markdown=as_markdown,
        template=template,
        args=args,
        is_notification=is_notification,
        inline_images=inline_images,
        **kwargs
    )
