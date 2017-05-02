from datetime import datetime
from odoo import models, fields, api, _

class product_product_stock_rotation(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def _get_stock_at_date(self, product_id, date_str):
        
        date = datetime.strptime(date_str, '%Y-%m-%d').date()   
        datetime_max = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        obj_stock_history = self.env['stock.history']
        stock_historys = obj_stock_history.search(
                            [('date', '<=', str(datetime_max)),
                             ('product_id', '=', product_id),
                                ])
        quantity = 0.0
        for stock_history in stock_historys:
            quantity += stock_history.quantity
        return quantity
        

    
    def _get_average_stock(self):              
        for product in self:
            stock_quantity_begin = self._get_stock_at_date(product.id,
                self.env.context.get('period_begin'))
            stock_quantity_end = self._get_stock_at_date(product.id,
                self.env.context.get('period_end'))
            product.average_stock = (stock_quantity_begin + stock_quantity_end) / 2.0
    
    def _get_sold_quantity(self):

        for product in self:
            try:
                date_begin = datetime.strptime(self.env.context['period_begin'],
                                           '%Y-%m-%d').date()
                period_begin = datetime(date_begin.year, date_begin.month,
                                    date_begin.day, 0, 0, 0)
                date_end = datetime.strptime(self.env.context['period_end'],
                                           '%Y-%m-%d').date()
                period_end = datetime(date_end.year, date_end.month,
                                  date_end.day, 23, 59, 59)
                stock_moves = self.env['stock.move'].search(
                                            [('date', '>', str(period_begin)),
                                             ('date', '<', str(period_end)),
                                             ('product_id.id', '=', product.id),
                                             ('picking_type_id.code', '=', 'outgoing'),
                                             ('state', '=', 'done'),
                                             ])
                quantity = 0.0
                for stock_move in stock_moves:
                    quantity += stock_move.product_qty
                
                product.sold_quantity = quantity
            except: #Catch error in duplication function because periods are not available
                product.sold_quantity = 0
    
    def _compute_stock_rotation(self):
        for product in self:
            if product.average_stock != 0.0:
                product.stock_rotation = product.sold_quantity / product.average_stock
            else:
                product.stock_rotation = 0.0
    
    def _get_analytic_distribution(self):        
        for product in self:        
            account_invoice_lines= self.env['account.invoice.line'].search([('product_id.id', '=', product.id)])
            
            product.analytic_distribution.ids = [account_invoice_line.analytics_id.id for account_invoice_line in account_invoice_lines]
    
    

    average_stock = fields.Float(compute='_get_average_stock', string='Average Stock')
    sold_quantity = fields.Float(compute='_get_sold_quantity', string='Sold Quantity')
    stock_rotation = fields.Float(compute='_compute_stock_rotation', string='Stock Rotation')
    analytic_distribution = fields.One2many(compute='_get_analytic_distribution', obj="account.analytic.plan.instance", string='Analytic distribution')

