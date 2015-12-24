from openerp.osv import fields, osv, expression

"Bug fixes: Use the statement date in imported lignes inside bank statements"

class account_payment_populate_statement_prisme(osv.osv_memory):
    _inherit = "account.payment.populate.statement"

    def _prepare_statement_line_vals(self, cr, uid, payment_line, amount, statement, context=None):
        return {
            'date': statement.date,
            'name': payment_line.order_id.reference or '?',
            'amount':-amount,
            'partner_id': payment_line.partner_id.id,
            'statement_id': statement.id,
            'ref': payment_line.communication,
        }
account_payment_populate_statement_prisme()