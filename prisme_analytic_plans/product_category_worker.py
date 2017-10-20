from osv import osv, fields

class product_category(osv.osv):

    _name = 'product.category'
    _inherit = 'product.category'
    
    def _get_category(selfself, cr, uid, ids, context={}):
        return ids
    
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        return super(product_category, self)._name_get_fnc(cr, uid, ids, prop,
                                                           unknow_none,
                                                           context=context)
    
    _columns = {
        'complete_name': fields.function(_name_get_fnc, method=True,
                                         store={ 
                                                'product.category': (
                                                        _get_category,
                                                        ['name', 'parent_id'],
                                                        10)
                                                                        },
                                         type='char', size=255, string='Name'),
    }
    
    # Order overridden to order by name if no sequence
    _order = 'sequence, complete_name, name'
    
product_category()
