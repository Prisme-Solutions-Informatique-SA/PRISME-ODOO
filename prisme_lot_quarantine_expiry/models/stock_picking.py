from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = "stock.picking"

    expiry_lot_batch_id = fields.Many2one('stock.production.lot', string='Lot / Batch')

    def _create_lots_for_picking(self):
        ''' @override: Override this method for create/write use_date and removal_date '''
        Lot = self.env['stock.production.lot']
        for pack_op_lot in self.mapped('pack_operation_ids').mapped('pack_lot_ids'):
            if not pack_op_lot.lot_id:
                lot = Lot.create({
                    'name': pack_op_lot.lot_name,
                    'product_id': pack_op_lot.operation_id.product_id.id,
                    'use_date': pack_op_lot.use_date,
                    'removal_date': pack_op_lot.removal_date,
                })
                pack_op_lot.write({'lot_id': lot.id})
            else:
                pack_op_lot.lot_id.write({
                    'use_date': pack_op_lot.use_date or pack_op_lot.lot_id.use_date,
                    'removal_date': pack_op_lot.removal_date or pack_op_lot.lot_id.removal_date,
                })
        self.mapped('pack_operation_ids').mapped('pack_lot_ids').filtered(lambda op_lot: op_lot.qty == 0.0).unlink()
    create_lots_for_picking = _create_lots_for_picking

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
