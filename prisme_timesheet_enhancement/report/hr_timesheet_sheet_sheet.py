from odoo import models, fields, api, _

class hr_timesheet_sheet_prisme(models.Model):
    _name = "hr_timesheet_sheet.sheet"
    _inherit = "hr_timesheet_sheet.sheet"
    
    def get_sorted_timesheets(self):
        #sheet = self.env['hr_timesheet_sheet.sheet'].search(['id', '=', sheet_id])[0]
        timesheets = self.timesheet_ids
        sorted_timesheets = timesheets.sorted(key=lambda r: r.time_beginning)
        
        return sorted_timesheets
    
    oldDate = False
    curDate = False
    
    def updateDate(self, date):
        if hr_timesheet_sheet_prisme.oldDate != date:
            hr_timesheet_sheet_prisme.curDate = date
        else:
            hr_timesheet_sheet_prisme.curDate=""
        hr_timesheet_sheet_prisme.oldDate = date
        
        return hr_timesheet_sheet_prisme.curDate