from osv import osv, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import decimal_precision as dp
import netsvc
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

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
                    states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'manual': [('readonly', False)]}),

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
    
    # Method copied from sale/sale.py (action_ship_create) the 10.12.2010
    # Modified the 10.12.2010 by Damien Raemy to use the date_delivery_field
    # for the date planned if existant.
    # Modified the 20.04.2011 by Damien Raemy to be synchronized with the last
    # version of the method
    # Modified the 12.07.2011 by Damien Raemy to manage the refused line
    
    # Old Method used in V6.0.2 (see _create_pickings_and_procurements)
#===============================================================================
#    def action_ship_create(self, cr, uid, ids, *args):
#        wf_service = netsvc.LocalService('workflow')
#        picking_id = False
#        move_obj = self.pool.get('stock.move')
#        proc_obj = self.pool.get('procurement.order')
#        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
#        for order in self.browse(cr, uid, ids, context={}):
#            proc_ids = []
#            output_id = order.shop_id.warehouse_id.lot_output_id.id
#            picking_id = False
#            for line in order.order_line:
#                proc_id = False
#                
#                #Modification begin
#                # Modification no       2
#                # Author(s):            Damien Raemy
#                # Date:                 12.07.2011
#                # Last modification:    12.07.2011
#                # Description:          Don't treat a line if it is refused
#                # But:                  Manage the refused boolean in the lines
#                
#                if line.refused:
#                    continue
#                
#                # Modification 2 end
#                                        
#                #Modification begin
#                # Modification no:      1
#                # Author(s):            Damien Raemy
#                # Date:                 20.04.2011
#                # Last modification:    20.04.2011
#                # Description:          Override the planned delivery date 
#                #                       computation
#                # But:                  Consider the date delivery field in a
#                #                       sale order line (added by this module)
#                if line.date_delivery:
#                    date_planned = datetime.strptime(line.date_delivery, '%Y-%m-%d')
#                else:
#                    date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)
#                #Modification 1 end
#                
#                date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')
#                if line.state == 'done':
#                    continue
#                move_id = False
#                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
#                    location_id = order.shop_id.warehouse_id.lot_stock_id.id
#                    if not picking_id:
#                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
#                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
#                            'name': pick_name,
#                            'origin': order.name,
#                            'type': 'out',
#                            'state': 'auto',
#                            'move_type': order.picking_policy,
#                            'sale_id': order.id,
#                            'address_id': order.partner_shipping_id.id,
#                            'note': order.note,
#                            'invoice_state': (order.order_policy == 'picking' and '2binvoiced') or 'none',
#                            'company_id': order.company_id.id,
#                        })
#                    move_id = self.pool.get('stock.move').create(cr, uid, {
#                        'name': line.name[:64],
#                        'picking_id': picking_id,
#                        'product_id': line.product_id.id,
#                        'date': date_planned,
#                        'date_expected': date_planned,
#                        'product_qty': line.product_uom_qty,
#                        'product_uom': line.product_uom.id,
#                        'product_uos_qty': line.product_uos_qty,
#                        'product_uos': (line.product_uos and line.product_uos.id)\
#                                or line.product_uom.id,
#                        'product_packaging': line.product_packaging.id,
#                        'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
#                        'location_id': location_id,
#                        'location_dest_id': output_id,
#                        'sale_line_id': line.id,
#                        'tracking_id': False,
#                        'state': 'draft',
#                        #'state': 'waiting',
#                        'note': line.notes,
#                        'company_id': order.company_id.id,
#                    })
# 
#                if line.product_id:
#                    proc_id = self.pool.get('procurement.order').create(cr, uid, {
#                        'name': line.name,
#                        'origin': order.name,
#                        'date_planned': date_planned,
#                        'product_id': line.product_id.id,
#                        'product_qty': line.product_uom_qty,
#                        'product_uom': line.product_uom.id,
#                        'product_uos_qty': (line.product_uos and line.product_uos_qty)\
#                                or line.product_uom_qty,
#                        'product_uos': (line.product_uos and line.product_uos.id)\
#                                or line.product_uom.id,
#                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
#                        'procure_method': line.type,
#                        'move_id': move_id,
#                        'property_ids': [(6, 0, [x.id for x in line.property_ids])],
#                        'company_id': order.company_id.id,
#                    })
#                    proc_ids.append(proc_id)
#                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {'procurement_id': proc_id})
#                    if order.state == 'shipping_except':
#                        for pick in order.picking_ids:
#                            for move in pick.move_lines:
#                                if move.state == 'cancel':
#                                    mov_ids = move_obj.search(cr, uid, [('state', '=', 'cancel'), ('sale_line_id', '=', line.id), ('picking_id', '=', pick.id)])
#                                    if mov_ids:
#                                        for mov in move_obj.browse(cr, uid, mov_ids):
#                                            move_obj.write(cr, uid, [move_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
#                                            proc_obj.write(cr, uid, [proc_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
# 
#            val = {}
# 
#            if picking_id:
#                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
# 
#            for proc_id in proc_ids:
#                wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
# 
#            if order.state == 'shipping_except':
#                val['state'] = 'progress'
#                val['shipped'] = False
# 
#                if (order.order_policy == 'manual'):
#                    for line in order.order_line:
#                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
#                            val['state'] = 'manual'
#                            break
#            self.write(cr, uid, [order.id], val)
#        return True
#===============================================================================
    
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
            date_planned = datetime.strptime(line.date_delivery, DEFAULT_SERVER_DATE_FORMAT)
        else:
            date_planned = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=line.delay or 0.0)
        #Modification 1 end
        
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return date_planned
    
    # Method copied the 28.08.2012 from OpenERP 6.1. addons/sale/sale.py
    # (sale_order._create_pickings_and_procurement). 
    # Contains modifications formerly made on the action_ship_create method.
    # Modified the 12.07.2011 by Damien Raemy to manage the refused line
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Create the required procurements to supply sale order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sale order's requested location.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: sale order to which the order lines belong
        :param list(browse_record) order_lines: sale order line records to procure
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if ommitted.
        :return: True
        """
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []

        for line in order_lines:
            if line.state == 'done':
                continue
            
            #Modification begin
            # Modification no       1
            # Author(s):            Damien Raemy
            # Date:                 12.07.2011
            # Last modification:    12.07.2011
            # Description:          Don't treat a line if it is refused
            # But:                  Manage the refused boolean in the lines
            
            if line.refused:
                continue
            
            # Modification 1 end

            date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

            if line.product_id:
                if line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context))
                else:
                    # a service has no stock move
                    move_id = False

                proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context))
                proc_ids.append(proc_id)
                line.write({'procurement_id': proc_id})
                self.ship_recreate(cr, uid, order, line, move_id, proc_id)

        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        val = {}
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False

            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True

sale_order_prisme()
