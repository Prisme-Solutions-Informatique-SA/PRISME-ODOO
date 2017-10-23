from openerp.osv import fields, osv, expression
from openerp import netsvc
import openerp.addons.decimal_precision as dp

class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    
    def product_id_change(self, cr, uid, ids, product_id, uom, qty=0, name='', \
                          type='out_invoice', partner_id=False, \
                          fposition_id=False, \
                          price_unit=False, address_invoice_id=False, \
                          currency_id=False, context=None):
        res = super(account_invoice_line, self).product_id_change(cr, \
                    uid, ids, product_id, uom, qty, name, type, partner_id, \
                    fposition_id, price_unit, address_invoice_id, currency_id, \
                    context=context)
        if type == 'out_invoice' or type == 'in_invoice':
            if product_id:
                product = self.pool.get('product.product').browse(cr, uid,
                                            product_id, context=context)
                if product.analytic_distribution:
                    res['value'].update({'analytics_id': 
                                         product.analytic_distribution.id})
            else:
                res['value'].update({'analytics_id': False})
        return res

account_invoice_line()
