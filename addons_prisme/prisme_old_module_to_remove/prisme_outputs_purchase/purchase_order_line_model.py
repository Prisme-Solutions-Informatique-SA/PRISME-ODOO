from osv import osv, fields

class purchase_order_line_prisme(osv.osv):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"
    
    _order = 'sequence ASC'
    _columns = {
        "page_break": fields.boolean("Page Break", 
                                     help="Add a page break before this line"),
        
        'sequence': fields.integer('Sequence'),
    }
      
purchase_order_line_prisme()
