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
#    Project ID:    OERP-002-08
#    Phabricator:   T499
#
##########################################################################
{
    'name': 'Swiss QR-bill',
    'version': '2020-04-17 15:00',
    'category': 'Accounting',
    'summary': """QR-bill for payment slips in Switzerland""",
    'description'  : """
Adds a QR-bill to invoices.
""",
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'depends': [
        'account',
        'l10n_ch_payment_slip'
    ],
    'external_dependencies' : {
        'python' : [
            'png', # png is the import of pypng
            'pyqrcode'
        ]
    },
    'data': [
        'views/report_invoice.xml',
        'views/account_invoice.xml',
        'views/reports.xml'
    ],
    'images':['static/images/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 100,
    'currency': 'EUR',
    'license': 'OPL-1',
}
