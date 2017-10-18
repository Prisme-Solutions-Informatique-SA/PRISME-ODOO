# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Additional Report Attachments",
    'version': '1.0',
    'category': 'Discuss',
    'sequence': 26,
    'summary': """Additional Report Attachments""",
    'description': """        
Additional Report Attachments
=============================
Allow user to add an additional attachments on mail template 
    """,
    'author' : 'Synconics Technologies Pvt. Ltd',
    'website': 'http://www.synconics.com',
    'depends': [
        'mail'
    ],
    'data': [
         'security/ir.model.access.csv',
         'views/mail_template_views.xml'
    ],
    'demo': [
    ],    
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: