from osv import osv, fields 
import netsvc
import hr_timesheet_invoice
from datetime import datetime
import openerp.addons.decimal_precision as dp

class product_product_cplg(osv.osv):
    _name = "product.product"
    _inherit = "product.product"
    _columns = {
        'qty_pallet': fields.integer('Quantity pallet'),
   }
    
product_product_cplg()

