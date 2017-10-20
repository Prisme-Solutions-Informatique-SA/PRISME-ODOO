from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import fields
from osv import osv
from tools.translate import _
import netsvc
import time

class prisme_procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _name = 'procurement.order'

    # Method copied from addons/mrp/procurement.py    
    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            loc_id = procurement.location_id.id
            newdate = datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.product_id.product_tmpl_id.produce_delay or 0.0)
            newdate = newdate - relativedelta(days=company.manufacturing_lead)
            
            # Modified the 19.11.2012 to use the locations defined on products
            # if defined. Modification by Damien Raemy
            
            #Get the corresponding warehouse
            warehouse = self.pool.get('stock.warehouse')
            warehouse_id = warehouse.search(cr, uid, [('company_id', '=', procurement.company_id.id)])
            warehouse_obj = warehouse.browse(cr, uid, warehouse_id)[0]
             
            #Get the corresponding warehouse
            warehouse = self.pool.get('stock.warehouse')
            warehouse_id = warehouse.search(cr, uid, [('company_id', '=', procurement.company_id.id)])
            warehouse_obj = warehouse.browse(cr, uid, warehouse_id)[0]
            if procurement.product_id.shopfloor_location:
                src_location = procurement.product_id.shopfloor_location.id
            else:
                # Standard case
                src_location = procurement.location_id.id
            change_location = True
            if procurement.product_id.storage_location:
                dst_location = procurement.product_id.storage_location.id
            else:
                # Standard Case
                change_location = False
                dst_location = procurement.location_id.id
            # Modification end
            
            produce_id = production_obj.create(cr, uid, {
                'origin': procurement.origin,
                'product_id': procurement.product_id.id,
                'product_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                # Modified the 19.11.2012 by Damien Raemy to use the values
                # redefined
                'location_src_id': src_location,
                'location_dest_id': dst_location,
                # Original lines:
                #'location_src_id': procurement.location_id.id,
                #'location_dest_id': procurement.location_id.id,
                # Modification end
                'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                'move_prod_id': res_id,
                'company_id': procurement.company_id.id,
            })
            res[procurement.id] = produce_id
            self.write(cr, uid, [procurement.id], {'state': 'running'})
            bom_result = production_obj.action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            # Modification begin
            # We don't want an automatic acceptation of MO
            #wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
            # Modification End
            
            # Modified the 19.11.2012 by Damien Raemy to use the source and
            # location redefined.
            move_obj.write(cr, uid, [res_id],
                           {'location_id':src_location})
            # In standard case, the destination is not set here. 
            if change_location:
                move_obj.write(cr, uid, [res_id],
                               {'location_dest_id':dst_location}) 
            # Original lines: 
            #move_obj.write(cr, uid, [res_id],
            #        {'location_id': procurement.location_id.id})
            # Modification end
        return res
        
prisme_procurement_order()
