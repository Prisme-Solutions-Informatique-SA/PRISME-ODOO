from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_assign(self):
        ''' @override: Override this method for auto assign lot of created picking from procurement order '''
        res = True
        for move in self:
            move = move.with_context(expiry_lot_batch_id=move.picking_id.expiry_lot_batch_id)
            res = super(StockMove, move).action_assign()
            # On assigning a picking, a related lot will be automatically assigned to pack_operation_product_ids.
            if move.picking_id.expiry_lot_batch_id:
                for link in move.linked_move_operation_ids:
                    for pack_lot in link.operation_id.pack_lot_ids:
                        min_qty = min(pack_lot.qty_todo, link.move_id.product_uom_qty)
                        pack_lot.write({'qty': min_qty})
                        if not (link.move_id.product_uom_qty - min_qty):
                            break
                    link.operation_id.save()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: