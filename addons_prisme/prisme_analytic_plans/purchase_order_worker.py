from osv import osv

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    
    def inv_line_create(self, cr, uid, a, ol):
        res = super(purchase_order, self).\
            inv_line_create(cr, uid, a, ol)
        product = ol.product_id
        if product:
            if product.analytic_distribution:
                res[2]['analytics_id'] = \
                  product.analytic_distribution.id or False
        return res
    
purchase_order()
