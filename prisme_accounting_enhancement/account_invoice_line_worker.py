from openerp import netsvc
from openerp import models, api, _
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp

class account_invoice_line_prisme(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        if self.discount_type == 'amount':
            price = self.price_unit - (self.discount or 0.0)
        elif self.discount_type == 'percent':
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        else:
            price = self.price_unit
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = round(self.price_subtotal / self.invoice_id.rounding_on_subtotal) * self.invoice_id.rounding_on_subtotal
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)      
    
    _columns = {
        
        # Field copied to remove the '%' in the label        
        'discount': fields.float(string='Discount'   ,digits=dp.get_precision('Discount'),default=0.0),

        'discount_type': fields.selection([('none', ''),
                                           ('amount', 'Amount'),
                                           ('percent', 'Percent')],
                                          'Discount type'),
    }
    
    _defaults = {
        'discount_type': 'percent',
    }
    

    @api.model
    def move_line_get(self, invoice_id):
        inv = self.env['account.invoice'].browse(invoice_id)
        currency = inv.currency_id.with_context(date=inv.date_invoice)
        company_currency = inv.company_id.currency_id

        res = []
        for line in inv.invoice_line:
            mres = self.move_line_get_item(line)
            mres['invl_id'] = line.id
            res.append(mres)
            tax_code_found = False

            # Loic -> allow amount discount
            if line.discount_type == 'amount':
                price = line.price_unit - (line.discount or 0.0)
            elif line.discount_type == 'percent':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit
            # end

            taxes = line.invoice_line_tax_id.compute_all(price,
                line.quantity, line.product_id, inv.partner_id)['taxes']
            for tax in taxes:
                if inv.type in ('out_invoice', 'in_invoice'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(dict(mres))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = currency.compute(tax_amount, company_currency)

        return res

account_invoice_line_prisme()