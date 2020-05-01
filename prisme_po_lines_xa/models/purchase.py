# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2020 Prisme Solutions Informatique SA <http://prisme.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#    You should have received a copy of the GNU Lesser General Public Lic
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project ID:    OERP-007-03 - T524
#
#    Modifications:
#
##########################################################################
from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    move_ids = fields.One2many('stock.move', 'purchase_line_id', string='Reservation', readonly=True, ondelete='set null', copy=False)
    amount_local_currency = fields.Monetary(string='Amount in local currency', store=True, readonly=True, compute='_amount_local')
    local_currency = fields.Many2one(string="Local Currency", related='company_id.currency_id',store=True)
    
    @api.depends('price_subtotal')
    def _amount_local(self):
        for record in self:
            company_currency = record.company_id.currency_id.id
            amount_local_currency = record.price_subtotal
            
            if record.currency_id.id != company_currency:
                rate = record.currency_id.rate
                if rate and rate != 0.0:
                    amount_local_currency = record.price_subtotal / rate 
                
            record.amount_local_currency = amount_local_currency