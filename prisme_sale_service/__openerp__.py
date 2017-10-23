{
'name': 'Prisme sale_service extension',
'version': '7.0',
'category': 'Human Resources',
'description': """


Add features to sale_service module:
    * Add task stage_id on product (used to create task)
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'product',
        'stock',
	'sale_service',
        ],
'init_xml': [],
    'update_xml': [
        'view_product_product.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
