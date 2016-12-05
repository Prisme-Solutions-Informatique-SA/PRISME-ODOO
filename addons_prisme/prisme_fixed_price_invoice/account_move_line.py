# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class AccountMoveLine(osv.osv):

    _inherit = 'account.move.line'
    
    """ Redefined _prepare_analytic_line method to set the quantity(hours) to zero in sale journal when "fixed price" is chosen in analytic journal invoicing and the line amount is 0.0"""
    def _prepare_analytic_line(self, cr, uid, obj_line, context=None):

        quantity = obj_line.quantity
        amount = (obj_line.credit or  0.0) - (obj_line.debit or 0.0)
        if(obj_line.analytic_account_id.fix_price_invoices and amount == 0.0):
            quantity = 0.0
        
        return {'name': obj_line.name,
                'date': obj_line.date,
                'account_id': obj_line.analytic_account_id.id,
                'unit_amount': quantity,
                'product_id': obj_line.product_id and obj_line.product_id.id or False,
                'product_uom_id': obj_line.product_uom_id and obj_line.product_uom_id.id or False,
                'amount': amount,
                'general_account_id': obj_line.account_id.id,
                'journal_id': obj_line.journal_id.analytic_journal_id.id,
                'ref': obj_line.ref,
                'move_id': obj_line.id,
                'user_id': uid,
               }
               
AccountMoveLine()