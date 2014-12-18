{
'name': 'Prisme po Enhancement',
'version': '7.0',
'category': 'Purchase order',
'description': """
Add features to purchase order

- display origin when created manually


For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'sequence': 150,
'website': 'http://www.prisme.ch',
'depends': [
            'purchase',
],
'init_xml': [],
'update_xml': [
                'purchase_order_view.xml',

],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           ],
}