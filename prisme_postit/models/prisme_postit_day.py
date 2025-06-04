from odoo import fields, models


class PrismePostitDay(models.Model):
    _name = 'prisme.postit.day'
    _description = "Postit Day"

    name = fields.Char(string="Day name", required=True, translate=True)
    nbr = fields.Integer('Day number', required=True)
