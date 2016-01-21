# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 ONESTEiN BV (<http://www.onestein.nl>).
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

{
    'name': 'Prisme account_cost_center enhancement',
    'summary': """improve account_cost_center to add cost center for Entries Analysis""",
    'description': """
Costcenter
================================================================
This module adds possibility to group and filter by cost center in Entries Analysis
    """,
    'depends': [
        'account',
        'account_accountant',
        'account_cost_center',
    ],
    'author': "ONESTEiN BV",
    'website': 'http://www.onestein.eu',
    'category': 'Accounting',
    'version': '1.1',
    'data': [
        'account_entries_report_prisme.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
