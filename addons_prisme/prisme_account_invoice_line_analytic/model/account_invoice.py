from openerp.osv import osv, fields

class AccountInvoice(osv.Model):
    _inherit = "account.invoice"
    _columns = {
        'analytic_journal_id': fields.related(
            'journal_id', 'analytic_journal_id', relation='account.analytic.journal',
            type='many2one', string='Journal Analytique'),
    }