from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.stock.get_item_details import get_price_list_rate_for, get_item_details
import frappe
from frappe import _
import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)

from frappe.utils import (
	DATE_FORMAT,
	add_days,
	add_to_date,
	cint,
	comma_and,
	date_diff,
	flt,
	get_link_to_form,
	getdate,
)

class IStockEntry(StockEntry):
	def get_margin(self, item):
		if self.with_margin and self.purpose == 'Material Transfer':
			if self.margin_type == "Percentage":
				if item.margin and item.margin > 0 and item.margin != self.default_margin:
					return item.margin
				else:
					return self.default_margin
			elif self.margin_type == "Price List":
				price_list = self.transfer_price_list
				#item_pl_rate = frappe.db.get_value("Item Price", {"item_code": item.item_code, "price_list": price_list}, "price_list_rate")
				item_pl_rate = flt(get_item_price(item.item_code, price_list, item.uom, self.posting_date, item.qty, item.conversion_factor, self))
				if not item_pl_rate:
					frappe.throw(_("Price List Rate not found for Item {0} in Price List {1}").format(item.item_code, price_list))
				else:
					diff = item_pl_rate - item.basic_rate
					return (diff * 100) / item.basic_rate
	def distribute_additional_costs(self):
		
		# If no incoming items, set additional costs blank
		if not any(d.item_code for d in self.items if d.t_warehouse):
			self.additional_costs = []

		self.total_additional_costs = sum(flt(t.base_amount) for t in self.get("additional_costs"))

		if self.purpose in ("Repack", "Manufacture"):
			incoming_items_cost = sum(flt(t.basic_amount) for t in self.get("items") if t.is_finished_item)
		else:
			incoming_items_cost = sum(flt(t.basic_amount) for t in self.get("items") if t.t_warehouse)

		if not incoming_items_cost:
			return

		for d in self.get("items"):
			if self.purpose in ("Repack", "Manufacture") and not d.is_finished_item:
				d.additional_cost = 0
				continue
			elif not d.t_warehouse:
				d.additional_cost = 0
				continue
			d.additional_cost = (flt(d.basic_amount) / incoming_items_cost) * self.total_additional_costs
			if self.purpose == 'Material Transfer' and self.with_margin == 1:
				margin = self.get_margin(d)
				d.margin = margin
				margin = flt(1 + (margin / 100))
				stock_uom_qty = flt(flt(d.qty) * flt(d.conversion_factor))
				
				d.additional_cost = flt(((d.basic_rate * margin) - d.basic_rate) * stock_uom_qty)

				if self.difference_account:
					d.expense_account = self.difference_account


def get_item_price(item_code, price_list, uom, transaction_date, qty, conversion_factor, doc):
	frappe.msgprint(_("Start Getting Item Price for Item {0} from Price List {1}!").format(item_code, price_list), alert=True)
	price = None
	args = {
    	"item_code":item_code,
    	"currency":frappe.db.get_value("Company", doc.company, "default_currency"),
    	"update_stock":0,
    	"conversion_rate":1,
    	"price_list":price_list,
    	"price_list_currency":frappe.db.get_value("Price List", price_list, "currency"),
    	"plc_conversion_rate":1,
    	"company":doc.company,
    	"ignore_pricing_rule":0,
    	"doctype":"Sales Invoice",
    	"qty":qty,
    	"stock_uom":frappe.db.get_value("Item", item_code, "stock_uom"),
    	"uom": frappe.db.get_value("Item", item_code, "stock_uom"),
    }

	# try to get stock_uom price
	price = get_item_details(args).get("price_list_rate")

	if price :
		frappe.msgprint(_("Stock UOM Rate found for Item {0} from Price List {1}!").format(item_code, price_list), alert=True)
		return price
	else:
		# try to get the line uom price
		args['uom'] = uom
		id = get_item_details(args)
		price = id.get("price_list_rate")
		cf= id.get("conversion_factor")
		if price :
			frappe.msgprint(_("Line UOM Rate found for Item {0} from Price List {1}! price {2} -- {3}").format(item_code, price_list, price, cf), alert=True)
			return flt(price / cf)
		else:
			sql = """
				select distinct uom from `tabItem Price` where item_code = '{0}' and price_list = '{1}' 	
			""".format(item_code, price_list)
			uoms = frappe.db.sql(sql, as_dict=True)
			if uoms:
				for u in uoms:
					args['uom']= u.uom
					price = get_item_details(args).get("price_list_rate")
					cf = get_item_details(args).get("conversion_factor")
					if price:
						frappe.msgprint(_("UOM Rate found for Item {0} from Price List {1}! with CV {2} with UOM {3}").format(item_code, price_list, cf, u.uom), alert=True)
						return flt(price / cf)
			else:
				frappe.throw(_("Can't find or calculate the Stock UOM Rate for Item {0} from Price List {1}!").format(item_code, price_list))
				return 0
