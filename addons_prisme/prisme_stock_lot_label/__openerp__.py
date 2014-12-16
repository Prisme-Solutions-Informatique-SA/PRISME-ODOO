{
'name': 'Prisme Solutions Informatique SA - stock lot label',
'version': '7.0',
'category': 'Human Resources',
'description': """
CPLG SA specific developments

Add features to stock management:
    * Add label size to product
    * Add no lot to stock production lot
    * Add no lot supplier to stock production lot
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'product',
        'stock',
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
