{
'name': 'Prisme Shortage',
'version': '2016-05-17 10:45',
'category': 'Warehouse',
'summary': 'products shortage',
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
