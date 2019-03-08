from openerp.report import report_sxw
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from odoo import api, fields, models, _
from openerp import netsvc
import openerp.addons.decimal_precision as dp
import xml.etree.ElementTree as ET
import re

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    # Bug fix - change default print button to custom prisme report
    @api.multi
    def print_quotation(self):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'sale.order.email.prisme')


class prisme_sale_order_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(prisme_sale_order_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'sale_order_lines': self._get_sale_order_lines,
            'get_column_disc': self._get_column_disc,
            'get_contact': self._get_contact,
        })
        self.context = context
        
    # This method return the address block.
    # The first value is the address object.
    # The second value is the options to pass to the QWeb method.
    def _get_contact(self, value, options):
        if not value:
            return ""
        
        # Copy the value with the context of the parser
        # With this the address is translated in the lang of the customer
        value = value.with_context(self.localcontext)
        
        try:
            # Try to use the QWeb function (should works)
            return self._get_contact_qweb(value, options)
        except Exception, e:
            #print("Failed to generate address with QWeb method: " + str(e))
            # Otherwise use the older version (from Odoo 7)
            try:
                return self._get_contact_display_address(value)
            except Exception, e:
                print("Failed to generate address with RML method: " + str(e))
    
    # This method return the address block.
    # The first value is the address object.
    def _get_contact_display_address(self, value):
        # Please use get_contact(self, value, options)
        # https://github.com/odoo/odoo/blob/7.0/addons/sale/report/sale_order.rml#L119
        
        contact_str = ""
        if isinstance(value.parent_name, basestring) and not value.is_company:
            contact_str += value.parent_name + "\n"
        # No need to show the company name twice
        if value.parent_name != value.name:
            if value.title:
                contact_str += value.title.name + " "
            contact_str += value.name + "\n"
        # Call _display_address and let it handle the company name (without_company=False)
        contact_str += value._display_address(True)
        return contact_str
        
    # This method return the address block.
    # The first value is the address object.
    # The second value is the options to pass to the QWeb method.
    def _get_contact_qweb(self, value, options):
        raise Exception("Disabled, Move Contact under Company in address")
        
        # Please use get_contact(self, value, options)
        # https://github.com/odoo/odoo/blob/10.0/addons/sale/report/sale_report_templates.xml#L12
        
        # Get env var from self or the value
        env = self.env if hasattr(self, 'env') else value.env
        
        # Call the QWeb widget. The function returns the HTML for a QWeb report
        contact_str = env['ir.qweb.field.contact'].value_to_html(value, options)
        
        # Transform <br/> and <br> (HTML New Line) to \n (New Line character) with Regex (re)
        contact_str = re.sub('<br\s*/?>', '\n', contact_str.strip())
        
        # ET.fromstring(contact_str) => Parse XML (HTML) to ETree Object
        # ET.tostring(..., method='text') => Stringify ETree Object to Plain text (remove tags)
        # This line remove every tags in contact_str
        contact_str = ET.tostring(ET.fromstring(contact_str), method='text')
        
        # This line use Regex (re) to replace multiple new line (empty or whitespaced) to one new line
        # "\s*(\n|\r)+\s*":
        # - "\s*" => Zero or more Whitespace (space, tab, ...)
        # - "(\n|\r)+" One or more new line (\n) or carriage return (\r)
        contact_str = re.sub('\s*(\n|\r)+\s*', '\n', contact_str.strip())
        return contact_str
    
    
    # method to determine whether there have a discount
    # if so,  return a flag at 1 (one)
    # In the .rml, make a conditional clauses
    def _get_column_disc(self, sale_order):
        
        flag_disc = 0
        # Initialize variables
        sub_total = {}
        order_lines = []
        res = {}

        for line in sale_order.order_line:
            order_lines.append(line)

        j = 0
        sum_flag = {}
        sum_flag[j] = -1
        
        #for debuging
        #pdb.set_trace() 
        
        for entry in order_lines:
            res = {}
            #if entry.refused:
             #   continue
                
            total_discount = (entry.price_subtotal - entry.product_uom_qty * entry.price_unit)
            if entry.layout_type == 'article':
                res['discount'] = total_discount > 0.0 and self.formatLang(total_discount, digits=self.get_digits(dp='Sale Price'))
                if total_discount != 0.0:
                    flag_disc = flag_disc + total_discount
            else:
                res['discount'] = ''

                if entry.layout_type == 'subtotal':
                    sum = 0
                    sum_id = 0
                    if sum_flag[j] == -1:
                        temp = 1
                    else:
                        temp = sum_flag[j]

                    for sum_id in range(temp, len(sub_total)+1):
                        sum += sub_total[sum_id]
                    sum_flag[j+1] = sum_id +1

                    j = j + 1
                    res['discount'] = ''
                if total_discount < 0.0:
                    flag_disc = flag_disc + total_discount

        if flag_disc == 0.0:
            return '0'
        return '1'
   
    # Method copied from addons/sale_layout/report/report_sale_layout.py,
    # line 41 to be modified for the specifics Prisme, cleared and used in the
    # Prisme's specifics reports.    
    def _get_sale_order_lines(self, sale_order):
        # Initialize variables
        result = []
        sub_total = {}
        order_lines = []
        res = {}
        for line in sale_order.order_line:
            order_lines.append(line)

        i = 1
        j = 0
        sum_flag = {}
        sum_flag[j] = -1
        
        for entry in order_lines:
            res = {}
            total_discount = (entry.price_subtotal - entry.product_uom_qty * entry.price_unit)
            if entry.refused:
                continue
                
            if entry.layout_type == 'article':
                res['tax_id'] = ', '.join(map(lambda x: x.name, entry.tax_id)) or ''
                res['name'] = entry.name
                res['product_uom_qty'] = entry.product_uom_qty or 0.00
                res['product_uom'] = entry.product_uom.name
                res['price_unit'] = entry.price_unit or 0.00
                res['discount'] = total_discount < 0.0 and self.formatLang(total_discount, digits=self.get_digits(dp='Sale Price'))
                res['price_subtotal'] = self.formatLang(entry.price_subtotal, digits=self.get_digits(dp='Sale Price')) or 0.00
                sub_total[i] = entry.price_subtotal and entry.price_subtotal
                i = i + 1
                res['notes'] = entry.notes or ''
                res['layout_type'] = entry.layout_type
            else:
                res['product_uom_qty'] = ''
                res['price_unit'] = ''
                res['discount'] = ''
                res['tax_id'] = ''
                res['layout_type'] = entry.layout_type
                res['notes'] = entry.notes or ''
                res['product_uom'] = ''

                if entry.layout_type == 'subtotal':
                    res['name'] = entry.name
                    sum = 0
                    sum_id = 0
                    if sum_flag[j] == -1:
                        temp = 1
                    else:
                        temp = sum_flag[j]

                    for sum_id in range(temp, len(sub_total)+1):
                        sum += sub_total[sum_id]
                    sum_flag[j+1] = sum_id +1

                    j = j + 1
                    res['price_subtotal'] = self.formatLang(sum, digits=self.get_digits(dp='Sale Price'))
                    res['quantity'] = ''
                    res['price_unit'] = ''
                    res['discount'] = ''
                    res['tax_id'] = ''
                    res['product_uom'] = ''
                elif entry.layout_type == 'title':
                    res['name'] = entry.name
                    res['price_subtotal'] = ''
                elif entry.layout_type == 'text':
                    res['name'] = entry.name
                    res['price_subtotal'] = ''
                elif entry.layout_type == 'line':
                    res['name'] = ''
                    res['price_subtotal'] = ''
                elif entry.layout_type == 'break':
                    res['name'] = ''
                    res['price_subtotal'] = ''
                else:
                    res['name'] = entry.name
                    res['price_subtotal'] = ''
                    
            result.append(res)
        return result

report_sxw.report_sxw(
        'report.sale.order.paper.prisme',
        'sale.order',
        'addons/prisme_outputs_sale/report/sale_order.rml',
         parser=prisme_sale_order_parser,
    )

report_sxw.report_sxw(
        'report.sale.order.email.prisme',
        'sale.order',
        'addons/prisme_outputs_sale/report/sale_order.rml',
        parser=prisme_sale_order_parser
    )
