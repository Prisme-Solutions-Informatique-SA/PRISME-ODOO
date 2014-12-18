from osv import osv, fields 

class product_product_prisme(osv.osv):
    _name = "product.product" 
    _inherit = "product.product"
    
    _columns = {
                "sale_analytic_account_id": fields.many2one("account.analytic.account", 
                                                string="Sale Analytic Account")
    }

product_product_prisme()