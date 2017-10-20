from osv import osv, fields 
import netsvc
import hr_timesheet_invoice
from datetime import datetime

class hr_timesheet_lines_prisme(osv.osv):
    """
    Contain the the Prisme"s supplemental data of the timesheet lines
    Don"t forget to import this class in __init__.py 
    """
    
    # the _name and the _inherit have to be the same as the parent"s name 
    _name = "hr.analytic.timesheet"
    _inherit = "hr.analytic.timesheet"
    
    def _get_month(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            date = datetime.strptime(line.date, '%Y-%m-%d')
            month = date.strftime('%Y-%m')
            result[line.id] = month
        return result
        
    # the data that are stored   
    _columns = {
        "time_beginning": fields.float("Beginning"),
        "time_end": fields.float("End"),
        "time_quantity": fields.related("line_id", "unit_amount", type="float"),
        "internal_description": fields.text("Internal Description"),
        "working_date": fields.related("line_id", "date", type="date",
                                        store=True),
        'working_month': fields.function(_get_month, type='char', size=7, 
                                         method=True, store=True)
    }
        
    _order = "working_date ASC, time_beginning ASC"
         
    def on_change_account_id(self, cr, uid, ids, account_id):
        res = {}
        if not account_id:
            return res
        res.setdefault("value", {})
        acc = self.pool.get("account.analytic.account").browse(cr, uid, account_id)
        st = acc.to_invoice.id
        res["value"]["to_invoice"] = st or False
        res["value"]["partner_id"] = acc.partner_id.id
        if acc.state == "pending":
            res["warning"] = {
                "title": "Warning",
                "message": "The analytic account is in pending state.\nYou should not work on this account !"
            }
        return res
    
    def onchange_times(self, cr, uid, ids, beginning, end):
        res = {}
        res.setdefault("value", {})
        quantity = end - beginning
        res["value"]["unit_amount"] = quantity
        return res
    
    def _check_beginning(self, cr, uid, ids):
        for hr_line in self.browse(cr, uid, ids):
            beginning = hr_line.time_beginning
        return beginning >= 0 and beginning <= 24
    
    def _check_end(self, cr, uid, ids):
        for hr_line in self.browse(cr, uid, ids):
            end = hr_line.time_end
        return end >= 0 and end <= 24        

    def _check_beginning_end(self, cr, uid, ids):
        for hr_line in self.browse(cr, uid, ids):
            beginning = hr_line.time_beginning
            end = hr_line.time_end
        return beginning <= end or end == 0

    _constraints = [
                    (_check_beginning, "Beginning time must be between 00:00 and 24:00", ["time_beginning"]),
                    (_check_end, "End time must be between 00:00 and 24:00", ["time_end"]),
                    (_check_beginning_end, "End time must not be before beginning time", ["time_beginning", "time_end"]),
                   ]
        
# instantiation of the class (OBLIGATORY)
hr_timesheet_lines_prisme()
