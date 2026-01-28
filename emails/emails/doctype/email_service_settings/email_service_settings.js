// Copyright (c) 2024, Alumicraft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Email Service Settings", {
    refresh: function (frm) {
        // Add button to detect available doctypes
        frm.add_custom_button(__("Detect Available Doctypes"), function () {
            frappe.call({
                method: "emails.emails.doctype.email_service_settings.email_service_settings.get_available_doctypes_for_site",
                callback: function (r) {
                    if (r.message) {
                        show_available_doctypes_dialog(frm, r.message);
                    }
                },
            });
        });

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
    },

    onload: function (frm) {
        // Set up the doctype_name field filter to only show available doctypes
        frm.set_query("doctype_name", "supported_doctypes", function () {
            return {
                filters: {
                    istable: 0,
                    issingle: 0,
                },
            };
        });

        // Set up print_format field filter
        frm.set_query("print_format", "supported_doctypes", function (doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.doctype_name) {
                return {
                    filters: {
                        doc_type: row.doctype_name,
                        disabled: 0,
                    },
                };
            }
            return {};
        });
    },
});

frappe.ui.form.on("Email Doctype Configuration", {
    doctype_name: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.doctype_name) {
            return;
        }

        // Auto-populate defaults when doctype is selected
        frappe.call({
            method: "emails.emails.doctype.email_service_settings.email_service_settings.get_doctype_defaults",
            args: {
                doctype: row.doctype_name,
            },
            callback: function (r) {
                if (r.message) {
                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "recipient_field",
                        r.message.recipient_field || ""
                    );
                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "recipient_doctype",
                        r.message.recipient_doctype || ""
                    );
                    frappe.model.set_value(cdt, cdn, "source_app", r.message.source_app || "");
                }
            },
        });
    },
});

function show_available_doctypes_dialog(frm, doctypes) {
    let html = '<div class="available-doctypes-list">';
    html +=
        "<p>" +
        __("The following doctypes are available for email configuration based on installed apps:") +
        "</p>";
    html += "<table class='table table-bordered'>";
    html +=
        "<thead><tr><th>" +
        __("DocType") +
        "</th><th>" +
        __("App") +
        "</th><th>" +
        __("Category") +
        "</th><th>" +
        __("Status") +
        "</th></tr></thead>";
    html += "<tbody>";

    doctypes.forEach(function (dt) {
        let status = dt.is_configured
            ? '<span class="indicator-pill green">' + __("Configured") + "</span>"
            : '<span class="indicator-pill gray">' + __("Not Configured") + "</span>";

        html +=
            "<tr>" +
            "<td><strong>" +
            dt.doctype +
            "</strong></td>" +
            "<td>" +
            dt.app +
            "</td>" +
            "<td>" +
            dt.category +
            "</td>" +
            "<td>" +
            status +
            "</td>" +
            "</tr>";
    });

    html += "</tbody></table>";

    // Add unconfigured doctypes to the form if requested
    let unconfigured = doctypes.filter((dt) => !dt.is_configured);
    if (unconfigured.length > 0) {
        html +=
            "<p class='text-muted'>" +
            __("Click 'Add All Unconfigured' to add all unconfigured doctypes to the list.") +
            "</p>";
    }

    html += "</div>";

    let dialog = new frappe.ui.Dialog({
        title: __("Available Doctypes"),
        fields: [
            {
                fieldtype: "HTML",
                fieldname: "doctype_list",
                options: html,
            },
        ],
        primary_action_label: unconfigured.length > 0 ? __("Add All Unconfigured") : null,
        primary_action:
            unconfigured.length > 0
                ? function () {
                      add_unconfigured_doctypes(frm, unconfigured);
                      dialog.hide();
                  }
                : null,
    });

    dialog.show();
}

function add_unconfigured_doctypes(frm, doctypes) {
    doctypes.forEach(function (dt) {
        let row = frm.add_child("supported_doctypes");
        row.doctype_name = dt.doctype;
        row.enabled = 1;
        row.recipient_field = dt.default_recipient_field || "";
        row.recipient_doctype = dt.default_recipient_doctype || "";
        row.source_app = dt.app || "";
        row.require_submit = 1;
    });

    frm.refresh_field("supported_doctypes");
    frappe.show_alert(
        {
            message: __("{0} doctypes added to configuration", [doctypes.length]),
            indicator: "green",
        },
        5
    );
}
