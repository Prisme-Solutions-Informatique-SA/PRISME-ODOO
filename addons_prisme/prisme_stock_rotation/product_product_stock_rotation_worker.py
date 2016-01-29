from datetime import datetime
from openerp.osv import fields, osv, expression

class product_product_stock_rotation(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def _get_stock_at_date(self, cr, uid, product_id, date_str, context):
        
        date = datetime.strptime(date_str, '%Y-%m-%d').date()   
        datetime_max = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        obj_stock_history = self.pool.get('stock.history')
        stock_history_ids = obj_stock_history.search(cr, uid,
                            [('date', '<=', str(datetime_max)),
                             ('product_id', '=', product_id),
                                ])
        quantity = 0.0
        for stock_history in obj_stock_history.browse(cr, uid, stock_history_ids):
            quantity += stock_history.quantity
        return quantity
        

    
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
                                             ('picking_type_id.code', '=', 'outgoing'),
                                             ('state', '=', 'done'),
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
    
    def _get_analytic_distribution(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        
        for product in self.browse(cr, uid, ids, context=context):
        
            obj_account_invoice_line = self.pool.get('account.invoice.line')
            account_invoice_line_ids = obj_account_invoice_line.search(cr, uid,
                                            [('product_id.id', '=', product.id),
                                            ])
            
            res[product.id] = []
            res[product.id].extend([account_invoice_line.analytics_id.id for account_invoice_line in obj_account_invoice_line.browse(cr, uid, account_invoice_line_ids)])
            
        
        return res
    
    def _search_analytic_distribution_name(self, cr, uid, model_again, field_name, criterion, context=None):
        
        ids = []
        obj_account_invoice_line = self.pool.get('account.invoice.line')
        account_invoice_line_ids = obj_account_invoice_line.search(cr, uid,
                                            [('analytics_id.name', 'ilike', criterion[0][2]),
                                            ])
        ids.extend([account_invoice_line.product_id.id for account_invoice_line in obj_account_invoice_line.browse(cr, uid, account_invoice_line_ids)])
            
        
        return [('id','in', ids)]
    
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
                'analytic_distribution': fields.function(_get_analytic_distribution,
                    type='one2many', obj="account.analytic.plan.instance", string='Analytic distribution',
                    method=True, fnct_search=_search_analytic_distribution_name),
               } 
    
product_product_stock_rotation()
