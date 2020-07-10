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
#    Phabricator :   T515
#
##########################################################################
from odoo import api, fields, models

class stock_production_lot(models.Model):
    _name = "stock.production.lot"
    _inherit = "stock.production.lot"
    

    description = fields.Text("Lot Description")
    model_no = fields.Char("Model No")
    customer = fields.Many2one("res.partner", string="Customer")
    user = fields.Char("End User")
    user_department = fields.Char("End User Dept")
    installation_date = fields.Date("Installation Date")
    customer_invoice = fields.Many2one("account.move",
                                        string="Customer Invoice",
                                        domain="[('type','=','out_invoice')]",)
    attachments = fields.Text("Attachments")
    manufacturer = fields.Char("Manufacturer")
    manufact_item_no = fields.Char("Part. Number")
    supplier = fields.Many2one("res.partner", string="Supplier")
    supplier_item_no = fields.Char("Supplier Item No")

    supplier_invoice = fields.Many2one("account.move", string="Supplier Invoice", domain="[('type','=','in_invoice')]")
    delivery_date = fields.Date("Delivery Date")
    remarks = fields.Text("Remarks")
                
    warranties_ids = fields.One2many('prisme.warranty.warranty', 'lot_id', 'Warranties')
    end_life_date = fields.Date("End Life Delivery Date")

    @api.onchange('product_id')
    def onchange_product(self):
        product_description = ''
        if(self.product_id and self.product_id.product_tmpl_id and self.product_id.product_tmpl_id.description):
            product_description = self.product_id.product_tmpl_id.description
            
        self.description = product_description
        

    def write(self, vals):
        res = super(stock_production_lot,self).write(vals)
        for w in self.warranties_ids:
            w.partner = self.customer
        
        return res
