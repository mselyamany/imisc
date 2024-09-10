// Copyright (c) 2023, Infinity Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('imisc', {
	refresh: function(frm) {
		frm.set_query("default_difference_account", function() {
			return {
				"filters": {
					"account_type": 'Income Account',
					"is_group": 0,
				}
			};
		})

	}
});
