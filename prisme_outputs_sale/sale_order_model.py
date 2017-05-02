from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from odoo import api, fields, models, _
import openerp.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class sale_order_prisme(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    

    print_totals = fields.Boolean('Print Totals',
                                              help='Show the totals on the ' + 
                                              'botom of the quotation/SO. ' + 
                                              'Used, for example, to offer 2 ' + 
                                              'choices to a customer and ' + 
                                              ' don\'t show a useless total.',
                                              default=True)
    print_vat = fields.Boolean('Print VAT',
                                            help='Show the VAT on the bottom ' + 
                                            ' on the Quotation/SO. Warning: ' + 
                                            'you cannot print VAT if you ' + 
                                             'don\'t print the totals.',
                                             default=True)
    footer_comment = fields.Text('Footer comment')
    header_comment = fields.Text('Header comment')

    @api.constrains('print_vat')
    def _check_printings(self):
        for sale_order in self:
            if not sale_order.print_totals:
                if sale_order.print_vat:
                    raise ValidationError('You can\'t print VAT if you don\'t print totals')
    

class sale_order_line_prisme(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    notes = fields.Text('Notes')
    
