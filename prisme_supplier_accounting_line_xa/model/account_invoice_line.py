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
#    Project ID:    OERP-002-05 - T496
#
##########################################################################
from odoo import models, fields, _


class AccountInvoiceLine(models.Model):
	_inherit = "account.move.line"
	
	date_invoice = fields.Date(related='move_id.invoice_date', string=_('Invoice Date'))
	journal_id = fields.Many2one(related='move_id.journal_id', relation='account.journal', string=_('Journal'))
	invoice_currency = fields.Char(related='move_id.currency_id.name', string=_('Invoice Currency'), store=True)
	origin = fields.Char(related='move_id.invoice_origin', string=_('Source Document'))
	invoice_payment_state = fields.Selection(related='move_id.invoice_payment_state', string=_('Payment State'), store=True)