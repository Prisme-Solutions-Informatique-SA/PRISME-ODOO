from openerp import models, fields, api, _
from openerp import netsvc
from openerp.osv.orm import browse_record_list, browse_record, browse_null
from openerp.tools.translate import _


class AccountInvoiceLine(models.Model):
	_name = "account.invoice.line"
	_inherit = "account.invoice.line"
	
	
	state = fields.Selection(related='invoice_id.state', string='State', store=True)
	journal_id = fields.Many2one(related='invoice_id.journal_id', relation='account.journal', string='Journal', store=True)
	currency_id = fields.Many2one(related='invoice_id.currency_id', relation='res.currency', string='Currency', store=True)