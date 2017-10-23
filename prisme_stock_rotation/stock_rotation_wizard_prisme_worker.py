from openerp.osv import fields, osv, expression
from datetime import date, datetime

class stock_rotation_wizard_prisme(osv.osv_memory):
    _name = 'stock.rotation.wizard.prisme'

    _columns = {
        'period_begin': fields.date('Beginning of period', required=True),
        'period_end': fields.date('End of period', required=True),
    }
    
    _defaults = {
        'period_begin': str(date(date.today().year, 1, 1)),
        'period_end': str(date.today()),
    }
    
    def _check_periods(self, cr, uid, ids):
        ok = True
        for record in self.browse(cr, uid, ids):
            begin_date = datetime.strptime(record.period_begin, \
                                           '%Y-%m-%d').date()
            end_date = datetime.strptime(record.period_end, \
                                         '%Y-%m-%d').date() 
                                                                                
            if begin_date > end_date:
                ok = False
            if end_date > date.today():
                ok = False
                
        return ok
    
    _constraints = [
                    (_check_periods,
                     'The beginning of the period must be before the end' + \
                     ' of period and none can be future',
                     ['period_begin', 'period_end']),
                   ]
    
    def stock_rotation_prisme_launch_report(self, cr, uid, ids, context=None):
        model_obj = self.pool.get('ir.model.data')
        action_obj = self.pool.get('ir.actions.act_window')
        result_context = {}
        if context is None:
            context = {}
        result = model_obj.get_object_reference(cr, uid, 'prisme_stock_rotation',
                                    'product_product_stock_rotation_action')
        id = result and result[1] or False
        result = action_obj.read(cr, uid, [id], context=context)[0]
        data = self.read(cr, uid, ids, [])[0]
        result_context.update({'period_begin': data['period_begin']})
        result_context.update({'period_end': data['period_end']})
        result['context'] = str(result_context)
        return result

stock_rotation_wizard_prisme()
