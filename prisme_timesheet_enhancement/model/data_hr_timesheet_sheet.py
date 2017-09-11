from odoo import models, fields, api, _

class hr_timesheet_sheet_prisme(models.Model):
    _name = "hr_timesheet_sheet.sheet"
    _inherit = "hr_timesheet_sheet.sheet"
    
    period_hours = fields.Float("Period Hours")
    bonus_malus = fields.Float(compute="_calculats_bonus_malus",
                           string="Bonus/malus",
                           store=False)
    
    @api.one
    def _calculats_bonus_malus(self):
        nb_hours = self.total_timesheet
        nb_period_hours = self.period_hours
        bonus_malus = nb_hours - nb_period_hours
        self.bonus_malus = bonus_malus
    
    def name_get(self):
        res = []
        for timesheet in self:
            res.append((timesheet.id,timesheet.name))
        return res 
    
    
    _order="date_from"
