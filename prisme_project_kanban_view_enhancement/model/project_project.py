from openerp.osv import osv, fields

class AccountInvoice(osv.Model):
    _inherit = "project.project"
    _columns = {
        'client_id': fields.related(
            'analytic_account_id', 'partner_id', relation='res.partner',
            type='many2one', string='Client'),
    }