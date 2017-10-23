from openerp.osv import osv, fields

class prisme_project_worker(osv.Model):
    _inherit = "project.project"
    
    def _get_sale_orders(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        
        for project in self.browse(cr, uid, ids, context=context):
        
            obj_sale_orders = self.pool.get('sale.order')
            sale_orders_ids = obj_sale_orders.search(cr, uid,
                                            [('origin', '=', project.code),
                                            ])
            
            res[project.id] = []
            res[project.id].extend([sale_order.id for sale_order in obj_sale_orders.browse(cr, uid, sale_orders_ids)])
            
        
        return res
    
    
    def _get_purchase_orders(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        
        for project in self.browse(cr, uid, ids, context=context):
        
            obj_purchase_orders = self.pool.get('purchase.order')
            purchase_orders_ids = obj_purchase_orders.search(cr, uid,
                                            [('origin', '=', project.code),
                                            ])
            
            res[project.id] = []
            res[project.id].extend([purchase_order.id for purchase_order in obj_purchase_orders.browse(cr, uid, purchase_orders_ids)])
            
        
        return res
    
    
    
    _columns = {
        'sale_orders': fields.function(_get_sale_orders,
                    type='one2many', obj="sale.order", string='Sale orders',
                    method=True),
        'purchase_orders': fields.function(_get_purchase_orders,
                    type='one2many', obj="purchase.order", string='Purchase orders',
                    method=True),
        
    }