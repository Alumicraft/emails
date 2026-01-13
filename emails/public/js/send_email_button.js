// Send Email Button for supported doctypes
// This adds a "Send Email" button for submitted documents with configured templates

frappe.provide("emails");

emails.SUPPORTED_DOCTYPES = [
    "Sales Invoice",
    "Quotation",
    "Sales Order",
    "Delivery Note",
    "Payment Entry",
    "Purchase Order",
    "Payment Request"
];

emails.setup_send_email_button = function(frm) {
    // Only show for submitted documents
    if (frm.doc.docstatus !== 1) {
        return;
    }

    // Check if this doctype is supported
    if (!emails.SUPPORTED_DOCTYPES.includes(frm.doctype)) {
        return;
    }

    // Check if Resend is enabled and template is configured for this doctype
    frappe.call({
        method: "emails.api.check_doctype_email_enabled",
        args: {
            doctype: frm.doctype
        },
        callback: function(r) {
            if (r.message && r.message.enabled) {
                frm.add_custom_button(__("Send Email"), function() {
                    emails.show_send_email_dialog(frm);
                });
            }
        }
    });
};

emails.show_send_email_dialog = function(frm) {
    // Get default recipient email
    frappe.call({
        method: "emails.api.get_document_recipient",
        args: {
            doctype: frm.doctype,
            docname: frm.doc.name
        },
        callback: function(r) {
            let default_email = r.message ? r.message.email : "";

            let dialog = new frappe.ui.Dialog({
                title: __("Send Email via Resend"),
                fields: [
                    {
                        fieldname: "to_email",
                        fieldtype: "Data",
                        label: __("Recipient Email"),
                        reqd: 1,
                        default: default_email,
                        options: "Email"
                    },
                    {
                        fieldname: "cc",
                        fieldtype: "Data",
                        label: __("CC"),
                        options: "Email"
                    },
                    {
                        fieldname: "custom_message",
                        fieldtype: "Small Text",
                        label: __("Additional Message (Optional)")
                    }
                ],
                primary_action_label: __("Send"),
                primary_action: function(values) {
                    dialog.hide();
                    emails.send_document_email(frm, values);
                }
            });

            dialog.show();
        }
    });
};

emails.send_document_email = function(frm, values) {
    frappe.call({
        method: "emails.api.send_document_email",
        args: {
            doctype: frm.doctype,
            docname: frm.doc.name,
            to_email: values.to_email,
            cc: values.cc,
            custom_message: values.custom_message
        },
        freeze: true,
        freeze_message: __("Sending email..."),
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: __("Email sent successfully"),
                    indicator: "green"
                });
                // Reload to show new communication in timeline
                frm.reload_doc();
            } else {
                frappe.msgprint({
                    title: __("Email Failed"),
                    message: r.message ? r.message.message : __("Unknown error"),
                    indicator: "red"
                });
            }
        }
    });
};

// Setup form hooks for all supported doctypes
$(document).ready(function() {
    emails.SUPPORTED_DOCTYPES.forEach(function(doctype) {
        frappe.ui.form.on(doctype, {
            refresh: function(frm) {
                emails.setup_send_email_button(frm);
            }
        });
    });
});
