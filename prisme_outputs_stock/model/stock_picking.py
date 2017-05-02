from openerp import models, fields, api, _

class stock_picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"
    
    psi_transporter = fields.Char("Transporter")
