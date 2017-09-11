from odoo import models, fields, api, _
import operator

class hr_timesheet_sheet_prisme(models.Model):
    _name = "account.analytic.line"
    _inherit = "account.analytic.line"
    
    old = ["", ""]
    client = False
    project = False

    def getSortedList(self):    
        sortedList = self.sorted(key=operator.attrgetter('partner_id.name', 'account_id.name', 'date', 'time_beginning'))
        return sortedList
    
    def updateClAPr(self):
        if self.partner_id.name == hr_timesheet_sheet_prisme.old[0]:
            hr_timesheet_sheet_prisme.client = ""
        else :
            hr_timesheet_sheet_prisme.client = self.partner_id.name
            hr_timesheet_sheet_prisme.old[0] = self.partner_id.name
        if self.account_id.name == hr_timesheet_sheet_prisme.old[1]:
            hr_timesheet_sheet_prisme.project = ""
        else:
            hr_timesheet_sheet_prisme.project = self.account_id.name
            hr_timesheet_sheet_prisme.old[1] = self.account_id.name
            
    def getClient(self):
        return hr_timesheet_sheet_prisme.client

    def getProject(self):
        return hr_timesheet_sheet_prisme.project