from openerp import netsvc
from odoo import api, fields, models, _
import openerp.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class account_invoice_line_prisme(models.Model):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
   
    # Field copied to remove the '%' in the label        
    discount = fields.Float(string='Discount (percent)' ,digits=dp.get_precision('Discount'),default=0.0)
    #New field for discount in amount
    discount_amount = fields.Float(string='Discount (amount)', digits=(16, 2), default=0.0)
    
    #Deprecated, tried to delete but stuck with a "discount_type doest not exist" error
    #Seems to work when uninstalling then installing the module but then the data is lost...
    discount_type = fields.Selection([('amount', 'Amount'),
                                      ('percent', 'Percent')],
                                       'Discount type', readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default='percent')
   
    def check_discount_percent(self, discount_value):
        error = ""
        if (discount_value < 0.0):
            error = _("A discount in percent cannot be negative !")
        elif (discount_value > 100.0):
            error = _("A discount in percent cannot be bigger than 100 !")
        return error
 
    def check_discount_amount(self, discount_amount_value, price_unit_value):
        error = ""
        if (discount_amount_value < 0.0):
            error = _("A discount in amount cannot be negative !")
        elif (discount_amount_value > price_unit_value):
            error = _("A discount in amount cannot be bigger than the price !")
        return error
    
    #Override "create" and "write" functions to check discount constraints each save/creation in DB.
    #Tried using @api.constrains for almost one day, seems never to be called...
    @api.model
    def create(self, values):
        # Do your custom logic here
        final_error = ""
        if 'discount' in values:
            error = self.check_discount_percent(values['discount'])
            if error:
                final_error+=(error+"\n")
        if 'discount_amount' in values:
            error = self.check_discount_amount(values['discount_amount'], values['price_unit'])
            if error:
                final_error+=error
        if final_error:
            raise ValidationError(final_error)    
        return super(account_invoice_line_prisme, self).create(values)
 
    @api.model
    def write(self, values):
        # Do your custom logic here
        final_error = ""
        if 'discount' in values:
            error = self.check_discount_percent(values['discount'])
            if error:
                final_error+=(error+"\n")
        if 'discount_amount' in values:
            error = self.check_discount_amount(values['discount_amount'], self.price_unit)
            if error:
                final_error+=error
        if final_error:
            raise ValidationError(final_error)
        return super(account_invoice_line_prisme, self).write(values)
   
    # Method inherited from default model to recompute correct price with percent and amount discounts        
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        #start prisme modification :  compute price_unit with percent or amount discount
        price = self.price_unit
        if (self.discount_amount):
            price = price - self.discount_amount
            
        if (self.discount):
            price = price * (1 - (self.discount / 100.0))        
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
