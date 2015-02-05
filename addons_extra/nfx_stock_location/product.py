from openerp.osv import osv, fields


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'

    def get_stock_locations(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result

        context['only_with_stock'] = True

        for id in ids:
            context['product_id'] = id
            location_obj = self.pool.get('stock.location')
            result[id] = location_obj.search(cr, uid, [('usage', '=', 'internal')], context=context)

        return result


    _columns = {
        'stock_locations': fields.function(get_stock_locations, type='one2many', relation='stock.location', string='Stock by Location'),
    }

product_product()
