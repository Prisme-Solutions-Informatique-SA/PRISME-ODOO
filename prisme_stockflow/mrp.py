from datetime import datetime
from osv import osv, fields
from tools.translate import _
import netsvc
import time
import tools


class prisme_mrp_production(osv.osv):
    _inherit = 'mrp.production' 
    _name = 'mrp.production'
        
    # Method copied from addons/mrp/mrp.py 
    def action_confirm(self, cr, uid, ids):
        """ Confirms production order.
        @return: Newly generated picking Id.
        """
        picking_id = False
        proc_ids = []
        seq_obj = self.pool.get('ir.sequence')
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        for production in self.browse(cr, uid, ids):
            if not production.product_lines:
                self.action_compute(cr, uid, [production.id])
                production = self.browse(cr, uid, [production.id])[0]
            routing_loc = None
            pick_type = 'internal'
            address_id = False
            if production.bom_id.routing_id and production.bom_id.routing_id.location_id:
                routing_loc = production.bom_id.routing_id.location_id
                if routing_loc.usage <> 'internal':
                    pick_type = 'out'
                address_id = routing_loc.address_id and routing_loc.address_id.id or False
                routing_loc = routing_loc.id
            pick_name = seq_obj.get(cr, uid, 'stock.picking.' + pick_type)
            # Modification begin
            #Get the corresponding warehouse
            warehouse = self.pool.get('stock.warehouse')
            warehouse_id = warehouse.search(cr, uid, [('company_id', '=', production.company_id.id)])
            warehouse_obj = warehouse.browse(cr, uid, warehouse_id)[0]
            # Modification end
            picking_id = pick_obj.create(cr, uid, {
                'name': pick_name,
                'origin': (production.origin or '').split(':')[0] + ':' + production.name,
                'type': pick_type,
                'move_type': 'one',
                'state': 'draft',
                'address_id': address_id,
                'auto_picking': self._get_auto_picking(cr, uid, production),
                'company_id': production.company_id.id,
            })

            # Modification begin
            if  production.product_id.shopfloor_location:
                dst_location = production.product_id.shopfloor_location.id
            else:
                # Standard case
                dst_location = production.location_dest_id.id,
            # Modification end

            source = production.product_id.product_tmpl_id.property_stock_production.id
            data = {
                'name':'PROD:' + production.name,
                'date': production.date_planned,
                'product_id': production.product_id.id,
                'product_qty': production.product_qty,
                'product_uom': production.product_uom.id,
                'product_uos_qty': production.product_uos and production.product_uos_qty or False,
                'product_uos': production.product_uos and production.product_uos.id or False,
                # Modification begin
                'location_id': source, #7
                'location_dest_id': dst_location,
                # Modification end
                'move_dest_id': production.move_prod_id.id,
                'state': 'waiting',
                'company_id': production.company_id.id,
            }
            res_final_id = move_obj.create(cr, uid, data)
             
            self.write(cr, uid, [production.id], {'move_created_ids': [(6, 0, [res_final_id])]})
            moves = []
            for line in production.product_lines:
                move_id = False
                newdate = production.date_planned
                if line.product_id.type in ('product', 'consu'):
                    # Modification begin
                    oldsource = source
                    oldrouting_loc = routing_loc
                    source = line.product_id.product_tmpl_id.property_stock_production.id
                    routing_loc = warehouse_obj.mo_cons_location.id
                    # Modification end
                    res_dest_id = move_obj.create(cr, uid, {
                        'name':'PROD:' + production.name,
                        'date': production.date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'location_id': routing_loc or production.location_src_id.id,
                        # Modification begin
                        'location_dest_id': source, #7
                        'move_dest_id': res_final_id, #12
                        # Modification end
                        'state': 'waiting',
                        'company_id': production.company_id.id,
                    })
                    # Modification begin
                    source = oldsource
                    routing_loc = oldrouting_loc
                    # Modification end
                    moves.append(res_dest_id)
                    # Modification begin
                    # picking move
                    routing_loc = warehouse_obj.mo_cons_location.id
                    
                    if line.product_id.storage_location:
                        src_location = line.product_id.storage_location.id
                    else:
                        src_location = production.location_src_id.id,
                    # Modification end
                    move_id = move_obj.create(cr, uid, {
                        'name':'PROD:' + production.name,
                        'picking_id':picking_id,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'date': newdate,
                        'move_dest_id': res_dest_id,
                        # Modification begin
                        'location_id': src_location,
                        'location_dest_id': routing_loc or production.location_src_id.id, #12
                        # Modification end
                        'state': 'waiting',
                        'company_id': production.company_id.id,
                    })
                    # Modification begin
                    routing_loc = None
                    # Modification end
                proc_id = proc_obj.create(cr, uid, {
                    'name': (production.origin or '').split(':')[0] + ':' + production.name,
                    'origin': (production.origin or '').split(':')[0] + ':' + production.name,
                    'date_planned': newdate,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'product_uos_qty': line.product_uos and line.product_qty or False,
                    'product_uos': line.product_uos and line.product_uos.id or False,
                    'location_id': production.location_src_id.id,
                    'procure_method': line.product_id.procure_method,
                    'move_id': move_id,
                    'company_id': production.company_id.id,
                })
                wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                proc_ids.append(proc_id)                
            #wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            self.write(cr, uid, [production.id], {'picking_id': picking_id, 'move_lines': [(6, 0, moves)], 'state':'confirmed'})
            message = _("Manufacturing order '%s' is scheduled for the %s.") % (
                production.name,
                datetime.strptime(production.date_planned, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
            )
            self.log(cr, uid, production.id, message)
        return picking_id

prisme_mrp_production()
