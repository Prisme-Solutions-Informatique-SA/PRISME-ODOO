from osv import osv, fields

class hr_analytic_timesheet_prisme(osv.osv):
    _name = 'hr.analytic.timesheet'
    _inherit = 'hr.analytic.timesheet'

    # Method copied the 30.08.2012 (OpenERP 6.1) from 
    # addons/hr_timesheet_sheet/hr_timesheet_sheet.py, line 479.
    # Not modified, but necessary to be called from the field
    def _sheet(self, cursor, user, ids, name, args, context=None):
        sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        res = {}.fromkeys(ids, False)
        for ts_line in self.browse(cursor, user, ids, context=context):
            sheet_ids = sheet_obj.search(cursor, user,
                [('date_to', '>=', ts_line.date), ('date_from', '<=', ts_line.date),
                 ('employee_id.user_id', '=', ts_line.user_id.id)],
                context=context)
            if sheet_ids:
            # [0] because only one sheet possible for an employee between 2 dates
                res[ts_line.id] = sheet_obj.name_get(cursor, user, sheet_ids, context=context)[0]
        return res

    _columns = {
                # Override the existing code field 
                # addons/hr_timesheet_sheet/hr_timesheet_sheet.py, line 516)
                # to store always the field (see bug 2726).
                'sheet_id': fields.function(_sheet, string='Sheet',
                        type='many2one', relation='hr_timesheet_sheet.sheet',
                        store=True),
    }
    
hr_analytic_timesheet_prisme()