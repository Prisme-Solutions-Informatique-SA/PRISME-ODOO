from os.path import split
from datetime import datetime
from openerp.report import report_sxw
from odoo import api, fields, models, _
from openerp import netsvc
import xml.etree.ElementTree as ET
import re
import logging

class prisme_accounting_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(prisme_accounting_parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            "get_date": self._get_date,
            "sorts_lines": self._sorts_lines,
            "get_contact": self._get_contact,
            "get_column_disc": self._get_column_disc,
            })
        self.context = context
    
    def _get_column_disc(self, lines):
        
        flag_disc = 0
        # Initialize variables
        sub_total = {}
        order_lines = []
        res = {}

        for line in lines:
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

            total_discount = (entry.price_subtotal - entry.quantity * entry.price_unit)                
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
        # No need to show the company name twice
        
        if isinstance(value.parent_name, basestring) and not value.is_company:
            contact_str += value.parent_name + "\n"
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
    
    #return date of sale by id of line
    def _get_date(self, line):
        
        id = line.id
        id = str(id)
        self.cr.execute("SELECT order_line_id FROM sale_order_line_invoice_rel WHERE invoice_id = "+ id)
        orderId = self.cr.fetchone()[0]
        
        relard_Stock=[]
        obj_Stock = self.pool.get("stock.move")
        related_Stock_ids = obj_Stock.search(self.cr, self.uid,
                              [("sale_line_id", "=", orderId),])
        if related_Stock_ids:
            relard_Stock = obj_Stock.browse(self.cr, self.uid, \
                                             related_Stock_ids)
        return relard_Stock[0].date_expected
    
    #return a dictionary of lines
    #differentiate between standard line and line of a combined delivery bulltin
    def _sorts_lines(self, lines):
        
        #import pdb
        #pdb.set_trace() 
        
        list_lines = []
        #sort by name
        linesstored = sorted(lines, key=lambda lines: lines.sequence, reverse=False)
        lasthead =''
        for l in linesstored:
            dic_lines = {}
            dic_lines['name'] = l.name

            dic_lines['tax'] = ' ,'.join([ lt.name or '' for lt in l.invoice_line_tax_ids ])
            dic_lines['quantity'] = l.quantity
            if l.uom_id:
              dic_lines['uos_name'] = l.uom_id.name
            else:
              dic_lines['uos_name'] = ''
            dic_lines['price_unit'] = l.price_unit
            total_discount = (l.price_subtotal - l.quantity * l.price_unit)
            dic_lines['discount'] = total_discount < 0.0 and self.formatLang(total_discount, digits=self.get_digits(dp='Sale Price'))               
            dic_lines['price_subtotal'] = l.price_subtotal
            #the fields 'note' is not in v7.0
            #dic_lines['note'] = l.note
            dic_lines['pick'] = ''
            #add dictionary in line
            list_lines.append(dic_lines)
        return list_lines

# Change default print report to custom prisme report 
class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    def invoice_print(self):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'account.invoice.email.prisme')

    
report_sxw.report_sxw(
        'report.account.invoice.paper.prisme',
        'account.invoice',
        rml='addons/prisme_outputs_accounting/report/invoice.rml',
        parser=prisme_accounting_parser
    )

report_sxw.report_sxw(
        'report.account.invoice.email.prisme',
        'account.invoice',
        rml='addons/prisme_outputs_accounting/report/invoice.rml',
        parser=prisme_accounting_parser
    )
