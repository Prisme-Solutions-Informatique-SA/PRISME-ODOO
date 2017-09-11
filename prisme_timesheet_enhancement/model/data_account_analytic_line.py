from odoo import api, fields, models, _

class account_analytic_line_prisme(models.Model):
    _name = "account.analytic.line" 
    _inherit = "account.analytic.line"
    
    invoice_id = fields.Many2one('account.invoice', 'Invoice', ondelete="set null", copy=False)
    to_invoice = fields.Many2one('hr_timesheet_invoice.factor', 'Invoiceable', help="It allows to set the discount while making invoice, keep empty if the activities should not be invoiced.")
    
    account_partner = fields.Many2one(related='account_id.partner_id', relation='res.partner', string='Partner Id', store=True)
    general_account_id = fields.Many2one(related='product_id.property_account_expense_id', relation='account.account')