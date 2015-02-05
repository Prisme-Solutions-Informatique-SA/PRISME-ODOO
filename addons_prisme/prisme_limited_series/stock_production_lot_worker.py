from osv import osv, fields

class stock_production_lot(osv.osv):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'
    
    _columns = {
        'limited_series_no': fields.char('Limited Series No', 255),
        'limited_series_of': fields.char('Of', 255),
    }
    
    def _check_series_completion(self, cr, uid, ids):
        ok = True
        for lot in self.browse(cr, uid, ids):
            if lot.limited_series_of:
                 if not lot.limited_series_no:
                     ok = False
        return ok

    _constraints = [
                    (_check_series_completion, 'You must specify a Limited ' + \
                     'Series No or remove "Of" value',
                     ['limited_series_no', 'limited_series_of']),
                      ]
      
stock_production_lot()
