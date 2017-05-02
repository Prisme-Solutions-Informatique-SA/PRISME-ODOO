from odoo import api, fields, models, _


class prisme_warranty_type(models.Model):
    _name = "prisme.warranty.type"
    
    name = fields.Char("Name", required=True, unique=True)
    description = fields.Text("Description")
    
    _sql_constraints = [("name_uniq", "unique(name)", "Type must be unique")]
