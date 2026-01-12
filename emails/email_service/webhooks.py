"""
Resend Webhook Handler

Handles webhook events from Resend for email tracking (delivered, opened, clicked, etc.)
"""

import frappe
import json


@frappe.whitelist(allow_guest=True)
def handle_resend_webhook():
    """
    Handle incoming webhook from Resend.

    Resend sends events like:
    - email.sent
    - email.delivered
    - email.opened
    - email.clicked
    - email.bounced
    - email.complained
    """
    try:
        # Get the webhook payload
        payload = frappe.request.get_data(as_text=True)

        if not payload:
            frappe.log_error(title="Resend Webhook", message="Empty payload received")
            return {"status": "error", "message": "Empty payload"}

        data = json.loads(payload)

        event_type = data.get("type")
        event_data = data.get("data", {})

        # Log for debugging
        if frappe.get_single("Email Service Settings").log_all_attempts:
            frappe.log_error(
                title=f"Resend Webhook: {event_type}",
                message=json.dumps(data, indent=2)
            )

        # Get the email ID from Resend
        email_id = event_data.get("email_id")

        if not email_id:
            return {"status": "ok", "message": "No email_id in event"}

        # Find the Communication with this message_id
        comm_name = frappe.db.get_value(
            "Communication",
            {"message_id": email_id},
            "name"
        )

        if not comm_name:
            # Try without the angle brackets
            comm_name = frappe.db.get_value(
                "Communication",
                {"message_id": ["like", f"%{email_id}%"]},
                "name"
            )

        if not comm_name:
            return {"status": "ok", "message": "Communication not found"}

        # Handle different event types
        if event_type == "email.delivered":
            update_communication_status(comm_name, "delivered")

        elif event_type == "email.opened":
            update_communication_status(comm_name, "opened")
            mark_communication_as_read(comm_name)

        elif event_type == "email.clicked":
            update_communication_status(comm_name, "clicked")
            mark_communication_as_read(comm_name)

        elif event_type == "email.bounced":
            update_communication_status(comm_name, "bounced")
            add_communication_comment(comm_name, f"Email bounced: {event_data.get('bounce', {}).get('message', 'Unknown reason')}")

        elif event_type == "email.complained":
            update_communication_status(comm_name, "complained")
            add_communication_comment(comm_name, "Recipient marked email as spam")

        frappe.db.commit()

        return {"status": "ok"}

    except json.JSONDecodeError as e:
        frappe.log_error(title="Resend Webhook JSON Error", message=str(e))
        return {"status": "error", "message": "Invalid JSON"}
    except Exception as e:
        frappe.log_error(title="Resend Webhook Error", message=frappe.get_traceback())
        return {"status": "error", "message": str(e)}


def update_communication_status(comm_name, status):
    """Update communication with delivery status."""
    frappe.db.set_value(
        "Communication",
        comm_name,
        "delivery_status",
        status.title(),
        update_modified=False
    )


def mark_communication_as_read(comm_name):
    """Mark communication as read/seen."""
    frappe.db.set_value(
        "Communication",
        comm_name,
        {
            "read_by_recipient": 1,
            "read_by_recipient_on": frappe.utils.now()
        },
        update_modified=False
    )


def add_communication_comment(comm_name, comment):
    """Add a comment to the communication."""
    comm = frappe.get_doc("Communication", comm_name)
    comm.add_comment("Comment", comment)
