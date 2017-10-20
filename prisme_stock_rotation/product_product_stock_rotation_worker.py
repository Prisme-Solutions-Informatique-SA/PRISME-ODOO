from osv import osv, fields
from datetime import datetime

class product_product_stock_rotation(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def _get_stock_at_date(self, cr, uid, product_id, date_str, context):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()   
            datetime_from = datetime(date.year, date.month, date.day, 0, 0, 0)
            datetime_to = datetime(date.year, date.month, date.day, 23, 59, 59)
            context['from_date'] = str(datetime_from)
            context['to_date'] = str(datetime_to)
            product = self.browse(cr, uid, product_id, context=context)
            return product.qty_available
        except:   #Catch error in duplication function because dat_str is not available
            return 0
    
    def _get_average_stock(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for product in self.browse(cr, uid, ids):
            stock_quantity_begin = self._get_stock_at_date(cr, uid, product.id,
                context.get('period_begin'), context)
            stock_quantity_end = self._get_stock_at_date(cr, uid, product.id,
                context.get('period_end'), context)
            res[product.id] = (stock_quantity_begin + stock_quantity_end) / 2.0
        return res
    
    def _get_sold_quantity(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        obj_stock_move = self.pool.get('stock.move')
        for product in self.browse(cr, uid, ids, context=context):
            try:
                date_begin = datetime.strptime(context['period_begin'],
                                           '%Y-%m-%d').date()
                period_begin = datetime(date_begin.year, date_begin.month,
                                    date_begin.day, 0, 0, 0)
                date_end = datetime.strptime(context['period_end'],
                                           '%Y-%m-%d').date()
                period_end = datetime(date_end.year, date_end.month,
                                  date_end.day, 23, 59, 59)
                stock_move_ids = obj_stock_move.search(cr, uid,
                                            [('date', '>', str(period_begin)),
                                             ('date', '<', str(period_end)),
                                             ('product_id.id', '=', product.id),
                                             ('picking_id.type', '=', 'out'),
                                             ('picking_id.state', '=', 'done'),
                                             ])
                quantity = 0.0
                for stock_move in obj_stock_move.browse(cr, uid, stock_move_ids):
                    quantity += stock_move.product_qty
                
                res[product.id] = quantity
            except: #Catch error in duplication function because periods are not available
                res[product.id] = 0
        return res
    
    def _compute_stock_rotation(self, cr, uid, ids, field_name, arg,
                                context=None):
        res = {}
        
        for product in self.browse(cr, uid, ids, context=context):
            if product.average_stock != 0.0:
                res[product.id] = product.sold_quantity / product.average_stock
            else:
                res[product.id] = 0.0
        return res
    
    _columns = {
                'average_stock': fields.function(_get_average_stock,
                    type='float', digits=(16, 2), string='Average Stock',
                    method=True),
                'sold_quantity': fields.function(_get_sold_quantity,
                    type='float', digits=(16, 2), string='Sold Quantity',
                    method=True),
                'stock_rotation': fields.function(_compute_stock_rotation,
                    type='float', digits=(16, 8), string='Stock Rotation',
                    method=True),
               } 
    
product_product_stock_rotation()
