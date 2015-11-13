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
#
#       'date_planned': fields.related(
#           'production_id', 'date_planned',
#            type='datetime', string='Scheduled Date'),
#
#       'product_qty_final': fields.related(
#            'production_id', 'product_qty',
#            type='float', string='Product Quantity'),
#
#        'product_uom_final': fields.related(
#            'production_id', 'product_uom', relation='product.uom',
#            type='many2one', string='Product Unit of Measure'),
##########################################################################

from openerp.osv import osv, fields


class MRPProductionProductLine(osv.Model):
	_inherit = "mrp.production.product.line"
	_columns = {
		'product_final_id': fields.related('production_id', 'product_id', relation='product.product', type='many2one', string='Product'),	
		'date_planned': fields.related('production_id', 'date_planned', type='datetime', string='Scheduled Date'),
		'product_qty_final': fields.related('production_id', 'product_qty', type='float', string='Product Quantity'),
		'product_uom_final': fields.related('production_id', 'product_uom', relation='product.uom', type='many2one', string='Product Unit of Measure'),
	}