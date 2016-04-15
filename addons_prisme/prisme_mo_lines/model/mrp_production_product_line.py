from openerp.osv import osv, fields


class MRPProductionProductLine(osv.Model):
	_inherit = "mrp.production.product.line"
	_columns = {
		'product_final_id': fields.related('production_id', 'product_id', relation='product.product', type='many2one', string='Product'),	
		'date_planned': fields.related('production_id', 'date_planned', type='datetime', string='Scheduled Date'),
		'product_qty_final': fields.related('production_id', 'product_qty', type='float', string='Product Quantity'),
		'product_uom_final': fields.related('production_id', 'product_uom', relation='product.uom', type='many2one', string='Product Unit of Measure'),
	}