from openerp.osv import osv, fields


class AccountInvoiceLine(osv.Model):
	_inherit = "account.invoice.line"
	_columns = {
		'state': fields.related('invoice_id', 'state', type='char', size=64, string='State'),
		'journal_id': fields.related('invoice_id', 'journal_id', relation='account.journal', type='many2one', string='Journal', help='field'),
		'currency_id': fields.related('invoice_id', 'currency_id', relation='res.currency', type='many2one', string='Currency', help='field'),
		'analytic_journal_id': fields.related('invoice_id', 'analytic_journal_id', relation='account.analytic.journal', type='many2one', string='Journal Analytique', help='field'),
	}