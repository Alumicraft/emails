// Send Email Button for doctypes with email templates
// Shows popup after submit, and "Send Email" or "Resend Email" button based on status

frappe.provide("emails");

emails.SUPPORTED_DOCTYPES = [
    "Sales Invoice", "Quotation", "Sales Order", "Purchase Order",
    "Request for Quotation", "Payment Request", "Payment Entry"
];

// Cache the enabled check at load time to avoid async calls on every button setup
emails._service_enabled = null;

frappe.call({
    method: "emails.api.check_doctype_email_enabled",
    args: { doctype: "Sales Invoice" },
    callback: function(r) {
        emails._service_enabled = !!(r.message && r.message.enabled);
        console.log("[emails] service enabled:", emails._service_enabled);
    },
    error: function(e) {
        emails._service_enabled = false;
        console.log("[emails] service enabled check FAILED:", e);
    }
});

// Primary: register form handlers for all supported doctypes
// frappe.ui.form.on() just registers in a lookup table — safe to call at load time
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

// Fallback: Client Scripts can overwrite frappe.ui.form.on() handlers.
// This periodic check ensures the button appears even when our refresh handler
// is replaced by another script (e.g. a grid-row-fix Client Script on Payment Request).
setInterval(function() {
    try {
        if (!cur_frm || !cur_frm.doc) return;
        if (cur_frm.doc.docstatus !== 1) return;
        if (emails.SUPPORTED_DOCTYPES.indexOf(cur_frm.doctype) === -1) return;

        // ALWAYS remove ERPNext's button (unconditional)
        if (cur_frm.doctype === "Payment Request") {
            cur_frm.remove_custom_button(__("Resend Payment Email"));
        }

        var hasBtn = !!(cur_frm.custom_buttons[__("Send Email")] ||
            cur_frm.custom_buttons[__("Resend Email")]);

        if (cur_frm.doctype === "Payment Request") {
            console.log("[emails] interval tick — PR docstatus:", cur_frm.doc.docstatus,
                "hasBtn:", hasBtn, "enabled:", emails._service_enabled,
                "buttons:", Object.keys(cur_frm.custom_buttons));
        }

        if (hasBtn) return;

        emails._do_button_setup(cur_frm);
    } catch(e) {
        console.warn("[emails] setInterval error:", e);
    }
}, 2000);

emails.setup_send_email_button = function(frm) {
    // Only show for submitted documents
    if (frm.doc.docstatus !== 1) {
        return;
    }
    emails._do_button_setup(frm);
};

emails._do_button_setup = function(frm) {
    console.log("[emails] _do_button_setup called for", frm.doctype, frm.doc.name,
        "enabled:", emails._service_enabled);

    // Use cached enabled check — don't make an API call
    if (emails._service_enabled === false) {
        console.log("[emails] SKIP: service disabled");
        return;
    }
    if (emails._service_enabled === null) {
        console.log("[emails] SKIP: service still loading");
        return;
    }

    // Remove existing buttons
    frm.remove_custom_button(__("Send Email"));
    frm.remove_custom_button(__("Resend Email"));
    if (frm.doctype === "Payment Request") {
        frm.remove_custom_button(__("Resend Payment Email"));
    }

    // Hide standard email button
    emails.hide_standard_email_button(frm);

    // Add button SYNCHRONOUSLY — don't gate on async call
    frm.add_custom_button(__("Send Email"), function() {
        emails.show_send_email_dialog(frm);
    });

    var btnAdded = !!frm.custom_buttons[__("Send Email")];
    console.log("[emails] add_custom_button result — in custom_buttons:", btnAdded,
        "buttons after:", Object.keys(frm.custom_buttons));

    if (btnAdded) {
        frm.custom_buttons[__("Send Email")]
            .removeClass("btn-default")
            .addClass("btn-primary-light");
    }

    // Async: update label to "Resend" if email was already sent
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
        callback: function(count_r) {
            console.log("[emails] get_count result:", count_r.message);
            if (count_r.message > 0 && frm.custom_buttons[__("Send Email")]) {
                frm.remove_custom_button(__("Send Email"));
                frm.add_custom_button(__("Resend Email"), function() {
                    emails.show_send_email_dialog(frm);
                });
            }
        },
        error: function(e) {
            console.warn("[emails] get_count FAILED:", e);
        }
    });
};

emails.hide_standard_email_button = function(frm) {
    // Hide the standard "+ New Email" button in the activity/timeline section
    setTimeout(function() {
        frm.$wrapper.find('.timeline-actions .btn-new-email, .comment-box .btn-new-email, .new-btn .btn-comment-email').hide();
        frm.$wrapper.find('.reply-link, .reply-email-link').hide();
        // Also hide the "New Email" action in the activity section
        frm.$wrapper.find('.activity-actions .btn[data-action="new_email"]').hide();
        frm.$wrapper.find('.timeline-item .action-btn[title="Reply"]').hide();
        // Hide "+ New Email" button in timeline action-buttons
        frm.$wrapper.find('.action-buttons .action-btn').filter(function() {
            return $(this).text().trim().indexOf("New Email") !== -1;
        }).hide();
    }, 500);
};

emails.prompt_send_email_after_submit = function(frm) {
    // Check if Resend is enabled and template is configured
    frappe.call({
        method: "emails.api.check_doctype_email_enabled",
        args: {
            doctype: frm.doctype
        },
        callback: function(r) {
            if (r.message && r.message.enabled) {
                frappe.confirm(
                    __("Would you like to send an email?"),
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
                title: __("Send Email"),
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
                        fieldname: "bcc",
                        fieldtype: "Data",
                        label: __("BCC"),
                        options: "Email"
                    },
                    {
                        fieldname: "custom_message",
                        fieldtype: "Small Text",
                        label: __("Custom Message")
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
            bcc: values.bcc,
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
