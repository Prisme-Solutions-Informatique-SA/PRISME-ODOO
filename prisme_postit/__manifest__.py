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
#    Project ID:    OERP-009-01 - T527
#
#    Modifications:
#
##########################################################################

{
    'name': 'Prisme postit',
    'version': '2019-09-20 15:15',
    'category': 'Tools',
    'summary': "task manager, reminder",
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'summary': 'tasks and reminders manager',
    'sequence': 9,
    'depends': [
        'mail',
    ],
    'data': [
        'views/postit_view.xml',
        'views/init_scheduler.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [

    ],
    'test': [
    ],
     'css': [
        'static/src/css/note.css',
     ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['images/icon.png','images/banner.png'],
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: