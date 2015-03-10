from openerp.osv import fields, osv, expression

class account_invoice_prisme(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    _columns = {
                'rounding_on_subtotal': fields.float('Rounding on Subtotal')
    }
    
    _defaults = {
        'rounding_on_subtotal': lambda *a: 0.01,
    }
    
account_invoice_prisme()
