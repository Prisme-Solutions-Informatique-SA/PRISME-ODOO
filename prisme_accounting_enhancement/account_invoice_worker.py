from odoo import api, fields, models, _

class account_invoice_prisme(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    rounding_on_subtotal = fields.Float('Rounding on Subtotal', default=lambda *a: 0.01)
    
    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            #Prisme modification start : compute price_unit with percent or amount discount
            price_unit = line.price_unit
            if (line.discount_amount):
                price_unit = price_unit - line.discount_amount
            
            if (line.discount):
                price_unit = price_unit * (1 - (line.discount / 100.0)) 
                 
            #Prisme modification end
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped
    
    @api.multi
    def copy(self, default=None):
        default['reference_type'] = 'none'
        
        return super(account_invoice_prisme, self).copy(default=default)
