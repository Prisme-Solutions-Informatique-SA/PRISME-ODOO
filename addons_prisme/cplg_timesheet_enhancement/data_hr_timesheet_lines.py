from osv import osv, fields 
import netsvc
import hr_timesheet_invoice
from datetime import datetime
import openerp.addons.decimal_precision as dp

class hr_timesheet_lines_cplg(osv.osv):
    _name = "hr.analytic.timesheet"
    _inherit = "hr.analytic.timesheet"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
   }
    
hr_timesheet_lines_cplg()
