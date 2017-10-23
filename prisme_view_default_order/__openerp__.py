{
'name': 'Prisme view default order',
'version': '7.0',
'category': 'Human Resources',
'description': """
CPLG SA specific developments

Add filter to computed field:
    
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
        'view_product_product.xml',
 	'view_stock_production_lot.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
