from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc

class prisme_sale_order(osv.osv):
    _inherit = 'sale.order'
    _name = 'sale.order'
    
    
    def action_ship_create(self, cr, uid, ids, *args):
        result = super(prisme_sale_order, self).action_ship_create(cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids, context={}):
            for picking in order.picking_ids:           
                for line in picking.move_lines:
                    if line.product_id.storage_location and picking.name.startswith('INT'):
                        print 'line:'
                        print line
                        self.pool.get('stock.move').write(cr, uid, line.id, 
                                                          {'location_id': line.product_id.storage_location.id,
                                                           'location_dest_id': order.shop_id.warehouse_id.lot_output_id.id})
        return result
    
#    # Method copied from addons/sale/sale.py
#    def action_ship_create(self, cr, uid, ids, *args):
#        wf_service = netsvc.LocalService("workflow")
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
#                                #Modification begin
#                # Modification no:   1
#                # Author(s):         Damien Raemy
#                # Date:              20.04.2011
#                # Last modification: 20.04.2011
#                # Description:       Override the planned delivery date 
#                #                    computation
#                # But:               Consider the date delivery field in a
#                #                    sale order line (added by this module)
#                if line.date_delivery:
#                    date_planned =datetime.strptime(line.date_delivery, '%Y-%m-%d')
#                else:
#                    date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)
#                #Modification end
#                date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')
#
#                if line.state == 'done':
#                    continue
#                move_id = False
#                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
#                    # Modification begin
#                    if line.product_id.storage_location:
#                        location_id = line.product_id.storage_location.id
#                    else:
#                        # Standard case
#                        location_id = order.shop_id.warehouse_id.lot_stock_id.id
#                    # Modification end
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
#                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
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
#                     # Modification begin
#                    if line.product_id.storage_location:
#                        location_id = line.product_id.storage_location.id
#                    else:
#                        # Standard case
#                        location_id = order.shop_id.warehouse_id.lot_stock_id.id
#                    # Modification end
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
#                        # Modification begin
#                        'location_id': location_id,
#                        # Original lines:
#                        #'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
#                        # Modification end
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
#                                    mov_ids = move_obj.search(cr, uid, [('state', '=', 'cancel'),('sale_line_id', '=', line.id),('picking_id', '=', pick.id)])
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

prisme_sale_order()