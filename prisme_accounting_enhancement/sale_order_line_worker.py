from openerp import netsvc
from openerp.osv import fields, osv, expression


class sale_order_line_prisme(osv.osv):
    _name = 'sale.order.line' 
    _inherit = 'sale.order.line'

    def _calc_line_base_price(self, cr, uid, line, context=None):
        if line.discount_type == 'amount':
            price = line.price_unit - (line.discount or 0.0)
        elif line.discount_type == 'percent':
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        else:
            price = line.price_unit
        return price * (1 - (line.discount or 0.0) / 100.0)
    
    def invoice_line_create(self, cr, uid, ids, context=None):
        res = super(sale_order_line_prisme, self).invoice_line_create(cr,\
                    uid, ids, context)
            
        # Discount type recovery
        obj_inv_line = self.pool.get('account.invoice.line')
        for so_line in self.browse(cr, uid, ids, context=context):
            for inv_line in so_line.invoice_lines:
                obj_inv_line.write(cr, uid, inv_line.id,\
                                   {'discount_type': so_line.discount_type})
        
        return res

sale_order_line_prisme()