from osv import osv, fields

class blanket_line_prisme(osv.osv):
    _name = 'blanket.line.prisme'
    _columns = {
                'name': fields.char('Title', size=64, required=True, translate=True),
                'delivery_date': fields.date('Delevriy date'),
                'quantity': fields.integer('quantitiy'),
                'stock_picking_id': fields.many2one('stock.picking', 'stock picking', readonly=True),
                'purchase_order_line_id': fields.many2one('purchase.order.line', 'purchase order id', readonly=True),
                }
blanket_line_prisme()

class purchase_order_line_prisme(osv.osv):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    _columns = {
               'blanket_line_prisme_ids': fields.one2many('blanket.line.prisme', 'purchase_order_line_id', 'blanket line'),
               }
purchase_order_line_prisme()

