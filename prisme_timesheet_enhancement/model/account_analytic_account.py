from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

class account_analytic_account(models.Model):
    _name = "account.analytic.account" 
    _inherit = "account.analytic.account"
    
    invoice_on_timesheets = fields.Boolean("Invoice On Timesheets")       
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist',
            help="The product to invoice is defined on the employee form, the price will be deducted by this pricelist on the product.")
    
    hours_qtt_est = fields.Float('Estimation of Hours to Invoice')
    timesheet_ca_invoiced = fields.Float(compute='_timesheet_ca_invoiced_calc', string='Remaining Time',
            help="Sum of timesheet lines invoiced for this contract.")
    remaining_hours_to_invoice = fields.Float(compute='_remaining_hours_to_invoice_calc', string='Remaining Time',
            help="Computed using the formula: Expected on timesheets - Total invoiced on timesheets")
    ca_to_invoice = fields.Float(compute='_analysis_all' , string='Uninvoiced Amount',
            help="If invoice from analytic account, the remaining amount you can invoice to the customer based on the total costs.",
            digits_compute=dp.get_precision('Account'))
    
    to_invoice = fields.Many2one('hr_timesheet_invoice.factor', 'Timesheet Invoicing Ratio',
            help="You usually invoice 100% of the timesheets. But if you mix fixed price and timesheet invoicing, you may use another ratio. For instance, if you do a 20% advance invoice (fixed price, based on a sales order), you should invoice the rest on timesheet with a 80% ratio.")
    
    def _timesheet_ca_invoiced_calc(self):
        
        lines_obj = self.env['account.analytic.line']
        res = {}
        inv_ids = []
        for account in self:
            account.timesheet_ca_invoiced = 0.0
            lines = lines_obj.search([('account_id','=', account.id), ('invoice_id','!=',False), ('invoice_id.state', 'not in', ['draft', 'cancel']), ('to_invoice','!=', False), ('invoice_id.type', 'in', ['out_invoice', 'out_refund'])])
            for line in lines:
                if line.invoice_id.id not in inv_ids:
                    inv_ids.append(line.invoice_id.id)
                    if line.invoice_id.type == 'out_refund':
                        account.timesheet_ca_invoiced -= line.invoice_id.amount_untaxed
                    else:
                        account.timesheet_ca_invoiced += line.invoice_id.amount_untaxed
                        
    def _analysis_all(self):
        cr = self.env.cr
        for account in self:
            cr.execute("""
                SELECT product_id, sum(amount), user_id, to_invoice, sum(unit_amount), product_uom_id, line.name
                FROM account_analytic_line line
                WHERE account_id = %s
                    AND invoice_id IS NULL
                    AND to_invoice IS NOT NULL
                GROUP BY product_id, user_id, to_invoice, product_uom_id, line.name""", (account.id,))

            res = 0.0
            for product_id, price, user_id, factor_id, qty, uom, line_name in cr.fetchall():
                price = -price
                if product_id:
                    price = self._get_invoice_price(account, product_id, qty)
                factor = self.env['hr_timesheet_invoice.factor'].browse(factor_id)
                res += price * qty * (100-factor.factor or 0.0) / 100.0
        
            # sum both result on account_id
            dp = 2
            account.ca_to_invoice = round(res, dp)
    
    def _get_invoice_price(self, account, product_id, qty):
        if account.pricelist_id:
            pl = account.pricelist_id
            price = pl.price_get(product_id, qty or 1.0, account.partner_id.id)[pl.id]
        else:
            price = 0.0
        return price
    
    @api.depends('hours_qtt_est','timesheet_ca_invoiced','ca_to_invoice')
    def _remaining_hours_to_invoice_calc(self):
        res = {}
        for account in self:
            account.remaining_hours_to_invoice = max(account.hours_qtt_est - account.timesheet_ca_invoiced, account.ca_to_invoice)
    
