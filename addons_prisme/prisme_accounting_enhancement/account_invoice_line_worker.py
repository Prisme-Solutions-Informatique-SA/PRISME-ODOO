from openerp import netsvc
from odoo import api, fields, models, _
import openerp.addons.decimal_precision as dp

class account_invoice_line_prisme(models.Model):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
   
    # Method inherited from default model to recompute correct price with percent and amount discounts        
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        #start prisme modification :  compute price_unit with percent or amount discount
        if self.discount_type == 'amount':
            price = self.price_unit - (self.discount or 0.0)
        elif self.discount_type == 'percent':
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        else:
            price = self.price_unit        
        #end prisme modification
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        
        #start prisme modification :  compute rounding price
        if self.invoice_id:
            self.price_subtotal = round(self.price_subtotal / self.invoice_id.rounding_on_subtotal) * self.invoice_id.rounding_on_subtotal
        #end prisme modification   
        
    # Field copied to remove the '%' in the label        
    discount = fields.Float(string='Discount' ,digits=dp.get_precision('Discount'),default=0.0)

    discount_type = fields.Selection([('none', ''),
                                           ('amount', 'Amount'),
                                           ('percent', 'Percent')],
                                          'Discount type', default='percent')
