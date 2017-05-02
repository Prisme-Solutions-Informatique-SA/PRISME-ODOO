from openerp import netsvc
from odoo import api, fields, models, _


class sale_order_line_prisme(models.Model):
    _name = 'sale.order.line' 
    _inherit = 'sale.order.line'
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = super(sale_order_line_prisme, self)._prepare_invoice_line(qty)
        
        res['discount_type'] = self.discount_type

        return res