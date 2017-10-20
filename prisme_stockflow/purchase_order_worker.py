from osv import fields, osv

class purchase_order_worker(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

#    def action_picking_create(self, cr, uid, ids, *args):
#        result = super(purchase_order_worker, self).action_picking_create(cr, \
#                                                            uid, ids, args)
#        picking = self.pool.get('stock.picking').browse(cr, uid, result)
#        for stock_move in picking.move_lines:
#            move_product = stock_move.product_id
#            if move_product.storage_location:
#                self.pool.get('stock.move').write(cr, uid, [stock_move.id], \
#                        {'location_dest_id': move_product.storage_location.id})
#        return result
        
purchase_order_worker()
