frappe.ui.form.on('Sales Invoice', {
    onload: function(frm){
		if(frm.doc.customer && frm.doc.docstatus == 0){
			frappe.db.get_single_value('imisc', 'enable_customer_balance_in_sales_invoice').then(value => {
				if (value) {
					let field_name = $('[data-fieldname="current_customer_balance"] .control-value')
					field_name.css({
						'color': 'red',
						'font-weight': 'bold',
						'background-color' : 'azure'
					});
					field_name = $('[data-fieldname="customer_balance_after_invoice"] .control-value')
					field_name.css({
						'color': 'red',
						'font-weight': 'bold',
						'background-color' : 'yellow'
					});
					if (frm.doc.docstatus == 0 && (!frm.doc.current_customer_balance || frm.doc.current_customer_balance == 0) && frm.doc.customer){
						frm.trigger('customer')
					}
				}
			})
		}	
    },
    cost_center: function(frm){
        frappe.db.get_single_value('imisc', 'enable_sales_invoice_cost_center_propagation').then(value => {
            if (value && frm.doc.cost_center) {
                frm.doc.items.forEach(function(row){
                    frappe.model.set_value(row.doctype, row.name, 'cost_center', frm.doc.cost_center)
                })    
            }
        })
    },
    customer: function(frm){
		frappe.db.get_single_value('imisc', 'enable_customer_balance_in_sales_invoice').then(value => {
            if (value) {
				if (frm.doc.docstatus == 0 && frm.doc.customer) {
					frappe.call({
						method: "imisc.imisc.doctype.imisc.imisc.get_customer_balance",
						args: {
							customer: frm.doc.customer,
							date: frm.doc.posting_date,
							company: frm.doc.company
						},
						callback: function(res){
							if (res && res.message){
								frm.set_value('current_customer_balance', res.message);
								let field_name = $('[data-fieldname="current_customer_balance"] .control-value')
								field_name.css({
									'color': 'red',
									'font-weight': 'bold',
									'background-color' : 'azure'
								});
							}
						}
					});
				}
			}
		})
	},
	customer_balance_after_invoice: function(frm){
	},
    
})


frappe.ui.form.on('Sales Invoice Item', {
    items_add: function(frm, cdt, cdn){
        frappe.db.get_single_value('imisc', 'enable_sales_invoice_cost_center_propagation').then(value => {
            if (value && frm.doc.cost_center) {
                let row = locals[cdt][cdn]
                frappe.model.set_value(row.doctype, row.name, 'cost_center', frm.doc.cost_center)
            }
        })
    }
})
