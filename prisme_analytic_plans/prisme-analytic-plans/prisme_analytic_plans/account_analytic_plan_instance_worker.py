from osv import osv, fields

class account_analytic_plan_instance(osv.osv):
    _name = 'account.analytic.plan.instance'
    _inherit = 'account.analytic.plan.instance'
    
    _order = 'name, code'
    
account_analytic_plan_instance()