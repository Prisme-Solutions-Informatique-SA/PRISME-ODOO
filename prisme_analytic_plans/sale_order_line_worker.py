from openerp.osv import fields, osv, expression
from openerp import netsvc
class sale_order_line(osv.osv):
    _name = 'sale.order.line' 
    _inherit = 'sale.order.line'
    
    # TODO Adapt
    def invoice_line_create(self, cr, uid, ids, context=None):
        res = super(sale_order_line, self).invoice_line_create(cr,\
                    uid, ids, context)
        obj_inv_line = self.pool.get('account.invoice.line')
        for line in obj_inv_line.browse(cr, uid, res):
            product = line.product_id
            if product:
                if product.analytic_distribution:
                    obj_inv_line.write(cr, uid, line.id,\
                        {'analytics_id': product.analytic_distribution.id})
        
        return res

sale_order_line()