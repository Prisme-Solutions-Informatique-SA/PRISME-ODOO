from osv import osv

class account_invoice_line_prisme(osv.osv):
    _inherit = "account.invoice.line"
    
    # Method copied from BZR, Revision 4983 to correct the bug of the margin report
    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('cost_price', False):
            if vals.get('product_id', False):
                res = self.pool.get('product.product').read(cr, uid, [vals['product_id']], ['standard_price'])
                vals['cost_price'] = res[0]['standard_price']
        return super(account_invoice_line_prisme, self).write(cr, uid, ids, vals, context)

    # Method copied from BZR, Revision 4983 to correct the bug of the margin report
    def create(self, cr, uid, vals, context=None):
        if not vals.get('cost_price', False):
            if vals.get('product_id',False):
                res = self.pool.get('product.product').read(cr, uid, [vals['product_id']], ['standard_price'])
                vals['cost_price'] = res[0]['standard_price']
        return super(account_invoice_line_prisme, self).create(cr, uid, vals, context)
    
account_invoice_line_prisme()