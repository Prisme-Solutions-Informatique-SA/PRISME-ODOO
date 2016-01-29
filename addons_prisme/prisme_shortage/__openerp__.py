{
'name': 'Prisme Shortage',
'version': '6.1',
'category': 'Warehouse',
'description': """
Computes and shows a list of shortage products.

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': ['base', 'account', 'sale', 'stock', ],
'init_xml': [],
'update_xml': [
    'security/ir.model.access.csv',
    'sql_data.xml',
    'shortage_view.xml',
],
'demo_xml': [],
'installable': True,
'active': False,
'images': [
           'images/shortage.jpg',
           ],
}
