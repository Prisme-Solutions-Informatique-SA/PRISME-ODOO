# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha / Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields


class AccountInvoiceLine(osv.Model):
	_inherit = "account.invoice.line"
	_columns = {
		'state': fields.related('invoice_id', 'state', type='char', size=64, string='State'),
		'journal_id': fields.related('invoice_id', 'journal_id', relation='account.journal', type='many2one', string='Journal', help='field'),
		'currency_id': fields.related('invoice_id', 'currency_id', relation='res.currency', type='many2one', string='Currency', help='field'),
		'analytic_journal_id': fields.related('invoice_id', 'analytic_journal_id', relation='account.analytic.journal', type='many2one', string='Journal Analytique', help='field'),
	}