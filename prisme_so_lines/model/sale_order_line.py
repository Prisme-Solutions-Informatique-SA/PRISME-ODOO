from openerp.osv import osv, fields


class SaleOrderLine(osv.Model):
	_inherit = "sale.order.line"
	_columns = {
		'currency_id': fields.related('order_id', 'currency_id', relation='res.currency', type='many2one', string='Currency', help='field'),
	}
