from openerp.osv import osv, fields


class AccountInvoiceLine(osv.Model):
    _inherit = "account.invoice.line"
    _columns = {
        'analytic_journal_id': fields.related(
            'invoice_id', 'analytic_journal_id', relation='account.analytic.journal',
            type='many2one', string='Journal Analytique', help='field'),
    }
