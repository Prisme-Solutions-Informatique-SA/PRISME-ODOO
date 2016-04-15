from openerp.osv import osv, fields


class SaleOrder(osv.Model):
	_inherit = "sale.order"
	_columns = {
		'currency_id': fields.related('pricelist_id', 'currency_id', relation='res.currency', type='many2one', string='Currency', help='field'),
	}