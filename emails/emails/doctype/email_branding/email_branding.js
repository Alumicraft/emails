// Copyright (c) 2024, Alumicraft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Email Branding", {
    refresh: function(frm) {
        // Add "Send Test Email" button if document is saved
        if (!frm.is_new()) {
            frm.add_custom_button(__("Send Test Email"), function() {
                frm.trigger("send_test_email");
            }, __("Actions"));
        }

        // Show helper text for footer template
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

        frappe.confirm(
            __("Send a test email to {0}?", [frappe.session.user_email]),
            function() {
                frappe.call({
                    method: "emails.emails.doctype.email_branding.email_branding.send_test_email",
                    args: {
                        branding_name: frm.doc.name
                    },
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
        );
    },

    is_default: function(frm) {
        if (frm.doc.is_default) {
            frappe.show_alert({
                message: __("This branding will be used for system emails and as fallback."),
                indicator: "blue"
            });
        }
    }
});
