// Email form handler — loaded per-doctype via doctype_js hook
// Registers refresh and after_submit handlers for the Send Email button

frappe.ui.form.on(cur_frm.doctype, {
    refresh: function(frm) {
        emails.setup_send_email_button(frm);
    },
    after_submit: function(frm) {
        emails.prompt_send_email_after_submit(frm);
    }
});
