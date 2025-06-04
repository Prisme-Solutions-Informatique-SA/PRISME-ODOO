from odoo import fields, models


class PrismePostitTeam(models.Model):
    _name = 'prisme.postit.team'
    _description = "Postit Team"
    name = fields.Char(string="Team", required=True)
