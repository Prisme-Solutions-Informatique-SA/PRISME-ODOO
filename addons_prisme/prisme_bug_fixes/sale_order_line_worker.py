from osv import osv

class sale_order_line_prisme(osv.osv):
    _inherit = "sale.order.line"

    # Method copied from BZR, Revision 4983 to correct the bug of the margin report
    def cost_price_change(self, cr, uid, sol_ids, inv_line_ids, context=None):
        """ Changes cost price on invoice line if it is changed on sale order line. """
        inv_line_obj = self.pool.get('account.invoice.line')
        for sol in self.browse(cr, uid, sol_ids, context=context):
            if sol.product_id.standard_price != sol.purchase_price:
                for inv_line in inv_line_obj.browse(cr, uid, inv_line_ids, context=context):
                    if inv_line.product_id.id == sol.product_id.id:
                        inv_line_obj.write(cr, uid, [inv_line.id], {'cost_price': sol.purchase_price})
        return True
    
    # Method copied from BZR, Revision 4983 to correct the bug of the margin report
    def invoice_line_create(self, cr, uid, ids, context=None):
        inv_line_ids = super(sale_order_line_prisme, self).invoice_line_create(cr, uid, ids, context=context)
        self.cost_price_change(cr, uid, ids, inv_line_ids, context=context)
        return inv_line_ids
    
sale_order_line_prisme()