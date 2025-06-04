from odoo import fields, models


class PrismePostitTag(models.Model):
    _name = 'prisme.postit.tag'
    _description = "Postit Tag"
    name = fields.Char(string="Tag name", required=True)
