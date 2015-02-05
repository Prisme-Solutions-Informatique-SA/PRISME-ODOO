from osv import osv

class stock_picking_prisme(osv.osv):
    _inherit = 'stock.picking'
    
    # Method copied from BZR, Revision 4983 to correct the bug of the margin report
    #===========================================================================
    # def action_invoice_create(self, cr, uid, ids, journal_id=False,
    #        group=False, type='out_invoice', context=None):
    #    # need to carify with new requirement
    #    sol_obj = self.pool.get('sale.order.line')
    #    picking_obj = self.pool.get('stock.picking')
    #    invoice_ids = []
    #    res = super(stock_picking_prisme, self).action_invoice_create(cr, uid, ids, journal_id=journal_id, group=group, type=type, context=context)
    #    invoice_ids = res.values()
    #    picking_obj.write(cr, uid, ids, {'invoice_ids': [[6, 0, invoice_ids]]})
    #    for picking in self.browse(cr, uid, ids, context=context):
    #        if picking.type == 'out':
    #            sol_ids = [sol.id for sol in picking.sale_id.order_line]
    #            for inv in picking.invoice_ids:
    #                inv_line_ids = [inv_line.id for inv_line in inv.invoice_line]
    #                sol_obj.cost_price_change(cr, uid, sol_ids, inv_line_ids, context=context)
    #    return res
    #===========================================================================
    
stock_picking_prisme()