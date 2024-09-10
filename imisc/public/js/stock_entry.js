frappe.ui.form.on('Stock Entry', {
	refresh(frm) {
        frappe.db.get_single_value('imisc', 'enable_stock_transfer_with_margin').then(value => {
            if (value) {
                frm.set_query("difference_account", function() {
                    return {
                        "filters": {
                            "account_type": 'Income Account',
                            "is_group": 0,
                            "company": cur_frm.doc.company
                        }
                    };
                });
                frappe.db.get_single_value('imisc', 'default_difference_account').then(value => {
                    if (value && !frm.doc.difference_account) {
                        frm.set_value('difference_account', value);
                    }
                });
                frappe.db.get_single_value('imisc', 'default_margin').then(value => {
                    if (value && !frm.doc.default_margin) {
                        frm.set_value('default_margin', value);
                    }
                })
                frappe.db.get_single_value('imisc', 'default_transfer_price_list').then(value => {
                    if (value && !frm.doc.transfer_price_list) {
                        frm.set_value('transfer_price_list', value);
                    }
                })
            }
        })
	}
})

