// Send Email Button for doctypes with email templates
// Shows "Send Email" or "Resend Email" button on submitted documents
// v4 — monkey-patches add_custom_button to prevent ERPNext's "Resend Payment Email" flicker

frappe.provide("emails");

emails.SUPPORTED_DOCTYPES = [
    "Sales Invoice", "Quotation", "Sales Order", "Purchase Order",
    "Request for Quotation", "Payment Request", "Payment Entry"
];

emails._safe_remove_button = function(frm, label) {
    if (frm.custom_buttons[__(label)]) {
        frm.remove_custom_button(__(label));
    }
};

// Check if our button is actually visible in the DOM (not just a stale reference)
emails._has_button_in_dom = function(frm) {
    var sendBtn = frm.custom_buttons[__("Send Email")];
    var resendBtn = frm.custom_buttons[__("Resend Email")];
    var sendInDom = sendBtn && sendBtn.length && $.contains(document.documentElement, sendBtn[0]);
    var resendInDom = resendBtn && resendBtn.length && $.contains(document.documentElement, resendBtn[0]);
    return sendInDom || resendInDom;
};

// Register form handlers for all supported doctypes
// frappe.ui.form.on() just registers in a lookup table — safe to call at load time
emails.SUPPORTED_DOCTYPES.forEach(function(doctype) {
    var handlers = {
        refresh: function(frm) {
            emails.setup_send_email_button(frm);
        },
        after_submit: function(frm) {
            // Payment Request auto-sends on submit via the override — skip prompt to avoid double-send
            if (frm.doctype === "Payment Request") return;
            emails.prompt_send_email_after_submit(frm);
        }
    };

    // For Payment Request, use setup to monkey-patch add_custom_button BEFORE
    // ERPNext's refresh handler runs — prevents "Resend Payment Email" from ever
    // being created, eliminating flicker.
    if (doctype === "Payment Request") {
        handlers.setup = function(frm) {
            var _original_add_button = frm.add_custom_button.bind(frm);
            frm.add_custom_button = function(label) {
                if (label === __("Resend Payment Email")) {
                    return $();  // silently block, return empty jQuery object
                }
                return _original_add_button.apply(frm, arguments);
            };
        };
    }

    frappe.ui.form.on(doctype, handlers);
});

