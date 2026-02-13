// Copyright (c) 2024, Alumicraft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Email Service Settings", {
    refresh: function (frm) {
        // Add test connection button
        frm.add_custom_button(__("Test Connection"), function () {
            frappe.call({
                method: "emails.api.test_resend_connection",
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __("Connection Successful"),
                            indicator: "green",
                            message: __("Resend API connection is working correctly."),
                        });
                    } else {
                        frappe.msgprint({
                            title: __("Connection Failed"),
                            indicator: "red",
                            message: r.message
                                ? r.message.message
                                : __("Failed to connect to Resend API."),
                        });
                    }
                },
            });
        });

        // Add "Send Test Email" button
        frm.add_custom_button(__("Send Test Email"), function () {
            frm.trigger("send_test_email");
        });

        // Show helper text for footer template
        if (frm.fields_dict.footer_text) {
            frm.fields_dict.footer_text.set_description(
                __("Available variables: {{company}}, {{year}}")
            );
        }
    },

    send_test_email: function (frm) {
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
                        { value: "magic-link", label: __("Magic Link") },
                        { value: "sales-invoice", label: __("Sales Invoice") },
                        { value: "quotation", label: __("Quotation") },
                        { value: "sales-order", label: __("Sales Order") },
                        { value: "purchase-order", label: __("Purchase Order") },
                        { value: "request-for-quotation", label: __("Request for Quotation") },
                        { value: "payment-request", label: __("Payment Request") },
                        { value: "document", label: __("Generic Document") },
                        { value: "password-reset", label: __("Password Reset") },
                        { value: "email-verification", label: __("Email Verification") },
                        { value: "welcome", label: __("Welcome") },
                    ],
                    default: "sales-invoice",
                    reqd: 1,
                },
                {
                    label: __("Send To"),
                    fieldname: "send_to",
                    fieldtype: "Data",
                    default: frappe.session.user_email,
                    read_only: 1,
                },
            ],
            primary_action_label: __("Send"),
            primary_action: function (values) {
                d.hide();
                frappe.call({
                    method: "emails.emails.doctype.email_service_settings.email_service_settings.send_test_email",
                    args: {
                        template: values.template,
                    },
                    freeze: true,
                    freeze_message: __("Sending test email..."),
                    callback: function (r) {
                        if (r.message) {
                            if (r.message.success) {
                                frappe.show_alert({
                                    message: r.message.message,
                                    indicator: "green",
                                });
                            } else {
                                frappe.msgprint({
                                    title: __("Error"),
                                    message: r.message.message,
                                    indicator: "red",
                                });
                            }
                        }
                    },
                });
            },
        });
        d.show();
    },
});
