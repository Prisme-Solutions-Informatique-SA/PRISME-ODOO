from odoo import api, fields, models, _

class ProcurementRule(models.Model):

    _inherit = 'procurement.rule'

    @api.model
    def _set_rules_to_route_quarantine(self):
        ''' This method is called from data file to create rule of route quarantine '''
        warehouse_id = self.env.ref('stock.warehouse0')
        lot_stock_id = warehouse_id.lot_stock_id        
        quarantine_route_id = self.env.ref('prisme_lot_quarantine_expiry.route_warehouse_svs')
        if not quarantine_route_id:
            quarantine_route_id = self.env['stock.location.route'].search([('name', 'like', _('Quarantine'))], limit=1)
        virtual_location_id = self.env.ref('stock.location_procurement')
        if not virtual_location_id:
            virtual_location_id = self.env['stock.location'].search([('name', 'like', _('Procurements'))], limit=1)
        if quarantine_route_id:
            # Added rules in route "quarantine" for "YourWarehouse" which is already created from data file
            quarantine_route_id.write({'pull_ids': [(0, 0, {
                                'name': u"%s: Stock -> Virtual" % warehouse_id.code,
                                'action': 'move',
                                'location_id': virtual_location_id.id,
                                'location_src_id': warehouse_id.lot_stock_id.id, 
                                'procure_method': 'make_to_stock',
                                'picking_type_id': warehouse_id.out_type_id.id,
                                'warehouse_id': warehouse_id.id,
                            }),(0, 0, {
                                'name': u"%s: Virtual -> Stock" % warehouse_id.code,
                                'action': 'move',
                                'location_id': warehouse_id.lot_stock_id.id,
                                'location_src_id': virtual_location_id.id,
                                'picking_type_id': warehouse_id.in_type_id.id,
                                'procure_method': 'make_to_order',
                                'warehouse_id': warehouse_id.id,
                            })], 'warehouse_ids': [(4, warehouse_id.id)]
                        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: