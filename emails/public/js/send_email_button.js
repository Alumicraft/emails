// Send Email Button for supported doctypes
// Shows popup after submit, and "Send Email" or "Resend Email" button based on status

frappe.provide("emails");

emails.SUPPORTED_DOCTYPES = [
    "Quotation",
    "Sales Order",
    "Payment Entry",
    "Purchase Order",
    "Payment Request"
];

emails.check_email_sent = function(frm) {
    // Check if an email was already sent for this document
    return new Promise((resolve) => {
        frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "Communication",
                filters: {
                    reference_doctype: frm.doctype,
                    reference_name: frm.doc.name,
                    communication_medium: "Email",
                    sent_or_received: "Sent"
                }
            },
            async: false,
            callback: function(r) {
                resolve(r.message > 0);
            }
        });
    });
};

emails.setup_send_email_button = function(frm) {
    // Only show for submitted documents
    if (frm.doc.docstatus !== 1) {
        return;
    }

    // Check if this doctype is supported
    if (!emails.SUPPORTED_DOCTYPES.includes(frm.doctype)) {
        return;
    }

    // Remove existing Send/Resend Email buttons first
    frm.remove_custom_button(__("Send Email"));
    frm.remove_custom_button(__("Resend Email"));

    // Check if Resend is enabled and template is configured for this doctype
    frappe.call({
        method: "emails.api.check_doctype_email_enabled",
        args: {
            doctype: frm.doctype
        },
        async: false,
        callback: function(r) {
            if (r.message && r.message.enabled) {
                // Check if email was already sent
                frappe.call({
                    method: "frappe.client.get_count",
                    args: {
                        doctype: "Communication",
                        filters: {
                            reference_doctype: frm.doctype,
                            reference_name: frm.doc.name,
                            communication_medium: "Email",
                            sent_or_received: "Sent"
                        }
                    },
                    async: false,
                    callback: function(count_r) {
                        let email_sent = count_r.message > 0;
                        let button_label = email_sent ? __("Resend Email") : __("Send Email");
                        frm.add_custom_button(button_label, function() {
                            emails.show_send_email_dialog(frm);
                        });
                    }
                });
            }
        }
    });
};

emails.prompt_send_email_after_submit = function(frm) {
    // Check if this doctype is supported
    if (!emails.SUPPORTED_DOCTYPES.includes(frm.doctype)) {
        return;
    }

    // Check if Resend is enabled and template is configured
    frappe.call({
        method: "emails.api.check_doctype_email_enabled",
        args: {
            doctype: frm.doctype
        },
        callback: function(r) {
            if (r.message && r.message.enabled) {
                frappe.confirm(
                    __("Would you like to send an email to the customer?"),
                    function() {
                        // Yes - show send email dialog
                        emails.show_send_email_dialog(frm);
                    },
                    function() {
                        // No - do nothing, button will be available
                    }
                );
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
                // Reload to show new communication in timeline and update button
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
            },
            after_submit: function(frm) {
                emails.prompt_send_email_after_submit(frm);
            }
        });
    });
});
