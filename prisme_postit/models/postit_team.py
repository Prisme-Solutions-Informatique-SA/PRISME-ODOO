# -*- coding: utf-8 -*-
from odoo  import fields, models


class prisme_postit_team(models.Model):
    _name = 'prisme.postit.team'
    _description = "Postit Team"
    name = fields.Char(string="Team", required=True)
