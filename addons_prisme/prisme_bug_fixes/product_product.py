from osv import osv, fields

class product_product_prisme(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    # Method overriden to fix the problem when searching a ressource linked
    # to a product using the product name. See bug 2759
    def name_search(self, cr, user, name='', args=None, operator='ilike', 
                    context=None, limit=100):
        if not limit:
            limit = 100
        res = super(product_product_prisme, self).name_search(cr, user, 
                        name=name, args=args, operator=operator, 
                        context=context, limit=limit)
        return res
    
product_product_prisme()