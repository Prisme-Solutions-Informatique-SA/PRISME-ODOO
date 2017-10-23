from openerp.osv import fields, osv, expression

class AccountInvoiceLine(osv.Model):
	_name = 'account.invoice.line'
	_inherit = 'account.invoice.line'
	
	def _get_analytic_journal(self, cr, uid, ids, field_name, arg, context=None):
		
		res = {}
		for invoice_line_object in self.browse(cr, uid, ids, context=context):
			res[invoice_line_object.id] = invoice_line_object.invoice_id.journal_id.analytic_journal_id.name
		
		
		return res
	
	_columns = {
		'state': fields.related('invoice_id', 'state', type='char', size=64, string='State'),
		'journal_id': fields.related('invoice_id', 'journal_id', relation='account.journal', type='many2one', string='Journal', help='field', store=True),
		'analytic_journal': fields.function(_get_analytic_journal, method=True, multi=False,
									type='char', string='Analytic Journal', store=True),
		'currency_id': fields.related('invoice_id', 'currency_id', relation='res.currency', type='many2one', string='Currency', help='field', store=True),
		
	}
AccountInvoiceLine()