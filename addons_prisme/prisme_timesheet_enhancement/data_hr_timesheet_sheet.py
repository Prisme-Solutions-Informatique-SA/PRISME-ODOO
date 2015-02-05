from osv import osv, fields

class hr_timesheet_sheet_prisme(osv.osv):
    _name = "hr_timesheet_sheet.sheet"
    _inherit = "hr_timesheet_sheet.sheet"
    
    def _calculats_bonus_malus(self, cr, uid, ids, field, arg, context=None):
        res = {}
        timesheets = self.browse(cr, uid, ids, context=context)
        for timesheet in timesheets:
            nb_hours = timesheet.total_timesheet
            nb_period_hours = timesheet.period_hours
            bonus_malus = nb_hours - nb_period_hours
            res[timesheet.id] = bonus_malus
        return res
    
    _columns = {
        "period_hours": fields.float("Period Hours"),
        #TODO Find how to allow to compute the sum when we use a group by
        # but with a recompute of the value when changing data (maybe with
        # triggers, see performance optimization in the documentation)
        "bonus_malus": fields.function(_calculats_bonus_malus,
                           type="float", method=True,
                           string="Bonus/malus",
                           store=False),
    }
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = []
	timesheets = self.read(cr, uid, ids,['id','name'],context=context)
	for timesheet in timesheets:
            res.append((timesheet['id'],timesheet['name']))
            return res
        return res 
    
    _order="date_from"
    
    
hr_timesheet_sheet_prisme()
