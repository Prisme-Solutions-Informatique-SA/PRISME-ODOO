from odoo import api, exceptions, fields, models, _

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _get_quarantine_route_id(self):
        ''' @return: Return quarantine route id '''
        quarantine_route_id = self.env.ref('prisme_lot_quarantine_expiry.route_warehouse_svs')
        if not quarantine_route_id:
            quarantine_route_id = self.env['stock.location.route'].search([('name', 'like', _('Quarantine'))], limit=1)
        if not quarantine_route_id:
            raise exceptions.UserError(_('Can\'t find any generic Quarantine route.'))
        return quarantine_route_id

    @api.model
    def create(self, vals):
        ''' @override: Override create method to create quarantine rules on warehouse creation '''
        res = super(StockWarehouse, self).create(vals)
        procurement_rule_obj = self.env['procurement.rule']
        route_id = self._get_quarantine_route_id()
        if route_id:
            virtual_location_id = self.env.ref('stock.location_procurement').id
            if not virtual_location_id:
                virtual_location_id = self.env['stock.location'].search([('name', 'like', _('Procurements'))], limit=1).id
            if not virtual_location_id:
                raise exceptions.UserError(_('Can\'t find any Virtual Locations.'))
            route_id.write({'pull_ids': [(0,0, {
                                'name': u"%s: Stock -> Virtual"%res.code,
                                'action': 'move',
                                'location_id': virtual_location_id,
                                'location_src_id': res.lot_stock_id.id, 
                                'procure_method': 'make_to_stock',
                                'picking_type_id': res.out_type_id.id,
                                'warehouse_id': res.id,
                            }),(0, 0, {
                                'name': u"%s: Virtual -> Stock"%res.code,
                                'action': 'move',
                                'location_id': res.lot_stock_id.id,
                                'location_src_id': virtual_location_id,
                                'picking_type_id': res.in_type_id.id,
                                'procure_method': 'make_to_order',
                                'warehouse_id': res.id,
                            })], 'warehouse_ids': [(4, res.id)]})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        