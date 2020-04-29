# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2016 Prisme Solutions Informatique SA <http://prisme.ch>
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
#    Project ID:    OERP-004-02 - T508
#
#    Modifications:
#
##########################################################################
from odoo import models


class account_move(models.Model):
    _inherit = "account.move"


# Override function of Odoo, when pressing draft button in invoice view
    def button_draft(self):
        AccountMoveLine = self.env['account.move.line']
        excluded_move_ids = []

        if self._context.get('suspense_moves_mode'):
            excluded_move_ids = AccountMoveLine.search(AccountMoveLine._get_suspense_moves_domain() + [('move_id', 'in', self.ids)]).mapped('move_id').ids
        
        for move in self:
            # Verification if the invoice is allowed to be draft. A error message is sended in the original odoo function
            if not (move in move.line_ids.mapped('full_reconcile_id.exchange_move_id') and move.tax_cash_basis_rec_id and  move.restrict_mode_hash_table and move.state == 'posted' and move.id not in excluded_move_ids):
                move.name = '/'

        return super(account_move, self).button_draft()