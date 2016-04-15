from openerp.osv import osv, fields


class AccountInvoiceLine(osv.Model):
    _inherit = "account.invoice.line"
    _columns = {
        'journal_id': fields.related(
            'invoice_id', 'journal_id', relation='account.journal',
            type='many2one', string='Journal', help='field'),
    }
