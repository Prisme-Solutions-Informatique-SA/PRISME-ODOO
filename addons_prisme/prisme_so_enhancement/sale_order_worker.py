from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from odoo import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta
from odoo.modules.module import OdooHook
from odoo.exceptions import UserError, ValidationError

class sale_order_prisme(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    
        # Method copied from sale/sale.py (sale_order._amount_line_tax the 22.09.2011
    # modified the 22.09.2011 by Damien Raemy to compute the subtotal by line 
    # using the discount type (percent, amount or null).
    def _amount_line_tax(self, line):
        val = 0.0
        #Modification begin
        # Modification no       1
        # Author(s):            Damien Raemy
        # Date:                 22.09.2011
        # Last modification:    22.09.2011
        # Description:          Calculate the unit price using discount_type
        # But:                  Have a price rightly calculated
        if line.discount_type == 'amount':
            unit_price = line.price_unit - (line.discount or 0.0)
        elif line.discount_type == 'percent':
            unit_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        else:
            unit_price = line.price_unit 
        # Modification 1 end    
        
        
        for c in self.env['account.tax'].compute_all(line.tax_id, unit_price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
            
    # Method copied from sale/sale.py (sale_order._amount_all) the 25.01.2017
    # and modified to don't compute the tax in the
    # total when the line is refused        
    @api.depends('order_line.price_total')
    def _amount_all_prisme(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:              
                # Prisme Modification begin
                # But: Manage the refused boolean in the lines
           
                if line.refused:
                    continue
                # Prisme Modification end
                
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    # Prisme modification start
                    if line.discount_type == 'amount':
                        price = line.price_unit - (line.discount or 0.0)
                    elif line.discount_type == 'percent':
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    else:
                        price = line.price_unit 
                    # Prisme modification end
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
    
    
    refused = fields.Text('refused')

    rounding_on_subtotal = fields.Float('Rounding on Subtotal', default=lambda *a: 0.05)
                    
    quotation_validity = fields.Date('Quotation Validity', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)] })
    quotation_comment = fields.Char('Quotation Comment', translate=True, readonly=False, states={'draft': [('readonly', False)]})
                                               
    cancellation_reason = fields.Char("Cancellation Reason", readonly=True, states={'draft': [('readonly', False)],
                            'sent': [('readonly', False)],
                              'manual': [('readonly', False)],
                              'progress': [('readonly', False)],
                              'shipping_except': [('readonly', False)],
                              'invoice_except': [('readonly', False)],
                              'sale': [('readonly', False)]})
                              
    # Columns overriden to use the Prisme's methode (see _amount_all_prisme)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all_prisme', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all_prisme', track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_prisme', track_visibility='always')
                    
                    
    shipped = fields.Boolean("Shipped")
    order_line = fields.One2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, 
                    states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'manual': [('readonly', False)]}, copy=True)

    
    @api.multi
    def action_cancel(self):
        result = super(sale_order_prisme, self).action_cancel()
        reason = self.cancellation_reason
        if not reason:
            raise ValidationError(_('You must specify a cancellation reason in the ' + 
                     'Other Information tab before cancelling this ' + 
                     'sale order'))
        return result
    
    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            # Prisme Modification begin
            if line.refused:
                continue
            # Prisme Modification end
            
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].create(vals)
            new_proc.message_post_with_view('mail.message_origin_link',
                values={'self': new_proc, 'origin': line.order_id},
                subtype_id=self.env.ref('mail.mt_note').id)
            new_procs += new_proc
        new_procs.run()
        return new_procs
