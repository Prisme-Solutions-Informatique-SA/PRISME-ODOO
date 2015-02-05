from osv import fields, osv
#----------------------------------------------------------
# Stock Warehouse
#----------------------------------------------------------
class prisme_stock_warehouse(osv.osv):
    _name = 'stock.warehouse'
    _inherit = 'stock.warehouse' 
    
    def get_mo_cons_location(self, cr, uid, ids, field, arg, context=None):
        res = {}
        warehouses = self.browse(cr, uid, ids, context=context)
        for warehouse in warehouses:
            res[warehouse.id] = warehouse.mo_cons_location.id
        return res
    
    def get_lot_output_id_2(self, cr, uid, ids, field, arg, context=None):
        res = {}
        warehouses = self.browse(cr, uid, ids, context=context)
        for warehouse in warehouses:
            res[warehouse.id] = warehouse.lot_output_id.id
        return res

    def get_lot_output_id_3(self, cr, uid, ids, field, arg, context=None):
        res = {}
        warehouses = self.browse(cr, uid, ids, context=context)
        for warehouse in warehouses:
            res[warehouse.id] = warehouse.lot_output_id.id
        return res
    
    
    
    _columns = {
        'mo_cons_location': fields.many2one('stock.location',  
                                            required=False, 
                                            domain=[('usage', '<>', 'view')]),
        # Field used to not put element twice in a view.
        'mo_cons_location_2': fields.function(get_mo_cons_location,
                           type='many2one', method=True, store=False,
                           obj='stock.location'),
        'lot_output_id_2': fields.function(get_lot_output_id_2,
                                           type='many2one', method=True,
                                           store=False,
                                           obj='stock.location'),
        'lot_output_id_3': fields.function(get_lot_output_id_3,
                                           type='many2one', method=True,
                                           store=False,
                                           obj='stock.location'),
        'so_picking_dest': fields.many2one('stock.location', 
                                            required=False, 
                                            domain=[('usage', '<>', 'view')]),
    }
prisme_stock_warehouse()
