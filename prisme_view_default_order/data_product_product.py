from openerp.osv import osv, fields 
from openerp import netsvc
import hr_timesheet_invoice
from datetime import datetime
import openerp.addons.decimal_precision as dp

class product_product_cplg(osv.osv):
    _name = "product.product"
    _inherit = "product.product"
    _columns = {
        'label_print_type': fields.selection([('mid','mid'), ('min','min')],'Label print type',required=False),
   }
    
product_product_cplg()

