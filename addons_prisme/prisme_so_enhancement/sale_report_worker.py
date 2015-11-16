from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp

class sale_report(osv.osv):
    _name = 'sale.report'
    _inherit = 'sale.report'

    def _compute_discount(self, cr, uid, ids, field_name, arg, context=None):
        import pdb; pdb.set_trace()
        res = {}
        
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.total_price - line.net_price_total
        
        return res
    
    _columns = {
                'so_name': fields.char('Sale Order', 255, readonly=True),
                'discount_total': fields.float('Total Discount', digits=(16, 2)),
                'net_price_total': fields.float('Total Price (Net)', digits=(16, 2)),
                'purchase_total': fields.float('Total Purchase', digits=(16, 2)),
                'margin_total': fields.float('Total Margin', digits=(16, 2)),
                }

   
    def _select(self):
        return  super(sale_report, self)._select() + """, sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total, 
        sum(l.price_subtotal) as net_price_total, 
        sum(l.product_uom_qty * l.purchase_price) as purchase_total, 
        sum(l.margin) as margin_total,
        s.name as so_name"""

    def _group_by(self):
        return super(sale_report, self)._group_by() + ", s.name"


sale_report()
