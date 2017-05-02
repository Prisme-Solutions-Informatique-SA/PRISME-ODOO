from odoo import api, fields, models, _


class Stock_move(models.Model):
	_name = "stock.move"
	_inherit = "stock.move"
	
	product_final_id = fields.Many2one(related='raw_material_production_id.product_id', relation='product.product',  string='Product')
	date_planned = fields.Datetime(related='raw_material_production_id.date_planned_start', string='Scheduled Date')
	product_qty_final = fields.Float(related='raw_material_production_id.product_qty', string='Product Quantity')
	product_uom_final = fields.Many2one(related='raw_material_production_id.product_uom_id', relation='product.uom',  string='Product Unit of Measure')
