from openerp.osv import fields, osv, expression

class AccountInvoiceLine(osv.Model):
	_name = 'account.invoice.line'
	_inherit = 'account.invoice.line'
	_columns = {
		'state': fields.related('invoice_id', 'state', type='char', size=64, string='State'),
		'journal_id': fields.related('invoice_id', 'journal_id', relation='account.journal', type='many2one', string='Journal', help='field'),
		'currency_id': fields.related('invoice_id', 'currency_id', relation='res.currency', type='many2one', string='Currency', help='field'),
		'analytic_journal_id': fields.many2one('account.analytic.journal', 'Journal Analytique'),
		
	}
AccountInvoiceLine()