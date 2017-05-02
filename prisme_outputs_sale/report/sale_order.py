from openerp.report import report_sxw
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from odoo import api, fields, models, _
from openerp import netsvc
import openerp.addons.decimal_precision as dp

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    # Bug fix - change default print button to custom prisme report
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'quotation_sent', cr)
        datas = {
                 'model': 'sale.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'sale.order.email.prisme', 'datas': datas, 'nodestroy': True}


class prisme_sale_order_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(prisme_sale_order_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'sale_order_lines': self._get_sale_order_lines,
            'get_column_disc': self._get_column_disc,
        })
        self.context = context
        
    
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
                
            if entry.layout_type == 'article':
                res['discount'] = entry.discount > 0.0 and entry.discount_type != 'none' and self.formatLang(entry.discount, digits=self.get_digits(dp='Sale Price'))
                res['discount_label'] = entry.discount > 0.0 and entry.discount_type == 'amount' and '-' or entry.discount > 0.0 and entry.discount_type == 'percent' and '%' or '' 
                if entry.discount != 0.0:
                    flag_disc = flag_disc + entry.discount
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
                if entry.discount < 0.0:
                    flag_disc = flag_disc + entry.discount

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
            if entry.refused:
                continue
                
            if entry.layout_type == 'article':
                res['tax_id'] = ', '.join(map(lambda x: x.name, entry.tax_id)) or ''
                res['name'] = entry.name
                res['product_uom_qty'] = entry.product_uom_qty or 0.00
                res['product_uom'] = entry.product_uom.name
                res['price_unit'] = entry.price_unit or 0.00
                res['discount'] = entry.discount > 0.0 and entry.discount_type != 'none' and self.formatLang(entry.discount, digits=self.get_digits(dp='Sale Price'))
                res['discount_label'] = entry.discount > 0.0 and entry.discount_type == 'amount' and '-' or entry.discount > 0.0 and entry.discount_type == 'percent' and '%' or '' 
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
