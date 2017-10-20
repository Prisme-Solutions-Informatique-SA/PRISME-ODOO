from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby
from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging

class prisme_stock_move(osv.osv):
    _inherit = 'stock.move'
    _name = 'stock.move'
    
    # Method copied from addons/stock/stock.py
    def create_chained_picking(self, cr, uid, moves, context=None):
        res_obj = self.pool.get('res.company')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        wf_service = netsvc.LocalService("workflow")
        new_moves = []
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        for picking, todo in self._chain_compute(cr, uid, moves, context=context).items():
            ptype = todo[0][1][5] and todo[0][1][5] or location_obj.picking_type_get(cr, uid, todo[0][0].location_dest_id, todo[0][1][0])
            if picking:
                # name of new picking according to its type
                new_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + ptype)
                pickid = self._create_chained_picking(cr, uid, new_pick_name, picking, ptype, todo, context=context)
                # Need to check name of old picking because it always considers picking as "OUT" when created from Sale Order
                old_ptype = location_obj.picking_type_get(cr, uid, picking.move_lines[0].location_id, picking.move_lines[0].location_dest_id)
                if old_ptype != picking.type:
                    old_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + old_ptype)
                    picking_obj.write(cr, uid, [picking.id], {'name': old_pick_name}, context=context)
            else:
                pickid = False
            for move, (loc, dummy, delay, dummy, company_id, ptype) in todo:
                new_id = move_obj.copy(cr, uid, move.id, {
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': loc.id,
                    'date_moved': time.strftime('%Y-%m-%d'),
                    'picking_id': pickid,
                    'state': 'waiting',
                    'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', context=context)  ,
                    'move_history_ids': [],
                    'date': (datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') + relativedelta(days=delay or 0)).strftime('%Y-%m-%d'),
                    'move_history_ids2': []}
                )
                # Modification begin
                if pickid:
                    tmp_stock_picking = self.pool.get('stock.picking')
                    tmp_sale_order = self.pool.get('sale.order')
                    tmp_linkpicking = tmp_stock_picking.browse(cr, uid, pickid)
                    if tmp_linkpicking.origin.find("SO") >= 0:
                            #In this case we need to change the stock move value
                            tmp_stock_move = self.pool.get('stock.move')
                            res3 = tmp_stock_move.search(cr, uid, [('picking_id', '=', pickid)])
                            sale_order_id = tmp_sale_order.search(cr, uid, [('name', '=', tmp_linkpicking.origin)])
                            so = tmp_sale_order.browse(cr, uid, sale_order_id)
                            tmp_loc_src = so[0].shop_id.warehouse_id.lot_output_id.id
                            tmp_loc_dst = so[0].shop_id.warehouse_id.so_picking_dest.id 
                            move_obj.write(cr, uid, [new_id], {
                                         'location_id': tmp_loc_src,
                                         'location_dest_id': tmp_loc_dst,
                                         })
                # Modification end
                move_obj.write(cr, uid, [move.id], {
                    'move_dest_id': new_id,
                    'move_history_ids': [(4, new_id)]
                })
                new_moves.append(self.browse(cr, uid, [new_id])[0])
            if pickid:
                wf_service.trg_validate(uid, 'stock.picking', pickid, 'button_confirm', cr)
        if new_moves:
            new_moves += self.create_chained_picking(cr, uid, new_moves, context)
        return new_moves
# OLD Version 6 alpha     
#    def action_confirm(self, cr, uid, ids, context=None):
#        """ Confirms stock move.
#        @return: List of ids.
#        """
#        moves = self.browse(cr, uid, ids)
#        self.write(cr, uid, ids, {'state': 'confirmed'})
#        res_obj = self.pool.get('res.company')
#        location_obj = self.pool.get('stock.location')
#        move_obj = self.pool.get('stock.move')
#        wf_service = netsvc.LocalService("workflow")
#
#        def create_chained_picking(self, cr, uid, moves, context=None):
#            new_moves = []
#            if context is None:
#                context = {}
#            for picking, todo in self._chain_compute(cr, uid, moves, context=context).items():
#                ptype = todo[0][1][5] and todo[0][1][5] or location_obj.picking_type_get(cr, uid, todo[0][0].location_dest_id, todo[0][1][0])
#                pick_name = picking.name or ''
#                if picking:
#                    pickid = self._create_chained_picking(cr, uid, pick_name,picking,ptype,todo,context)    
#                else:
#                    pickid = False
#                for move, (loc, dummy, delay, dummy, company_id, ptype) in todo:                       
#                    new_id = move_obj.copy(cr, uid, move.id, {
#                        'location_id': move.location_dest_id.id,
#                        'location_dest_id': loc.id,
#                        'date_moved': time.strftime('%Y-%m-%d'),
#                        'picking_id': pickid,
#                        'state': 'waiting',
#                        'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', context=context)  ,
#                        'move_history_ids': [],
#                        'date': (datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') + relativedelta(days=delay or 0)).strftime('%Y-%m-%d'),
#                        'move_history_ids2': []}
#                    )
#                    if pickid:
#                        stock_picking = self.pool.get('stock.picking')
#                        linkpicking = stock_picking.browse(cr,uid,pickid)
#                        if linkpicking.origin.find("SO")>=0:
#                            #In this case we need to change the stock move value
#                            stock_move = self.pool.get('stock.move')
#                            res3 = stock_move.search(cr,uid,[('picking_id','=',pickid)])
#                            tmp_loc_src = linkpicking.sale_id.shop_id.warehouse_id.lot_output_id.id
#                            tmp_loc_dst = linkpicking.sale_id.shop_id.warehouse_id.so_output_output.id 
#                            move_obj.write(cr, uid, [new_id], {
#                                         'location_id': tmp_loc_src,
#                                         'location_dest_id': tmp_loc_dst,
#                                         })
#                    move_obj.write(cr, uid, [move.id], {
#                        'move_dest_id': new_id,
#                        'move_history_ids': [(4, new_id)]
#                    })
#                    new_moves.append(self.browse(cr, uid, [new_id])[0])
#                if pickid:
#                    wf_service.trg_validate(uid, 'stock.picking', pickid, 'button_confirm', cr)
#            if new_moves:
#                create_chained_picking(self, cr, uid, new_moves, context)
#        create_chained_picking(self, cr, uid, moves, context)
#        return []    
    
prisme_stock_move()
