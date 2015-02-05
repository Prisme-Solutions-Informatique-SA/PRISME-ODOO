{
'name': 'Prisme Stock flow',
'version': '6.1',
'category': 'Warehouse',
'description': """
Add the possibility to modify stock flows. Flows modified are:

- Picking and issue of manufacturing orders components.
- Production entry and storing of manufacturing orders finished products
- Picking and delivery of sale order

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'base',
            'purchase',
            'product',
            'mrp',
            'sale',
            'stock',
            ],
'init_xml': [],
'update_xml': [
               'warehouse.xml',
               'product_product_view.xml',
               ],
'demo_xml': [],
'installable': True,
'active': False,
'images': [
           'images/warehouse.jpg',
           'images/product.jpg',
           ],
}
