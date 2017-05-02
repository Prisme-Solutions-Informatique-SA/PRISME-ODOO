
from odoo import api, fields, models, SUPERUSER_ID, _



class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"
    
    validator = fields.Many2one('res.users', string='Validator')


    @api.multi
    def button_approve(self, force=False):
        self.write({'state': 'purchase', 'validator' : self._uid})
        self._create_picking()
        if self.company_id.po_lock == 'lock':
            self.write({'state': 'done', 'validator' : self._uid})
        return {}