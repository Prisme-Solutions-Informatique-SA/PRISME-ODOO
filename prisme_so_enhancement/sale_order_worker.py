from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta

class sale_order_prisme(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    # Method copied from sale/sale.py (sale_order._get_order) the 19.07.2011
    # No modified, used to be referenced from the columns overriden 
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    # Method copied from sale/sale.py (sale_order._amount_line_tax the 22.09.2011
    # modified the 22.09.2011 by Damien Raemy to compute the subtotal by line 
    # using the discount type (percent, amount or null).
    def _amount_line_tax(self, cr, uid, line, context=None):
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
        
        
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, unit_price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
    # Method copied from sale/sale.py (sale_order._amount_all) the 19.07.2011
    # modified the 19.07.2011 by Damien Raemy to don't compute the tax in the
    # total when the line is refused
    def _amount_all_prisme(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        
        
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                #Modification begin
                # Modification no       1
                # Author(s):            Damien Raemy
                # Date:                 19.07.2011
                # Last modification:    19.07.2011
                # Description:          Don't treat a line if it is refused
                # But:                  Manage the refused boolean in the lines
                
                if line.refused:
                    continue
                # Modification 1 end
                
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + \
                    res[order.id]['amount_tax']
        return res
    
    _columns = {
                'refused' : fields.text('refused'),
                #######
                'rounding_on_subtotal': fields.float('Rounding on Subtotal'),
                    
                'quotation_validity': fields.date('Quotation Validity',
                    readonly=True,
                    states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]
}),
                'quotation_comment': fields.char('Quotation Comment', 255,
                    translate=True, readonly=False,
                    states={'draft': [('readonly', False)]}),
                                               
                'cancellation_reason': fields.char("Cancellation Reason", 255,
                    readonly=True,
                    states={'draft': [('readonly', False)],
                            'sent': [('readonly', False)],
                              'manual': [('readonly', False)],
                              'progress': [('readonly', False)],
                              'shipping_except': [('readonly', False)],
                              'invoice_except': [('readonly', False)]}),
                              
                # Columns overriden to use the Prisme's methode (see _amount_all_prisme)
                'amount_untaxed': fields.function(_amount_all_prisme, method=True, digits_compute=dp.get_precision('Sale Price'), string='Untaxed Amount',
                store={
                    'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                    'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                },
                 multi='sums', help="The amount without tax."),
                'amount_tax': fields.function(_amount_all_prisme, method=True, digits_compute=dp.get_precision('Sale Price'), string='Taxes',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                        'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                    },
                    multi='sums', help="The tax amount."),
                'amount_total': fields.function(_amount_all_prisme, method=True, digits_compute=dp.get_precision('Sale Price'), string='Total',
                    store={
                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                        'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                    },
                    multi='sums', help="The total amount."),
                'shipped': fields.boolean("Shipped"),
                'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, 
                    states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'manual': [('readonly', False)]}, copy=True),

    }
    
    _defaults = {
        'rounding_on_subtotal': lambda *a: 0.05,
    }
    
    def action_cancel(self, cr, uid, ids, context=None):
        result = super(sale_order_prisme, self).action_cancel(cr, uid,
                                                              ids, context)
        for order in self.browse(cr, uid, ids, context):
            reason = order.cancellation_reason
            if not reason:
                raise osv.except_osv(
                        ('Could not cancel sales order !'),
                        ('You must specify a cancellation reason in the ' + 
                         'Other Information tab before cancelling this ' + 
                         'sale order'))
        return result
    

    # Method copied the 28.08.2012 from OpenERP 6.1. addons/sale/sale.py
    # (sale_order._get_date_planned). 
    # Contains modifications formerly made on the action_ship_create method.
    # Modified the 10.12.2010 by Damien Raemy to use the date_delivery_field
    # for the date planned if existant.
    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):  
        #Modification begin
        # Modification no:      1
        # Author(s):            Damien Raemy
        # Date:                 20.04.2011
        # Last modification:    20.04.2011
        # Description:          Override the planned delivery date 
        #                       computation
        # But:                  Consider the date delivery field in a
        #                       sale order line (added by this module)
        if line.date_delivery:
            date_planned = datetime.strptime(line.date_delivery, "%Y-%m-%d")
        else:
            date_planned = datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(days=line.delay or 0.0)
        #Modification 1 end
        
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return date_planned
    
        
    # Method copied the 17.11.2015 from Odoo 8.0 addons/sale/sale.py
    # Modified to manage the refused line
    def action_ship_create(self, cr, uid, ids, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        :return: True
        """
        context = context or {}
        context['lang'] = self.pool['res.users'].browse(cr, uid, uid).lang
        procurement_obj = self.pool.get('procurement.order')
        sale_line_obj = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            proc_ids = []
            vals = self._prepare_procurement_group(cr, uid, order, context=context)
            if not order.procurement_group_id:
                group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                order.write({'procurement_group_id': group_id})

            for line in order.order_line:
            
                # Modification begin
                if line.refused:
                    continue
                # Modification end
            
                if line.state == 'cancel':
                    continue
                #Try to fix exception procurement (possible when after a shipping exception the user choose to recreate)
                if line.procurement_ids:
                    #first check them to see if they are in exception or not (one of the related moves is cancelled)
                    procurement_obj.check(cr, uid, [x.id for x in line.procurement_ids if x.state not in ['cancel', 'done']])
                    line.refresh()
                    #run again procurement that are in exception in order to trigger another move
                    except_proc_ids = [x.id for x in line.procurement_ids if x.state in ('exception', 'cancel')]
                    procurement_obj.reset_to_confirmed(cr, uid, except_proc_ids, context=context)
                    proc_ids += except_proc_ids
                elif sale_line_obj.need_procurement(cr, uid, [line.id], context=context):
                    if (line.state == 'done') or not line.product_id:
                        continue
                    vals = self._prepare_order_line_procurement(cr, uid, order, line, group_id=order.procurement_group_id.id, context=context)
                    ctx = context.copy()
                    ctx['procurement_autorun_defer'] = True
                    proc_id = procurement_obj.create(cr, uid, vals, context=ctx)
                    proc_ids.append(proc_id)
            #Confirm procurement order such that rules will be applied on it
            #note that the workflow normally ensure proc_ids isn't an empty list
            procurement_obj.run(cr, uid, proc_ids, context=context)

            #if shipping was in exception and the user choose to recreate the delivery order, write the new status of SO
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
                order.write(val)
        return True

sale_order_prisme()
