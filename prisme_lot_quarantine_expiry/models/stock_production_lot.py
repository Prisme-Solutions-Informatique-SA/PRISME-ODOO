from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _


class production_lot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def create_procurement_of_expiry_lot(self):
        '''
        CRON JOB: This method generates procurement order which creates delivery
        and receipt pickings of expiry batch/lot id 
        '''
        def _find_parent(location):
            ''' @return: Return most parent location of location '''
            parent_loc = location
            while parent_loc.location_id:
                if parent_loc.location_id.usage == 'view':
                    break
                parent_loc = parent_loc.location_id
            return parent_loc
        current_date = datetime.strptime(str(datetime.now().date()), DEFAULT_SERVER_DATE_FORMAT)
        stock_picking_obj = self.env['stock.picking']
        stock_loc_route_obj = self.env['stock.location.route']
        procurement_order_obj = self.env['procurement.order']
        warehouse_obj = self.env['stock.warehouse']
        for lot in self.search([]):
            if lot.removal_date and datetime.strptime(str(lot.removal_date), DEFAULT_SERVER_DATETIME_FORMAT) < current_date:
                procure = dict()
                # prepared a dictionary to store locations and it's total quantity to create picking for that
                for quant in lot.quant_ids.filtered(lambda q: q.location_id.usage == 'internal'):
                    parent_loc = _find_parent(quant.location_id)
                    if not procure.get(parent_loc):
                        procure[parent_loc] = [0, quant.product_uom_id.id]
                    procure[parent_loc][0] += quant.qty
                for location, quantity_uom in procure.items():
                    if not quantity_uom[0]:
                        continue
                    domain = [('location_id', '=', location.id), ('location_dest_id', '=', location.id),
                                ('expiry_lot_batch_id', '=', lot.id), ('state', 'not in', ['done', 'cancel'])]
                    # creating procurement for expired lot
                    if not stock_picking_obj.search(domain):
                        route_id = self.env.ref('prisme_lot_quarantine_expiry.route_warehouse_svs')
                        warehouse_id = warehouse_obj.search([('lot_stock_id', '=', location.id)], limit=1)
                        procurement = procurement_order_obj.create({
                                'name': lot.product_id.name or '',
                                'product_id': lot.product_id.id,
                                'product_qty': quantity_uom[0],
                                'product_uom': lot.product_id.uom_id.id,
                                'warehouse_id': warehouse_id.id,
                                'location_id': location.id,
                                'route_ids': [(4, route_id.id)],
                                'origin': self.env['ir.sequence'].next_by_code('procurement.order') or _('New')
                            })
                        procurement.run()
                        if procurement:
                            picking_id = stock_picking_obj.search([('origin', '=', procurement.origin)])
                            if picking_id:
                                # the picking from stock to virtual, set it's state to done state
                                picking_id.write({'expiry_lot_batch_id': lot.id})
                                for line in picking_id.move_lines:
                                    for move_orig in line.move_orig_ids:
                                        move_orig.picking_id.write({'expiry_lot_batch_id': lot.id})
                                        move_orig.picking_id.action_assign()
                                        move_orig.picking_id.do_new_transfer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: