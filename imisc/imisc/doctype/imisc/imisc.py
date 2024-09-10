# Copyright (c) 2023, Infinity Systems and contributors
# For license information, please see license.txt

from erpnext.accounts.utils import get_balance_on
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from frappe.model.document import Document
from frappe.utils.data import flt

class imisc(Document):
	def validate(self):
		if self.enable_stock_transfer_with_margin:
			make_stock_entry_with_margin_fields()
		else:
			make_stock_entry_with_margin_fields(remove = True)

		if self.enable_customer_balance_in_sales_invoice:	
			if not frappe.db.exists("Custom Field", {"fieldname": "current_customer_balance", "dt": 'Sales Invoice'}):
				df = dict(
					fieldname="current_customer_balance",
					label="Current Customer Balance",
					fieldtype="Currency",
					read_only=1,
					insert_after="customer",
				)
				create_custom_field('Sales Invoice', df)
				frappe.msgprint('Custom Field current_customer_balance Created Successfully.', alert = 1)
			if not frappe.db.exists("Custom Field", {"fieldname": "customer_balance_after_invoice", "dt": 'Sales Invoice'}):
				df = dict(
					fieldname="customer_balance_after_invoice",
					label="Customer Balance After Invoice",
					fieldtype="Currency",
					read_only=1,
					insert_after="current_customer_balance",
				)
				create_custom_field('Sales Invoice', df)
				frappe.msgprint('Custom Field customer_balance_after_invoice Created Successfully.', alert = 1)

def make_stock_entry_with_margin_fields(remove = False):
	'''Add or remove fields for Stock Entry'''
	if not remove:
		if not frappe.db.exists("Custom Field", {"fieldname": "with_margin", "dt": 'Stock Entry'}):
			df = dict(
				fieldname="with_margin",
				label="Transfer With Margin",
				fieldtype="Check",
				read_only=0,
				print_hide=0,
				insert_after="purchase_receipt_no",
				depends_on="eval:doc.purpose=='Material Transfer'",
			)
			create_custom_field('Stock Entry', df)
			frappe.msgprint('Custom Field with_margin Created Successfully.', alert = 1)
		
		if not frappe.db.exists("Custom Field", {"fieldname": "difference_account", "dt": 'Stock Entry'}):
			df = dict(
				fieldname="difference_account",
				label="Difference Account",
				fieldtype="Link",
				options="Account",
				read_only=0,
				print_hide=0,
				insert_after="with_margin",
				depends_on="eval:doc.with_margin==1",
				mandatory_depends_on="eval:doc.with_margin==1"
			)
			create_custom_field('Stock Entry', df)
			frappe.msgprint('Custom Field difference_account Created Successfully.', alert = 1)

		if not frappe.db.exists("Custom Field", {"fieldname": "margin_type", "dt": 'Stock Entry'}):
			df = dict(
				fieldname="margin_type",
				label="Margin Type",
				fieldtype="Select",
				#valu of options can't be a list
				#options=["Percentage", "Price List"],
				options="Percentage\nPrice List",
				default="Percentage",
				read_only=0,
				print_hide=0,
				insert_after="difference_account",
				depends_on="eval:doc.with_margin==1",
				mandatory_depends_on="eval:doc.with_margin==1"
			)
			create_custom_field('Stock Entry', df)
			frappe.msgprint('Custom Field margin_type Created Successfully.', alert = 1)

		if not frappe.db.exists("Custom Field", {"fieldname": "default_margin", "dt": 'Stock Entry'}):
			df = dict(
				fieldname="default_margin",
				label="Default Margin",
				fieldtype="Percent",
				read_only=0,
				print_hide=0,
				insert_after="margin_type",
				depends_on="eval:doc.margin_type=='Percentage' && doc.with_margin==1",
				mandatory_depends_on="eval:doc.margin_type=='Percentage' && doc.with_margin==1"
			)
			create_custom_field('Stock Entry', df)
			frappe.msgprint('Custom Field default_margin Created Successfully.', alert = 1)
		
		if not frappe.db.exists("Custom Field", {"fieldname": "transfer_price_list", "dt": 'Stock Entry'}):
			df = dict(
				fieldname="transfer_price_list",
				label="Transfer Price List",
				fieldtype="Link",
				options="Price List",
				read_only=0,
				print_hide=0,
				insert_after="margin_type",
				depends_on="eval:doc.margin_type=='Price List' && doc.with_margin==1",
				mandatory_depends_on="eval:doc.margin_type=='Price List' && doc.with_margin==1"
			)
			create_custom_field('Stock Entry', df)
			frappe.msgprint('Custom Field transfer_price_list Created Successfully.', alert = 1)

		if not frappe.db.exists("Custom Field", {"fieldname": "margin", "dt": 'Stock Entry Detail'}):
			df = dict(
				fieldname="margin",
				label="Transfer Margin",
				fieldtype="Percent",
				read_only=0,
				print_hide=0,
				insert_after="basic_rate",
				default=0,
			)
			create_custom_field('Stock Entry Detail', df)
			frappe.msgprint('Custom Field margin Created Successfully.', alert = 1)
	else:
		if frappe.db.exists("Custom Field", {"fieldname": "with_margin", "dt": 'Stock Entry'}):
			d = frappe.get_doc("Custom Field", {"fieldname": "with_margin", "dt": 'Stock Entry'})
			d.delete()
			frappe.msgprint('Custom Field with_margin Removed Successfully.', alert = 1)
		
		if frappe.db.exists("Custom Field", {"fieldname": "difference_account", "dt": 'Stock Entry'}):
			d = frappe.get_doc("Custom Field", {"fieldname": "difference_account", "dt": 'Stock Entry'})
			d.delete()
			frappe.msgprint('Custom Field difference_account Deleted Successfully.', alert = 1)

		if frappe.db.exists("Custom Field", {"fieldname": "margin_type", "dt": 'Stock Entry'}):
			d = frappe.get_doc("Custom Field", {"fieldname": "margin_type", "dt": 'Stock Entry'})
			d.delete()
			frappe.msgprint('Custom Field margin_type Deleted Successfully.', alert = 1)

		if frappe.db.exists("Custom Field", {"fieldname": "default_margin", "dt": 'Stock Entry'}):
			d = frappe.get_doc("Custom Field", {"fieldname": "default_margin", "dt": 'Stock Entry'})
			d.delete()			
			frappe.msgprint('Custom Field default_margin Deleted Successfully.', alert = 1)
		
		if frappe.db.exists("Custom Field", {"fieldname": "transfer_price_list", "dt": 'Stock Entry'}):
			d = frappe.get_doc("Custom Field", {"fieldname": "transfer_price_list", "dt": 'Stock Entry'})
			d.delete()
			frappe.msgprint('Custom Field transfer_price_list Deleted Successfully.', alert = 1)

		if frappe.db.exists("Custom Field", {"fieldname": "margin", "dt": 'Stock Entry Detail'}):
			d = frappe.get_doc("Custom Field", {"fieldname": "margin", "dt": 'Stock Entry Detail'})
			d.delete()
			frappe.msgprint('Custom Field margin Deleted Successfully.', alert = 1)


@frappe.whitelist()
def get_customer_balance(customer, date, company):
	return get_balance_on(party_type='Customer', party=customer, date=date, company=company)

@frappe.whitelist()
def sales_invoice_validate(doc, method):
	if frappe.db.get_single_value('imisc', 'enable_customer_balance_in_sales_invoice'):
			doc.customer_balance_after_invoice = flt(doc.get('current_customer_balance')) + flt(doc.get('net_total'))