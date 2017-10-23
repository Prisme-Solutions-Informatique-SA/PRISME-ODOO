from openerp.osv import fields, osv, expression

class product_product(osv.osv):
    _name = 'product.product' 
    _inherit = 'product.product'
    
    _columns = {
                'analytic_distribution': fields.many2one(
                    'account.analytic.plan.instance', 
                    string='Analytic Distribution',    help='Analytic ' +\
                    'distribution used to purchase and sale this product')
    }

product_product()