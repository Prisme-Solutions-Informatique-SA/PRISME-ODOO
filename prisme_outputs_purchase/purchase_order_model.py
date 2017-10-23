from openerp.osv import fields, osv, expression


class purchase_order_prisme(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    
    _columns = {
                'delivery_terms': fields.many2one('stock.incoterms', 
                                                  string = 'Delivery Terms'),
    }
      
purchase_order_prisme()
