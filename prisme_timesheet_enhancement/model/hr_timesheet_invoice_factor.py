from odoo import models, fields, api, _
# class used to set discount for timesheets invoicing
class hr_timesheet_invoice_factor(models.Model):
    _name = "hr_timesheet_invoice.factor"
    _description = "Invoice Rate"
    _order = 'factor'

    name = fields.Char('Internal Name', required=True, translate=True)
    customer_name = fields.Char('Name', help="Label for the customer")
    factor = fields.Float('Discount (%)', required=True, help="Discount in percentage", default=lambda *a: 0.0)