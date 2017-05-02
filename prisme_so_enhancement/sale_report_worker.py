from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from odoo import api, fields, models, _
import openerp.addons.decimal_precision as dp
import pdb

class sale_report(models.Model):
    _name = 'sale.report'
    _inherit = 'sale.report'
    

    so_name = fields.Char('Sale Order', readonly=True)
    discount_total = fields.Float('Total Discount', digits=(16, 2))
    net_price_total = fields.Float('Total Price (Net)', digits=(16, 2))
    purchase_total = fields.Float('Total Purchase', digits=(16, 2))
    margin_total = fields.Float('Total Margin', digits=(16, 2))
                

    def _select2(self):
        select_str = super(sale_report, self)._select() + """,
                    sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
                    sum(l.price_subtotal) as net_price_total,
                    sum(l.product_uom_qty * l.purchase_price) as purchase_total, 
                    sum(l.margin) as margin_total,
                    s.name as so_name
        """

        return select_str


    def _select(self):
        select_str = super(sale_report, self)._select() + """,
                    sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
                    sum(l.price_subtotal) as net_price_total,
                    sum(l.product_uom_qty * l.purchase_price) as purchase_total, 
                    sum(l.margin) as margin_total,
                    s.name as so_name
        """
        return select_str

    def _group_by(self):
        return super(sale_report, self)._group_by() + ", s.name,l.discount_type"
