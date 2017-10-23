from openerp.osv import fields, osv, expression
from openerp import netsvc

class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cr, \
                    uid, ids, journal_id=journal_id, group=group, type=type,
                    context=context)
        
        obj_invoice = self.pool.get('account.invoice')
        obj_line = self.pool.get('account.invoice.line')

        for picking_id, invoice_id in res.items():
            invoice = obj_invoice.browse(cr, uid, invoice_id)
            if invoice.type == 'out_invoice' or invoice.type == 'in_invoice':
                for line in invoice.invoice_line:
                    product = line.product_id
                    if product:
                        if product.analytic_distribution:
                            obj_line.write(cr, uid, line.id, \
                                {'analytics_id': \
                                 product.analytic_distribution.id})
                
        return res

stock_picking()
