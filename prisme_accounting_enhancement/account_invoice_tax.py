from odoo import api, fields, models, _

class account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"    
    
    def _compute_base_amount(self):
        super(account_invoice_tax, self)._compute_base_amount()
        for tax in self:
            if tax.base == 0.0 and not tax.tax_id:
                # sql request to get old base from previous ODOO 8 version in which tax.base was stored and note computed
                request_sql= 'Select base from account_invoice_tax where id = \''+str(tax.id)+'\''
                self.env.cr.execute(request_sql)
                taxes = self.env.cr.fetchall()
                if len(taxes) > 0:
                    tax_b = taxes[0]
                    if tax_b:
                        tax.base = tax_b[0]