# -*- coding: utf-8 -*-
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

{
    'name': 'prisme_postit',
    'version': '1.0',
    'category': 'Tools',
    'description': """
This module allows users to create their own postit inside OpenERP
=================================================================


""",
    'author': 'Prisme Solutions informatique SA',
    'website': 'http://openerp.com',
    'summary': 'Sticky notes, Collaborative, Memos',
    'sequence': 9,
    'depends': [
        'mail',
    ],
    'data': [
      #  'security/note_security.xml',
      #  'security/ir.rule.xml',
      #  'security/ir.model.access.csv',
        'postit_view.xml',
        'postit_workflow.xml',

    ],
    'demo': [

    ],
    'test': [
    ],
    'init_xml': [
    'init_scheduler.xml',

    ],
    'css': [
      #  'static/src/css/note.css',
    ],
    'images': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
