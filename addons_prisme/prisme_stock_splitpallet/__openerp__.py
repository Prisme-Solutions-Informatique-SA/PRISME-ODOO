{
'name': 'Prisme Solutions Informatique SA - stock enhancement - split pallet',
'version': '7.0',
'category': 'Human Resources',
'description': """
Prisme Solution Informatique SA specific developments

Add features to stock management:
    * Add palette quantity to product
    * Split reception line by pallet (rest of split is in the last pallet)
    * Auto create S/N by pallet
    
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
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
