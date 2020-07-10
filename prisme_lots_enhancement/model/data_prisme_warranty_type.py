# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2020 Prisme Solutions Informatique SA <http://prisme.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public Lic
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project ID :    OERP-006-02
#     Phabricator :    T515
#
##########################################################################
from odoo import fields, models

class prisme_warranty_type(models.Model):
    _name = "prisme.warranty.type"
    _description = "Prisme Warranty Type"
    
    name = fields.Char("Name", required=True, unique=True)
    description = fields.Text("Description")
    
    _sql_constraints = [("name_uniq", "unique(name)", "Type must be unique")]
