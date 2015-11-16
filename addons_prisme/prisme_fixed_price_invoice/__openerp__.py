# -*- coding: utf-8 -*-
{
    'name': "Prisme fixed price invoice",

    'description': 
    """ 
    Set the quantity (hours) to zero in sale journal when "fixed price" is chosen in analytic journal invoicing.

    For more informations:

    - info@prisme.ch
    - http://www.prisme.ch/openerp
    """,

    'author': 'Prisme Solutions Informatique SA',
    'website': 'http://www.prisme.ch',

    'category': 'Tools',
    'version': '8.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],
    
    'installable': True,

}