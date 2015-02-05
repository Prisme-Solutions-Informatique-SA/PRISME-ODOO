from osv import osv, fields

class account_invoice_prisme(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    _columns = {
                'rounding_on_subtotal': fields.float('Rounding on Subtotal')
    }
account_invoice_prisme()