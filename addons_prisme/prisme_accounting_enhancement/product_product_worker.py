from openerp.osv import fields, osv, expression

class product_product_prisme(osv.osv):
    _name = "product.template" 
    _inherit = "product.template"
    
    _columns = {
                "sale_analytic_account_id": fields.many2one("account.analytic.account", 
                                                string="Sale Analytic Account")
    }

product_product_prisme()