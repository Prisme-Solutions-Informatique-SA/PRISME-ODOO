from osv import osv, fields
from tools import float_compare
from tools.translate import _
import tools

class mrp_routing_workcenter_prisme(osv.osv):
    _name = 'mrp.routing.workcenter'
    _inherit = 'mrp.routing.workcenter'
    _columns = {
               'tool_product_id': fields.many2one('product.product', 'Tool'),
               }
mrp_routing_workcenter_prisme()

class mrp_production_prisme(osv.osv):
    _name = 'mrp.production.workcenter.line'
    _inherit = 'mrp.production.workcenter.line'
    _columns = {
                'tool_product_id': fields.many2one('product.product', 'Tool'),
                'reserved': fields.boolean('Reserved'),
                }
mrp_production_prisme()

class mrp_bom_prisme(osv.osv):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'
    def _bom_explode(self, cr, uid, bom, factor, properties=[], addthis=False, level=0, routing_id=False):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)
            
            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    # Modified the 29.10.12 by Damien Raemy to resolve bug 2793
                    # Original lines:
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    #mult = wc_use.workcenter_id.capacity_per_cycle / factor
                    
                    # Modification end
                    cycle = mult * wc_use.cycle_nbr
                    #import pdb;pdb.set_trace()
                    result2.append({
                        'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
                        'workcenter_id': wc.id,
                        'sequence': level+(wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                        'tool_product_id': wc_use.tool_product_id.id
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2
mrp_bom_prisme()
#code isn't in any module
def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r

