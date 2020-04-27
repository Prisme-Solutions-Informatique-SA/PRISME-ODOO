# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2019 Prisme Solutions Informatique SA <http://prisme.ch>
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
#    Project ID:    OERP-002-04  
#	 Phabricator: 	T945
#
#    Modifications:
#    $01		19.09.2019		Added new 'state' field
#
##########################################################################
from odoo import models, fields, _


class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"
	
	
	state = fields.Selection(related='invoice_id.state', string=_('State'), store=True)
	date_invoice = fields.Date(related='invoice_id.date_invoice', string=_('Invoice Date'), store=True)
	journal_id = fields.Many2one(related='invoice_id.journal_id', relation='account.journal', string=_('Journal'), store=True)
	currency_id = fields.Many2one(related='invoice_id.currency_id', relation='res.currency', string=_('Currency'), store=True)
	local_currency_id = fields.Many2one('res.currency', string='Local Currency', default=lambda self: self.env.user.company_id.currency_id, store=True)

	
