from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import date, datetime

class stock_rotation_wizard_prisme(models.TransientModel):
    _name = 'stock.rotation.wizard.prisme'

    period_begin = fields.Date('Beginning of period', default=str(date(date.today().year, 1, 1)), required=True)
    period_end = fields.Date('End of period', default=str(date.today()), required=True)
    
    @api.constrains('period_begin', 'period_end')
    def _check_periods(self):
        ok = True
        for record in self:
            begin_date = datetime.strptime(record.period_begin, \
                                           '%Y-%m-%d').date()
            end_date = datetime.strptime(record.period_end, \
                                         '%Y-%m-%d').date() 
                                                                                
            if begin_date > end_date:
                ok = False
            if end_date > date.today():
                ok = False
                
        if not ok:
            raise ValidationError('The beginning of the period must be before the end' + \
                     ' of period and none can be future')
    
    def stock_rotation_prisme_launch_report(self):
        model_obj = self.env['ir.model.data']
        action_obj = self.env['ir.actions.act_window']
        result_context = {}
        if self.env.context is None:
            context = {}
        
        result = self.env['ir.actions.act_window'].for_xml_id('prisme_stock_rotation', 'product_product_stock_rotation_action')
        
        data = self
        result_context.update({'period_begin': data['period_begin']})
        result_context.update({'period_end': data['period_end']})
        result['context'] = str(result_context)
        return result
