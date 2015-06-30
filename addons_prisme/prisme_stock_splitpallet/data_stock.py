from osv import osv, fields 
import netsvc
import hr_timesheet_invoice
from datetime import datetime
import openerp.addons.decimal_precision as dp
from math import fmod
import time

class purchase_order_cplg(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    def _prepare_order_line_move_qty(self, cr, uid, order, order_line, picking_id,spqty,lot, context=None):
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': spqty,
            'product_uos_qty': spqty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'type':'in',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': order_line.price_unit,
            'prodlot_id': lot,
        }

    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Creates pickings and appropriate stock moves for given order lines, then
        confirms the moves, makes them available, and confirms the picking.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: purchase order to which the order lines belong
        :param list(browse_record) order_lines: purchase order line records for which picking
                                                and moves should be created.
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if omitted.
        :return: list of IDs of pickings used/created for the given order lines (usually just one)
        """

        if not picking_id:
            picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
        todo_moves = []
        stock_move = self.pool.get('stock.move')
	stock_lot = self.pool.get('stock.production.lot')
        wf_service = netsvc.LocalService("workflow")
        for order_line in order_lines:
            if not order_line.product_id:
                continue
            if order_line.product_id.type in ('product', 'consu'):
                #Calcul du nombre de ligne a creer et du rest pour la derniere ligne
                qty_pallet=order_line.product_id.qty_pallet
		if (qty_pallet==0):				#Si qty_pallet est 0 ou non rempli
		   qty_pallet=99999999
		product_qty=order_line.product_qty              #Calcul du modulo et reste
                rest=fmod(product_qty,qty_pallet)
                nbr_pallet=0
                if (rest!=0):                                   #Calcul du nombre de palette
                   nbr_pallet=(product_qty-rest)/qty_pallet
                else:
                   nbr_pallet=product_qty/qty_pallet
                while (nbr_pallet!=0):                          #Creation des mouvements de stock pour chaque palette avec un lot
                  newlot=stock_lot.create(cr, uid,{'product_id':order_line.product_id.id,'entry_stock':order_line.move_dest_id.id,'no_lot':order_line.no_lot,'no_lot_supplier':order_line.no_lot_supplier,'life_date':order_line.limit_date,'date':order_line.lot_create_date,})
		  move = stock_move.create(cr, uid, self._prepare_order_line_move_qty(cr, uid, order, order_line, picking_id,qty_pallet,newlot, context=context))
                  if order_line.move_dest_id and order_line.move_dest_id.state != 'done':
                    order_line.move_dest_id.write({'location_id': order.location_id.id})
                  todo_moves.append(move)
                  nbr_pallet=nbr_pallet-1
                if (rest!=0):					#Creation du mouvement de stock pour le reste avec un lot
                  newlot=stock_lot.create(cr, uid,{'product_id':order_line.product_id.id,'entry_stock':order_line.move_dest_id.id,'no_lot':order_line.no_lot,'no_lot_supplier':order_line.no_lot_supplier,'life_date':order_line.limit_date,'date':order_line.lot_create_date,})
                  move = stock_move.create(cr, uid, self._prepare_order_line_move_qty(cr, uid, order, order_line, picking_id,rest,newlot, context=context))
                  if order_line.move_dest_id and order_line.move_dest_id.state != 'done':
                    order_line.move_dest_id.write({'location_id': order.location_id.id})
                  todo_moves.append(move)
        stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves)
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return [picking_id]

purchase_order_cplg()


class purchase_order_line_cplg(osv.osv):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"
    _columns = {
        'no_lot': fields.char('No Lot', size=64, required=False, translate=False),
        'no_lot_supplier': fields.char('No Lot Supplier', size=64, required=False, translate=False),
        'limit_date':fields.datetime('Limit Date', select=True),
        'lot_create_date': fields.datetime('Lot creation Date', required=True),
    }

    _defaults = {
        'lot_create_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

purchase_order_line_cplg()

