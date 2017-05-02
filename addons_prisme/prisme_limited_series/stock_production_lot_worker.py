from openerp import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class stock_production_lot(models.Model):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'
    
    limited_series_no = fields.Char('Limited Series No')
    limited_series_of = fields.Char('Of')
    
    @api.one
    @api.constrains('limited_series_of')
    def _check_series_completion(self):
        for lot in self.browse(cr, uid, ids):
            if lot.limited_series_of:
                 if not lot.limited_series_no:
                     raise ValidationError('You must specify a Limited Series No or remove "Of" value')