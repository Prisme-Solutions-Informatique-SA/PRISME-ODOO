from odoo import models, fields, api, _

class hr_employee(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"
     
    product_id = fields.Many2one('product.product', 'Product')