// Fallback: ERPNext's Payment Request refresh handler (or Client Scripts) can remove
// our buttons after our refresh handler runs. This periodic check verifies the button
// is actually in the DOM (not just a stale jQuery ref in custom_buttons) and re-adds it.
setInterval(function() {
    try {
        if (!cur_frm || !cur_frm.doc) return;
        if (cur_frm.doc.docstatus !== 1) return;
        if (emails.SUPPORTED_DOCTYPES.indexOf(cur_frm.doctype) === -1) return;

        if (emails._has_button_in_dom(cur_frm)) return;

        // Clean up stale references before re-adding
        delete cur_frm.custom_buttons[__("Send Email")];
        delete cur_frm.custom_buttons[__("Resend Email")];

        emails._do_button_setup(cur_frm);
    } catch(e) {
        console.warn("emails: setInterval fallback error", e);
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
    // Remove existing buttons (safe — no-op if button doesn't exist)
    emails._safe_remove_button(frm, "Send Email");
    emails._safe_remove_button(frm, "Resend Email");

    // Hide standard email button
    emails.hide_standard_email_button(frm);

    // Add button synchronously — server validates on send
    frm.add_custom_button(__("Send Email"), function() {
        emails.show_send_email_dialog(frm);
    });

    var btn = frm.custom_buttons[__("Send Email")];
    if (btn) {
        btn.removeClass("btn-default").addClass("btn-primary");
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
            if (count_r.message > 0 && frm.custom_buttons[__("Send Email")]) {
                frm.remove_custom_button(__("Send Email"));
                frm.add_custom_button(__("Resend Email"), function() {
                    emails.show_send_email_dialog(frm);
                });
            }
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

// Email Service Settings — test buttons
// Registered here (app_include_js) instead of doctype_js for reliable loading
frappe.ui.form.on("Email Service Settings", {
    refresh: function(frm) {
        frm.add_custom_button(__("Test Connection"), function() {
            frappe.call({
                method: "emails.api.test_resend_connection",
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __("Connection Successful"),
                            indicator: "green",
                            message: __("Resend API connection is working correctly.")
                        });
                    } else {
                        frappe.msgprint({
                            title: __("Connection Failed"),
                            indicator: "red",
                            message: r.message ? r.message.message : __("Failed to connect to Resend API.")
                        });
                    }
                }
            });
        });

        frm.add_custom_button(__("Send Test Email"), function() {
            frm.trigger("send_test_email");
        });

        if (frm.fields_dict.footer_text) {
            frm.fields_dict.footer_text.set_description(
                __("Available variables: {{company}}, {{year}}")
            );
        }
    },

    send_test_email: function(frm) {
        if (frm.is_dirty()) {
            frappe.msgprint(__("Please save the document before sending a test email."));
            return;
        }

        let d = new frappe.ui.Dialog({
            title: __("Send Test Email"),
            fields: [
                {
                    label: __("Email Template"),
                    fieldname: "template",
                    fieldtype: "Select",
                    options: [
                        { value: "sales-invoice", label: __("Sales Invoice") },
                        { value: "quotation", label: __("Quotation") },
                        { value: "sales-order", label: __("Sales Order") },
                        { value: "purchase-order", label: __("Purchase Order") },
                        { value: "request-for-quotation", label: __("Request for Quotation") },
                        { value: "payment-request", label: __("Payment Request") },
                        { value: "payment-entry", label: __("Payment Entry") },
                        { value: "document", label: __("Generic Document") },
                        { value: "ach-payment-failure", label: __("ACH Payment Failure") },
                        { value: "ach-payment-success", label: __("ACH Payment Success") },
                        { value: "ach-payment-upcoming", label: __("ACH Payment Upcoming") },
                        { value: "autopay-setup", label: __("Autopay Setup") },
                        { value: "autopay-update", label: __("Autopay Update") },
                        { value: "dealer-agreement-sent", label: __("Dealer Agreement Sent") },
                        { value: "dealer-agreement-signed", label: __("Dealer Agreement Signed") },
                        { value: "dealer-welcome", label: __("Dealer Welcome") },
                        { value: "factory-loa-received", label: __("Factory LOA Received") },
                        { value: "flooring-packet-sent", label: __("Flooring Packet Sent") },
                        { value: "flooring-packet-signed", label: __("Flooring Packet Signed") },
                        { value: "loan-disbursed", label: __("Loan Disbursed") },
                        { value: "retailer-application", label: __("Retailer Application") },
                        { value: "magic-link", label: __("Magic Link") },
                        { value: "password-reset", label: __("Password Reset") },
                        { value: "email-verification", label: __("Email Verification") },
                        { value: "welcome", label: __("Welcome") }
                    ],
                    default: "sales-invoice",
                    reqd: 1
                },
                {
                    label: __("Send To"),
                    fieldname: "send_to",
                    fieldtype: "Data",
                    default: frappe.session.user_email,
                    read_only: 1
                }
            ],
            primary_action_label: __("Send"),
            primary_action: function(values) {
                d.hide();
                frappe.call({
                    method: "emails.emails.doctype.email_service_settings.email_service_settings.send_test_email",
                    args: { template: values.template },
                    freeze: true,
                    freeze_message: __("Sending test email..."),
                    callback: function(r) {
                        if (r.message) {
                            if (r.message.success) {
                                frappe.show_alert({
                                    message: r.message.message,
                                    indicator: "green"
                                });
                            } else {
                                frappe.msgprint({
                                    title: __("Error"),
                                    message: r.message.message,
                                    indicator: "red"
                                });
                            }
                        }
                    }
                });
            }
        });
        d.show();
    }
});

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
