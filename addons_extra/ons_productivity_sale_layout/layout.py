# -*- coding: utf-8 -*-
#
#  File: layout.py
#  Module: ons_productivity_sale_layout
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2013 Open-Net Ltd. All rights reserved.
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

LAYOUTS_LIST = [
    ('article', 'Product'),
    ('title', 'Title'),
    ('text', 'Note'),
    ('subtotal', 'Sub Total'),
    ('line', 'Separator Line'),
    ('break', 'Page Break'),
]

def layout_val_2_text(layout_type):
    val = _( 'Product' )
    if layout_type == 'title':
        val = _( 'Title' )
    elif layout_type == 'text':
        val = _( 'Note' )
    elif layout_type == 'subtotal':
        val = _( 'Sub Total' )
    elif layout_type == 'line':
        val = _( 'Separator Line' )
    elif layout_type == 'break':
        val = _( 'Page Break' )

    return val

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    # ------------------------- Fields management
    
    def _sub_total(self, cr, uid, sol_ids, name, arg, context=None):
        res = {}
        for sol in self.browse(cr, uid, sol_ids, context=context):

            sub_total = 0.0
            if sol.layout_type == 'subtotal':
                sub_sol_ids = self.search(cr, uid, [('order_id','=',sol.order_id.id),('sequence','<=',sol.sequence),('id','!=',sol.id)], context=context, order='sequence desc,id desc')
                for sub_sol in self.browse(cr, uid, sub_sol_ids, context=context):
                    if sub_sol.layout_type == 'subtotal': break
                    if sub_sol.sequence == sol.sequence and sub_sol.id > sol.id: break
                    if sub_sol.layout_type == 'article':
                        sub_total += sub_sol.price_subtotal
            
            res[sol.id] = sub_total
        return res

    _columns = {
        'layout_type':fields.selection(LAYOUTS_LIST, 'Layout type', required=True, select=True),
        'rel_subtotal': fields.function(_sub_total, string='Rel. Sub-total', digits_compute= dp.get_precision('Account')),
    }
    
    _defaults = {
        'layout_type': lambda *a: 'article',
    }

    # ------------------------- Instance management
    
    def create(self, cr, uid, vals, context={}):
        layout_type = vals.get('layout_type', 'article')
        if not vals.get('name'):
            vals['name'] = layout_val_2_text(layout_type)
        
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

    # ------------------------- Interface related
    
    def layout_type_change(self, cr, uid, ids, layout_type):
        if layout_type == 'article':
            return { 'value':{} }

        vals = {
            'name': '',
            'product_id': False,
            'uos_id': False,
            'account_id': False,
            'price_unit': 0.0,
            'price_subtotal': 0.0,
            'quantity': 0,
            'discount': 0.0,
            'invoice_line_tax_id': False,
            'account_analytic_id': False,
            'product_uom_qty': 0.0,
        }
        vals['name'] = layout_val_2_text(layout_type)
        
        cr.execute("Select id from product_uom where name ilike 'unit%%' or name ilike '%%pce%%'")
        row = cr.fetchone()
        if row and row[0]:
            vals.update({
                'product_uom': row[0],
                'product_uos': row[0],
            })
        
        return { 'value': vals }

    # ------------------------- Utilities

    def invoice_line_create(self, cr, uid, ids, context=None):
        ret = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context=context)
        invl_obj = self.pool.get('account.invoice.line')

        for sol in self.browse(cr, uid, ids, context=context):
            invl_ids = [x.id for x in sol.invoice_lines]
            if invl_ids:
                invl_obj.write(cr, uid, invl_ids, {'layout_type': sol.layout_type}, context=context)
        
        return ret

sale_order_line()

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    # ------------------------- Fields management
    
    def _sub_total(self, cr, uid, inv_ids, name, arg, context=None):
        res = {}
        for invl in self.browse(cr, uid, inv_ids, context=context):

            sub_total = 0.0
            if invl.layout_type == 'subtotal':
                sub_invl_ids = self.search(cr, uid, [('invoice_id','=',invl.invoice_id.id),('sequence','<=',invl.sequence),('id','!=',invl.id)], context=context, order='sequence desc,id desc')
                for sub_invl in self.browse(cr, uid, sub_invl_ids, context=context):
                    if sub_invl.layout_type == 'subtotal': break
                    if sub_invl.sequence == invl.sequence and sub_invl.id > invl.id: break
                    if sub_invl.layout_type == 'article':
                        sub_total += sub_invl.price_subtotal
            
            res[invl.id] = sub_total
        return res

    _columns = {
        'layout_type':fields.selection(LAYOUTS_LIST, 'Layout type', required=True, select=True),
        'rel_subtotal': fields.function(_sub_total, string='Rel. Sub-total', digits_compute= dp.get_precision('Account')),
    }
    
    _defaults = {
        'layout_type': lambda *a: 'article',
    }

    _order = 'invoice_id desc, sequence, id'

    # ------------------------- Instance management
    
    def create(self, cr, uid, vals, context={}):
        layout_type = vals.get('layout_type', 'article')
        if not vals.get('name'):
            vals['name'] = layout_val_2_text(layout_type)
        
        return super(account_invoice_line, self).create(cr, uid, vals, context=context)

    # ------------------------- Interface related

    def layout_type_change(self, cr, uid, ids, layout_type):
        if layout_type == 'article':
            return { 'value':{} }

        vals = {
            'name': '',
            'product_id': False,
            'quantity': 1,
            'discount': 0.0,
            'invoice_line_tax_id': [(6,0,[])],
        }
        vals['name'] = layout_val_2_text(layout_type)
        
        return { 'value': vals }

account_invoice_line()
