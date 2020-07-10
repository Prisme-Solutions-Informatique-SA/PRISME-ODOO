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
{
'name': 'Prisme Lots Enhancement',
'version': '2020-03-03 15:00',
'category': 'Warehouse',
'summary': 'warranties, extra fields',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
    'stock',
    'account',
 ],
'data': [
    'data/init_scheduler.xml',
    'views/view_stock_production_lot.xml',
    'views/view_prisme_warranty_warranty.xml',
    'views/view_prisme_warranty_type.xml',
    'views/view_move_line_form.xml',
    'security/ir.model.access.csv',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': ['images/icon.png','images/banner.png'],
    'license': 'LGPL-3',
}