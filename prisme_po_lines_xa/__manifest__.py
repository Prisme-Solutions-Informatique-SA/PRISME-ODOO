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
{
    "name": "Prisme PO Lines",
    "version": "2020-04-30 14:45",
    "author": "Prisme Solutions Informatique SA",
    "category": "Generic Modules/Accounting",
    "summary": "purchase orders lines list",
    "website": "https://www.prisme.ch",
    "depends": [
		"purchase",
        "sale_stock",
        "account",
    ],
    "demo": [],
    "data": [
        "view/view_po_lines.xml"
    ],
    'images':[
        'static/images/main_screenshot.png',
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False,
    'price': 30,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
