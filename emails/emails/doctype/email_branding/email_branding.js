// Copyright (c) 2024, Alumicraft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Email Branding", {
    refresh: function(frm) {
        // Add "Send Test Email" button
        frm.add_custom_button(__("Send Test Email"), function() {
            frm.trigger("send_test_email");
        }, __("Actions"));

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

        // Show dialog with template selection
        let d = new frappe.ui.Dialog({
            title: __("Send Test Email"),
            fields: [
                {
                    label: __("Email Template"),
                    fieldname: "template",
                    fieldtype: "Select",
                    options: [
                        {"value": "magic-link", "label": __("Magic Link")},
                        {"value": "document", "label": __("Document")},
                        {"value": "notification", "label": __("Notification")},
                        {"value": "auth", "label": __("Authentication")}
                    ],
                    default: "magic-link",
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
                    method: "emails.emails.doctype.email_branding.email_branding.send_test_email",
                    args: {
                        template: values.template
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
        });
        d.show();
    }
});
