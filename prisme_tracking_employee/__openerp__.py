{
'name': 'Prisme stock tracking employee',
'version': '7.0',
'category': 'Human Resources',
'description': """
Prisme Solutions Informatique SA specific developments

Add features to stock management:
    * Add 
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'product',
        'stock',
	'purchase',
        ],
'init_xml': [],
    'update_xml': [
 	'view_stock_production_lot.xml',
	'view_stock_move.xml',
	'view_stock_picking.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
