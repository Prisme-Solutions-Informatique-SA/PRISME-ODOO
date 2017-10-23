from openerp.osv import fields, osv, expression

"Bug fixes: Use the statement date in imported lignes inside bank statements"

class account_bank_statement_prisme(osv.osv):
    _inherit = "account.bank.statement"
    
    def onchange_date(self, cr, uid, ids, date, company_id, context=None):
        res = super(account_bank_statement_prisme, self).onchange_date(cr, uid, ids, date, company_id, context=context)
        if context is None:
            context = {}
            
        for st in self.browse(cr, uid, ids, context=context):
            for st_line in st.line_ids:
                st_line.date = date
        return res
        
account_bank_statement_prisme()