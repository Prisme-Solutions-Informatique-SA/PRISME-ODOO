from osv import fields, osv

class product_product_worker(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    _columns = {
                'storage_location': fields.many2one('stock.location', 
                                            'Storage Location', 
                                            domain=[('usage', '<>', 'view')]),
                'shopfloor_location': fields.many2one('stock.location', 
                                            'Shopfloor Location', 
                                            doman=[('usage', '<>', 'view')])
                }
    
product_product_worker()
